"""Malayalam audio lessons, written and voiced by Gemini.

Two steps, so the text can be read and corrected before it is voiced:

    python3 tools/make_lesson.py write exams/ccao-f.html d1
        Gemini writes a beginner lesson for that domain from the page's own
        notes (the facts the "Learn in Malayalam with Gemini" button sends,
        plus the rest of the domain's notes) and puts it in the page as
        a read-along transcript.

    python3 tools/make_lesson.py speak exams/ccao-f.html d1
        A Gemini voice reads the transcript, one paragraph at a time. The
        paragraphs are joined with short pauses into assets/audio/<id>.mp3,
        and each paragraph's start time is written back into the page, so
        the player highlights it and tapping it jumps there.

    python3 tools/make_lesson.py models
        Lists the Gemini models your key can use.

Needs Python 3.10+, beautifulsoup4, ffmpeg and a Gemini API key from
https://aistudio.google.com/apikey in GEMINI_API_KEY. (In the cloud
environment the network proxy adds the key to each request, so the variable
can be left unset there.)

Voiced paragraphs are cached in .audio-cache/, so after an edit only the
changed paragraphs are voiced again, and a run stopped by a quota limit
carries on where it left off.
"""
import argparse
import base64
import hashlib
import html
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave

from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".audio-cache"
API = "https://generativelanguage.googleapis.com/v1beta"
TEXT_MODEL = os.environ.get("GEMINI_TEXT_MODEL", "gemini-3.8-flash")
TTS_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
VOICE = os.environ.get("GEMINI_VOICE", "Sulafat")   # described by Google as "warm"
STYLE = ("Read this aloud in Malayalam like a warm, friendly teacher talking to one student: "
         "natural, calm, clear and unhurried.")
GAP_PARAGRAPH = 0.6   # seconds of silence between paragraphs
GAP_SECTION = 1.2     # ... before a new section

BLOCK = re.compile(r"(<!-- audio-note:(?P<id>[\w-]+) -->\n)(?P<body>.*?)(<!-- /audio-note:(?P=id) -->\n)", re.S)
ITEM = re.compile(r'<(?P<tag>h4|p)(?P<attrs>[^>]*)>(?P<inner>.*?)</(?P=tag)>', re.S)


# ---------------------------------------------------------------- Gemini API
def call(model, body, timeout=600):
    """POST generateContent, retrying on rate limits and server errors."""
    req_body = json.dumps(body).encode()
    for attempt in range(8):
        req = urllib.request.Request(
            f"{API}/models/{model}:generateContent", data=req_body, method="POST",
            headers={"Content-Type": "application/json",
                     "x-goog-api-key": os.environ.get("GEMINI_API_KEY", "added-by-proxy")})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < 7:
                wait = 20 * (attempt + 1)
                m = re.search(r'"retryDelay":\s*"(\d+)', detail)
                if m:
                    wait = int(m.group(1)) + 2
                if e.code == 429 and "limit: 0" in detail:
                    raise SystemExit(f"{model} isn't available on this key's plan (its free-tier limit is 0). "
                                     "Pick another model with GEMINI_TEXT_MODEL or GEMINI_TTS_MODEL.")
                if e.code == 429 and "PerDay" in detail:
                    raise SystemExit(f"Daily quota used up for {model}. Run again tomorrow; finished parts are cached.\n{detail[:600]}")
                print(f"    {e.code}, waiting {wait}s and retrying", flush=True)
                time.sleep(wait)
                continue
            raise SystemExit(f"Gemini API error {e.code} for {model}:\n{detail[:1500]}")
    raise SystemExit("Gave up after repeated errors.")


def list_models():
    req = urllib.request.Request(f"{API}/models?pageSize=200",
                                 headers={"x-goog-api-key": os.environ.get("GEMINI_API_KEY", "added-by-proxy")})
    try:
        r = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Gemini API error {e.code}:\n{e.read().decode(errors='replace')[:800]}")
    with r:
        for m in json.load(r).get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(m["name"].removeprefix("models/"))


# ---------------------------------------------------------------- page facts
def clean(el):
    el = BeautifulSoup(str(el), "html.parser")
    for x in el.select(".label, svg"):
        x.decompose()
    return re.sub(r"\s+", " ", el.get_text()).strip()


def domain_facts(page_html, sec_id):
    soup = BeautifulSoup(page_html, "html.parser")
    for x in soup.select(".audio-note"):
        x.decompose()
    sec = soup.select_one(f"section.domain#{sec_id}")
    if not sec:
        raise SystemExit(f"No <section class=\"domain\" id=\"{sec_id}\"> in the page.")
    weight = sec.select_one(".weight")
    info = {
        "code": soup.select_one(".hero .exam-code").get_text(strip=True),
        "exam": soup.select_one(".hero h1").get_text(strip=True),
        "num": sec.select_one(".domain-num").get_text(strip=True).removeprefix("D"),
        "title": sec.select_one(".domain-head h2").get_text(strip=True),
        "weight": weight.contents[0].strip() if weight else "",
        "topics": [re.sub(r"^(\d+\.\d+)\s*", r"\1 ", clean(h)) for h in sec.select("h3.sub")],
    }
    info["notes"] = notes_text(sec)
    return info


def notes_text(sec):
    """The domain's notes as plain text: headings, cards, steps, table rows,
    lists, callouts, flashcards, practice questions and diagram captions."""
    sec = BeautifulSoup(str(sec), "html.parser")
    for x in sec.select("svg, .domain-head"):
        x.decompose()
    for h in sec.select("h3.sub"):
        h.insert_before("\n## ")
    for c in sec.select(".callout .label"):
        c.insert_after(": ")
    for st in sec.select(".flow .step"):
        st.insert_before("Step: ")
        if st.b:
            st.b.insert_after(": ")
    for q in sec.select("details.qa:not(.code-toggle)"):
        q.summary.insert_before("Q: ")
        q.summary.insert_after(" A: ")
    for f in sec.select("figcaption"):
        f.insert_before("Diagram: ")
    for q in sec.select(".quiz .q"):
        q.insert_before("Practice question: ")
    for li in sec.select("li"):
        li.insert_before("- ")
    for cell in sec.select("td, th"):
        cell.insert_after(" | ")
    for tag in sec.select("p, li, h3, h4, tr, figcaption, dt, dd, .step, .card, .callout, details.qa, .q, .why, .chips"):
        tag.insert_after("\n")
    lines = (re.sub(r"\s+", " ", ln).strip(" |") for ln in sec.get_text("").split("\n"))
    return "\n".join(ln for ln in lines if ln.strip())


LESSON_PROMPT = """You are a friendly teacher from Kerala. Write a spoken Malayalam lesson that teaches a complete beginner Domain {num}: {title}{weight_part} of the "{exam}" ({code}) certification exam. It will be turned into audio for a study website, with the text shown for reading along.

How to write it:
- Teach the whole domain from start to finish: every topic and every important point in the notes below, in order.
- Warm, flowing, spoken Malayalam, as if you are talking to me. Simple everyday words.
- Keep English technical terms (prompt, context window, API and so on) in English letters, and explain each one in Malayalam the first time.
- No markdown, bullet points, emoji or symbols. Write numbers and percentages as Malayalam words.
- Give a small everyday example for each main idea, and clearly warn me about each exam trap in the notes.
- Do not ask me questions. Start with a short welcome that says what this domain covers. End with a three-point recap and one line encouraging me to try the practice questions on the page.
- Sections, in order: the welcome, one section per topic below, one on the exam traps, and the recap. Give each a short Malayalam heading; a topic's heading starts with its number, like "1.1".
- Each paragraph has two to four sentences, because the website highlights one paragraph at a time while it plays.
- Length: about eight to ten minutes when read aloud at a calm pace.
- Teach only from the notes below. Don't read out the practice questions; teach the ideas behind them.

Topics:
{topics}

Notes for this domain:
{notes}"""

LESSON_SCHEMA = {
    "type": "OBJECT",
    "properties": {"sections": {"type": "ARRAY", "items": {
        "type": "OBJECT",
        "properties": {"heading": {"type": "STRING"}, "paragraphs": {"type": "ARRAY", "items": {"type": "STRING"}}},
        "required": ["heading", "paragraphs"]}}},
    "required": ["sections"],
}


def block_html(nid, info, sections, sub):
    title = f"{info['code']} · Domain {info['num']} · {info['title']}"
    out = [f'<!-- audio-note:{nid} -->',
           f'          <div class="audio-note" data-audio="" data-title="{html.escape(title)}">',
           '            <div class="an-head">',
           '              <span class="an-icon" aria-hidden="true">🎧</span>',
           '              <div>',
           '                <span class="an-title" lang="ml">മലയാളത്തിൽ കേൾക്കാം</span>',
           f'                <span class="an-sub">{html.escape(sub)}</span>',
           '              </div>',
           '            </div>',
           '            <div class="an-player"></div>',
           '            <details class="an-script">',
           '              <summary>Read along · tap a paragraph to play from there</summary>',
           '              <div class="an-text" lang="ml">']
    for s in sections:
        out.append(f'                <h4>{html.escape(s["heading"].strip())}</h4>')
        for p in s["paragraphs"]:
            if p.strip():
                out.append(f'                <p data-say>{html.escape(re.sub(r"\s+", " ", p).strip())}</p>')
    out += ['              </div>', '            </details>', '          </div>',
            f'<!-- /audio-note:{nid} -->', '']
    return "\n".join(out)


def write(page, sec_id):
    path = ROOT / page
    src = path.read_text()
    info = domain_facts(src, sec_id)
    prompt = LESSON_PROMPT.format(
        **{k: v for k, v in info.items() if k != "topics"}, weight_part=f" ({info['weight']} of the exam)" if info["weight"] else "",
        topics="\n".join("- " + t for t in info["topics"]))
    print(f"Asking {TEXT_MODEL} to write the lesson…", flush=True)
    res = call(TEXT_MODEL, {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "responseSchema": LESSON_SCHEMA},
    })
    text = "".join(p.get("text", "") for p in res["candidates"][0]["content"]["parts"])
    sections = json.loads(text)["sections"]
    nid = f"{info['code'].lower()}-{sec_id}"
    block = block_html(nid, info, sections, f"Domain {info['num']} as a beginner lesson · audio not made yet")
    m = BLOCK.search(src)
    if m and m.group("id") == nid:
        src = src[:m.start()] + block + src[m.end():]
    else:
        start = src.index(f'<section class="domain" id="{sec_id}">')
        head_end = src.index("</div>\n", src.index('<div class="domain-head">', start)) + len("</div>\n")
        src = src[:head_end] + "\n" + block + src[head_end:]
    path.write_text(src)
    n = sum(len(s["paragraphs"]) for s in sections)
    words = sum(len(p.split()) for s in sections for p in s["paragraphs"])
    print(f"Wrote {len(sections)} sections, {n} paragraphs, {words} words into {page} ({nid}).")


# ---------------------------------------------------------------- voice
def tts(text):
    """Voice one paragraph; returns (pcm bytes, sample rate). Cached on disk."""
    key = hashlib.sha256(json.dumps([TTS_MODEL, VOICE, STYLE, text]).encode()).hexdigest()[:24]
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{key}.pcm"
    if f.exists():
        rate, pcm = f.read_bytes().split(b"\n", 1)
        return pcm, int(rate)
    res = call(TTS_MODEL, {
        "contents": [{"parts": [{"text": f"{STYLE}\n\n{text}"}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}},
    })
    parts = res["candidates"][0]["content"]["parts"]
    data = next(p["inlineData"] for p in parts if "inlineData" in p)
    raw = base64.b64decode(data["data"])
    if raw[:4] == b"RIFF":   # newer models send a WAV file
        with wave.open(io.BytesIO(raw)) as w:
            if w.getnchannels() != 1 or w.getsampwidth() != 2:
                raise SystemExit(f"Unexpected audio format from {TTS_MODEL}: {w.getparams()}")
            rate, pcm = w.getframerate(), w.readframes(w.getnframes())
    else:                    # older ones send raw 16-bit PCM: audio/L16;codec=pcm;rate=24000
        rate, pcm = int(re.search(r"rate=(\d+)", data["mimeType"]).group(1)), raw
    f.write_bytes(f"{rate}\n".encode() + pcm)
    return pcm, rate


def speak(page, sec_id):
    path = ROOT / page
    src = path.read_text()
    m = next((m for m in BLOCK.finditer(src) if m.group("id").endswith(f"-{sec_id}")), None)
    if not m:
        raise SystemExit(f"No audio-note block for {sec_id} in {page}. Run 'write' first.")
    nid, body = m.group("id"), m.group("body")
    items = list(ITEM.finditer(body))
    pcm_all, starts, t, rate, new_section = [], [], 0.0, None, False
    paras = [i for i in items if i.group("tag") == "p" and "data-say" in i.group("attrs")]
    done = 0
    for it in items:
        if it.group("tag") == "h4":
            new_section = True
            continue
        if "data-say" not in it.group("attrs"):
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", it.group("inner"))).strip()
        pcm, rate = tts(text)
        if starts:
            gap = GAP_SECTION if new_section else GAP_PARAGRAPH
            pcm_all.append(b"\0\0" * int(gap * rate))
            t += gap
        new_section = False
        starts.append(round(t, 1))
        pcm_all.append(pcm)
        secs = len(pcm) / 2 / rate
        t += secs
        done += 1
        pace = len(text) / max(secs, 0.1)
        flag = "  <- check: unusual pace" if not 6 <= pace <= 22 else ""
        print(f"  {done}/{len(paras)}  {secs:5.1f}s  {pace:4.1f} chars/s{flag}", flush=True)

    out = ROOT / "assets" / "audio" / f"{nid}.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "-",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "24000", "-codec:a", "libmp3lame", "-b:a", "48k", str(out)],
                   input=b"".join(pcm_all), check=True)
    minutes = max(1, round(t / 60))
    print(f"Wrote {out.relative_to(ROOT)}: {t / 60:.1f} min, {out.stat().st_size / 1e6:.1f} MB")

    rel = os.path.relpath(out, path.parent)
    it = iter(starts)
    body = re.sub(r'data-audio="[^"]*"', f'data-audio="{rel}"', body, count=1)
    body = re.sub(r'<p data-say(?: data-t="[^"]*")?>', lambda _: f'<p data-say data-t="{next(it)}">', body)
    body = re.sub(r'<span class="an-sub">[^<]*</span>',
                  f'<span class="an-sub">Domain {sec_id.removeprefix("d")} as a beginner lesson · {minutes} min · '
                  f'Gemini voice “{VOICE}”</span>', body, count=1)
    path.write_text(src[:m.start()] + m.group(1) + body + m.group(4) + src[m.end():])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=["write", "speak", "models"])
    ap.add_argument("page", nargs="?", default="exams/ccao-f.html")
    ap.add_argument("domain", nargs="?", default="d1", help="section id, e.g. d1")
    a = ap.parse_args()
    {"write": lambda: write(a.page, a.domain), "speak": lambda: speak(a.page, a.domain), "models": list_models}[a.step]()
