"""Generate the Malayalam audio-note MP3s from the transcripts in the pages.

One-off setup (not needed to serve the site):

    python3 -m venv .ttsenv
    .ttsenv/bin/pip install torch transformers scipy lameenc

Run:

    .ttsenv/bin/python tools/make_audio.py exams/ccao-f.html

For every block between <!-- audio-note:ID --> and <!-- /audio-note:ID --> in the
page, this reads the [data-say] headings and paragraphs (without the small
English glosses in .en spans), speaks them one sentence at a time with Meta's
MMS Malayalam voice (facebook/mms-tts-mal), joins them with short pauses and
writes assets/audio/ID.mp3. It then writes data-audio and per-paragraph start
times (data-t, in seconds) back into the page, so the player highlights the
paragraph being read and tapping a paragraph jumps to it.

The voice model is licensed CC BY-NC 4.0: fine for this free, non-commercial
study site, not for commercial use.
"""
import html
import os
import pathlib
import re
import sys

import numpy as np
import torch
import lameenc
from transformers import AutoTokenizer, VitsModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "facebook/mms-tts-mal"
RATE = 0.9          # a little slower than default, for beginners
GAP_COMMA = 0.18     # seconds of silence at a comma (the voice ignores punctuation)
GAP_SENTENCE = 0.35  # ... between sentences
GAP_PARAGRAPH = 0.8  # ... between paragraphs
GAP_HEADING = 1.1    # ... before a section heading

LOG = []  # (clause, seconds), for checking the speaking pace
BLOCK = re.compile(r"(<!-- audio-note:(?P<id>[\w-]+) -->)(?P<body>.*?)(<!-- /audio-note:(?P=id) -->)", re.S)
SAY = re.compile(r'<(?P<tag>h4|p) data-say(?: data-t="[^"]*")?>(?P<inner>.*?)</(?P=tag)>', re.S)
EN = re.compile(r'<span class="en"[^>]*>.*?</span>', re.S)


def spoken(inner):
    text = html.unescape(re.sub(r"<[^>]+>", "", EN.sub("", inner)))
    return re.sub(r"\s+", " ", text).strip()


def merge_short(pieces, min_len=12):
    """Keep very short pieces (like "മൂന്ന്:") attached to the next one:
    a lone word sounds clipped."""
    out, carry = [], ""
    for p in (p for p in pieces if p.strip()):
        p = (carry + " " + p).strip() if carry else p
        if len(p) < min_len:
            carry = p
        else:
            out.append(p)
            carry = ""
    if carry:
        if out:
            out[-1] += " " + carry
        else:
            out.append(carry)
    return out


def sentences(text):
    return merge_short(re.split(r"(?<=[.!?:;])\s+", text))


def clauses(sentence):
    """Split at commas so the voice pauses there (it ignores punctuation)."""
    return merge_short(re.split(r"(?<=,)\s+", sentence))


def synthesise(model, tok, text):
    torch.manual_seed(0)  # VITS samples noise; a fixed seed keeps rebuilds identical
    inputs = tok(text, return_tensors="pt")
    with torch.no_grad():
        return model(**inputs).waveform[0].numpy()


def build(page):
    path = ROOT / page
    src = path.read_text()
    tok = AutoTokenizer.from_pretrained(MODEL)
    if getattr(tok, "is_uroman", False):
        raise SystemExit("This model needs uroman romanisation; not supported by this script.")
    model = VitsModel.from_pretrained(MODEL)
    model.config.speaking_rate = RATE
    sr = model.config.sampling_rate

    def one_block(m):
        nid, body = m.group("id"), m.group("body")
        parts = list(SAY.finditer(body))
        chunks, starts, t = [], [], 0.0
        for i, p in enumerate(parts):
            if i:
                gap = GAP_HEADING if p.group("tag") == "h4" else GAP_PARAGRAPH
                chunks.append(np.zeros(int(gap * sr), dtype=np.float32))
                t += gap
            starts.append(round(t, 1))
            for j, s in enumerate(sentences(spoken(p.group("inner")))):
                if j:
                    chunks.append(np.zeros(int(GAP_SENTENCE * sr), dtype=np.float32))
                    t += GAP_SENTENCE
                for k, clause in enumerate(clauses(s)):
                    if k:
                        chunks.append(np.zeros(int(GAP_COMMA * sr), dtype=np.float32))
                        t += GAP_COMMA
                    wav = synthesise(model, tok, clause)
                    chunks.append(wav)
                    t += len(wav) / sr
                    LOG.append((clause, len(wav) / sr))
            print(f"  {nid}: {i + 1}/{len(parts)} paragraphs, {t:5.1f}s", flush=True)
        audio = np.concatenate(chunks)
        audio = audio / max(1e-6, float(np.abs(audio).max())) * 0.9
        pcm = (audio * 32767).astype(np.int16).tobytes()
        enc = lameenc.Encoder()
        enc.set_bit_rate(48)
        enc.set_in_sample_rate(sr)
        enc.set_channels(1)
        enc.set_quality(2)
        mp3 = enc.encode(pcm) + enc.flush()
        out = ROOT / "assets" / "audio" / f"{nid}.mp3"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(mp3)
        print(f"  wrote {out.relative_to(ROOT)}: {len(audio) / sr:.0f}s, {len(mp3) / 1e6:.2f} MB")

        rel = os.path.relpath(out, path.parent)
        body = re.sub(r'class="audio-note" data-audio="[^"]*"', f'class="audio-note" data-audio="{rel}"', body, count=1)
        it = iter(starts)
        body = SAY.sub(lambda s: f'<{s.group("tag")} data-say data-t="{next(it)}">{s.group("inner")}</{s.group("tag")}>', body)
        return m.group(1) + body + m.group(4)

    out, n = BLOCK.subn(one_block, src)
    if not n:
        raise SystemExit(f"No audio-note blocks in {page}")
    path.write_text(out)


if __name__ == "__main__":
    for page in sys.argv[1:] or ["exams/ccao-f.html"]:
        print(page)
        build(page)
