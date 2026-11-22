/* Claude Exam Visual Notes — small, dependency-free behaviours.
   1. Theme toggle   2. Table of contents (sidebar, or a bar on phones)
   3. Section search 4. "Done" progress tracking (localStorage)
   5. Phone-friendly tables and diagrams   6. Malayalam audio lessons
   7. Practise with Gemini   8. Practice quizzes                   */
(() => {
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  };

  /* 1. Theme ------------------------------------------------------------ */
  const root = document.documentElement;
  const savedTheme = store.get("theme", null);
  if (savedTheme) root.dataset.theme = savedTheme;
  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    const sync = () => {
      const dark = root.dataset.theme
        ? root.dataset.theme === "dark"
        : matchMedia("(prefers-color-scheme: dark)").matches;
      btn.textContent = dark ? "☀️" : "🌙";
      const meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.content = getComputedStyle(root).getPropertyValue("--bg").trim();
      btn.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
    };
    btn.addEventListener("click", () => {
      const dark = btn.textContent === "☀️";
      root.dataset.theme = dark ? "light" : "dark";
      store.set("theme", root.dataset.theme);
      sync();
    });
    sync();
  });

  const exam = document.body.dataset.exam;
  const domains = [...document.querySelectorAll("section.domain[id]")];

  /* 2. TOC + scroll spy --------------------------------------------------
        Desktop shows it as a sidebar. On phones and tablets (CSS) it is a bar
        stuck to the top of the screen: it names the section you are reading
        and opens the full list. */
  const toc = document.querySelector("[data-toc]");
  const aside = toc?.closest(".toc");
  let tocLinks = [];
  let tocMeta = null;
  if (toc && domains.length) {
    domains.forEach((sec) => {
      const a = document.createElement("a");
      a.href = `#${sec.id}`;
      a.dataset.target = sec.id;
      const num = sec.querySelector(".domain-num")?.textContent.trim();
      if (num) {
        const n = document.createElement("span");
        n.className = "toc-num";
        n.textContent = num;
        a.appendChild(n);
      }
      const label = document.createElement("span");
      label.className = "toc-label";
      label.textContent = sec.querySelector("h2")?.textContent.trim() ?? sec.id;
      a.appendChild(label);
      toc.appendChild(a);
    });
    tocLinks = [...toc.querySelectorAll("a")];

    // Wrap the aside's contents in a panel and add the phone toggle bar.
    const panel = document.createElement("div");
    panel.className = "toc-panel";
    panel.id = "toc-panel";
    panel.append(...aside.childNodes);
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "toc-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", "toc-panel");
    toggle.innerHTML = `<span class="toc-cur"><span class="toc-label">${panel.querySelector(".toc-title")?.textContent ?? "Sections"}</span></span>
      <span class="toc-meta"></span><span class="toc-caret" aria-hidden="true">▼</span>`;
    aside.append(toggle, panel);
    const cur = toggle.querySelector(".toc-cur");
    tocMeta = toggle.querySelector(".toc-meta");
    const setOpen = (open) => {
      aside.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };
    toggle.addEventListener("click", () => setOpen(!aside.classList.contains("open")));
    tocLinks.forEach((a) => a.addEventListener("click", () => setOpen(false)));
    document.addEventListener("click", (e) => { if (!aside.contains(e.target)) setOpen(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });

    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        tocLinks.forEach((l) => {
          const on = l.dataset.target === e.target.id;
          l.classList.toggle("active", on);
          if (on) cur.replaceChildren(...[...l.children].map((c) => c.cloneNode(true)));
        });
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    domains.forEach((s) => io.observe(s));
  }

  /* 3. Search: filters domain sections by text ---------------------------- */
  const search = document.querySelector("[data-search]");
  if (search) {
    search.addEventListener("input", () => {
      const q = search.value.trim().toLowerCase();
      domains.forEach((s) => s.classList.toggle("hidden", q && !s.textContent.toLowerCase().includes(q)));
    });
  }

  /* 4. Progress ------------------------------------------------------------ */
  const progressKey = (e) => `progress:${e}`;
  const renderProgress = () => {
    if (!exam) return;
    const done = store.get(progressKey(exam), []);
    const n = done.filter((id) => domains.some((d) => d.id === id)).length;
    const pct = domains.length ? Math.round((n / domains.length) * 100) : 0;
    tocLinks.forEach((l) => l.classList.toggle("done", done.includes(l.dataset.target)));
    if (tocMeta) tocMeta.textContent = `${n}/${domains.length} done`;
    document.querySelectorAll("[data-progress-self]").forEach((el) => {
      el.querySelector("i").style.width = `${pct}%`;
      const label = el.nextElementSibling;
      if (label?.classList.contains("progress-label")) label.textContent = `${pct}% of sections marked done`;
    });
  };
  if (exam) {
    const done = new Set(store.get(progressKey(exam), []));
    domains.forEach((sec) => {
      const head = sec.querySelector(".domain-head");
      if (!head) return;
      const label = document.createElement("label");
      label.className = "done-toggle";
      label.innerHTML = `<input type="checkbox"> Done`;
      const box = label.querySelector("input");
      box.checked = done.has(sec.id);
      sec.classList.toggle("is-done", box.checked);
      box.addEventListener("change", () => {
        box.checked ? done.add(sec.id) : done.delete(sec.id);
        sec.classList.toggle("is-done", box.checked);
        store.set(progressKey(exam), [...done]);
        renderProgress();
      });
      head.appendChild(label);
    });
    renderProgress();
  }
  // Home page tiles: count sections in each exam page, then show saved progress
  document.querySelectorAll("[data-progress-for]").forEach(async (el) => {
    const id = el.dataset.progressFor;
    const label = el.nextElementSibling;
    try {
      const html = await (await fetch(`exams/${id}.html`)).text();
      const ids = [...new DOMParser().parseFromString(html, "text/html").querySelectorAll("section.domain[id]")].map((s) => s.id);
      const n = store.get(progressKey(id), []).filter((x) => ids.includes(x)).length;
      const pct = ids.length ? Math.round((n / ids.length) * 100) : 0;
      el.querySelector("i").style.width = `${pct}%`;
      if (label) label.textContent = `${n}/${ids.length} sections done`;
    } catch {
      if (label) label.textContent = "";
    }
  });

  /* 5. Phones: tables with three or more columns become one card per row.
         Each cell gets its column name, which the CSS shows as a label. */
  document.querySelectorAll("table.compare").forEach((t) => {
    const heads = [...t.querySelectorAll("thead th")].map((th) => th.textContent.trim());
    if (heads.length < 3) return;
    t.classList.add("stackable");
    t.querySelectorAll("tbody tr").forEach((tr) => {
      [...tr.children].forEach((cell, i) => {
        if (cell.tagName !== "TD") return;
        cell.dataset.label = heads[i] ?? "";
        const value = document.createElement("div");   // keeps mixed text and bold together
        value.className = "cv";
        value.append(...cell.childNodes);
        cell.append(value);
      });
    });
  });

  /*    Diagrams wider than the screen scroll sideways; mark them so only
         those show the swipe hint and edge shadows. */
  const figs = [...document.querySelectorAll("figure.dg")];
  const markScrolling = () => figs.forEach((f) => {
    const box = f.querySelector(".dg-scroll");
    if (box) f.classList.toggle("scrolls", box.scrollWidth > box.clientWidth + 2);
  });
  if (figs.length) {
    markScrolling();
    let t;
    addEventListener("resize", () => { clearTimeout(t); t = setTimeout(markScrolling, 150); });
  }

  /* 6. Malayalam audio lessons: <div class="audio-note" data-audio="file.mp3">
        (made by tools/make_lesson.py). A normal audio player with speed
        buttons; paragraphs with data-t="seconds" highlight as it plays and
        can be tapped to jump there. The phone's lock screen shows the title. */
  document.querySelectorAll(".audio-note").forEach((note) => {
    const slot = note.querySelector(".an-player");
    if (!note.dataset.audio || !slot) return;
    const parts = [...note.querySelectorAll("[data-say]")];
    const times = parts.map((p) => parseFloat(p.dataset.t));
    const audio = document.createElement("audio");
    audio.src = note.dataset.audio;
    audio.preload = "none";   // nothing is downloaded until you press play
    audio.controls = true;
    const speeds = document.createElement("div");
    speeds.className = "an-speed";
    speeds.setAttribute("role", "group");
    speeds.setAttribute("aria-label", "Playback speed");
    let rate = 1;
    [0.8, 1, 1.2, 1.5].forEach((r) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = `${r}×`;
      b.setAttribute("aria-pressed", String(r === rate));
      b.addEventListener("click", () => {
        rate = r;
        audio.playbackRate = r;
        speeds.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      });
      speeds.appendChild(b);
    });
    slot.append(audio, speeds);

    let current = -1;
    audio.addEventListener("timeupdate", () => {
      let i = -1;
      times.forEach((t, j) => { if (!isNaN(t) && t <= audio.currentTime + 0.05) i = j; });
      if (i === current) return;
      current = i;
      parts.forEach((p, j) => p.classList.toggle("speaking", j === i));
    });
    audio.addEventListener("ratechange", () => { rate = audio.playbackRate; });
    audio.addEventListener("play", () => {
      if ("mediaSession" in navigator && window.MediaMetadata) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: note.dataset.title || document.title, artist: "Claude Exam Notes", album: "Malayalam lessons",
        });
      }
    });
    parts.forEach((p, j) => p.addEventListener("click", () => {
      if (isNaN(times[j])) return;
      const go = () => {
        audio.currentTime = times[j];
        audio.playbackRate = rate;
        audio.play();
      };
      // With preload="none" the file isn't loaded yet, and seeking before
      // its metadata arrives is ignored.
      if (audio.readyState >= 1) go();
      else {
        audio.addEventListener("loadedmetadata", go, { once: true });
        audio.load();
      }
    }));
  });

  /* 7. "Practise with Gemini": every exam domain gets a card with two buttons, English and Malayalam
        (technical terms stay in English). Each copies a prompt built from that domain's own notes
        (diagram captions, callouts, flashcards, practice questions) and opens Gemini (the app on
        Android, gemini.google.com elsewhere). Gemini teaches the whole domain first, then runs
        exam-style practice questions one at a time and ends with a score card. */
  const examCode = document.querySelector(".hero .exam-code")?.textContent.trim();
  const examName = document.querySelector(".hero h1")?.textContent.trim();
  const isAndroid = /Android/i.test(navigator.userAgent);
  const GEMINI_WEB = "https://gemini.google.com/app";
  const geminiHref = isAndroid
    ? "intent://gemini.google.com/app#Intent;scheme=https;package=com.google.android.apps.bard;S.browser_fallback_url="
      + encodeURIComponent(GEMINI_WEB) + ";end"
    : GEMINI_WEB;
  const clean = (el) => {
    if (!el) return "";
    const c = el.cloneNode(true);
    c.querySelectorAll(".label, svg").forEach((e) => e.remove());
    return c.textContent.replace(/\s+/g, " ").trim();
  };
  const buildPrompt = (sec, lang) => {
    const ml = lang === "ml";
    const num = sec.querySelector(".domain-num")?.textContent.trim().replace(/^D/, "") ?? "";
    const title = sec.querySelector(".domain-head h2")?.textContent.trim() ?? "";
    const weight = sec.querySelector(".weight")?.firstChild?.textContent.trim() ?? "";
    const topics = [...sec.querySelectorAll("h3.sub")].map((h) => "- " + clean(h).replace(/^(\d+\.\d+)\s*/, "$1 "));
    const facts = [];
    sec.querySelectorAll("figure.dg figcaption").forEach((f) => facts.push("- " + clean(f)));
    sec.querySelectorAll(".callout").forEach((c) => {
      const label = c.querySelector(".label")?.textContent.trim();
      facts.push(`- ${label ? label + ": " : ""}${clean(c)}`);
    });
    sec.querySelectorAll("details.qa:not(.code-toggle)").forEach((d) => {
      facts.push(`- Q: ${clean(d.querySelector("summary"))} A: ${clean(d.querySelector(".a"))}`);
    });
    sec.querySelectorAll(".quiz").forEach((q) => {
      facts.push(`- Practice question: ${clean(q.querySelector(".q"))} ${clean(q.querySelector(".why"))}`);
    });
    const language = ml ? "simple Malayalam" : "clear, simple English";
    return [
      `You are my friendly exam tutor. I am a beginner preparing for the "${examName}" (${examCode}) certification exam. Teach me Domain ${num}: ${title}${weight ? ` (${weight} of the exam)` : ""}, in ${language}.`,
      "",
      "Part 1: the full lesson. Do this first, and ask me no questions yet.",
      "- Teach the whole domain from start to finish: every topic and every key fact below, in order.",
      `- Write it like a lesson a teacher reads aloud in class: warm, flowing spoken ${ml ? "Malayalam" : "English"} in full paragraphs, as if you are talking to me. I may listen to it with the read-aloud (Listen) option.`,
      ml
        ? "- Because it will be read aloud: no tables, bullet points, headings, bold, emoji or code blocks. Write numbers and percentages in words. Move to each new topic with a spoken line, like \"ഇനി നമുക്ക് അടുത്ത കാര്യം നോക്കാം\"."
        : "- Because it may be read aloud: no tables, bullet points, headings, bold, emoji or code blocks. Write numbers and percentages in words. Move to each new topic with a spoken line, like \"Now let's look at the next idea\".",
      ml
        ? "- Keep English technical terms (prompt, context window, API and so on) in English, and explain each one in Malayalam the first time."
        : "- Explain each technical term (prompt, context window, API and so on) in plain words the first time.",
      "- Give a small everyday example for each main idea, and clearly warn me about each exam trap listed below.",
      "- If the lesson is too long for one reply, stop at the end of a topic, tell me to type \"continue\", and carry on from there when I do.",
      "- Finish the lesson with a short three-point recap.",
      "",
      "Part 2: exam practice, only after the full lesson is done.",
      `- Ask me six exam-style questions${ml ? " in Malayalam (keep the technical terms in English)" : ""}, one at a time: short real-world scenarios with four options (A to D), like the real exam. Mix easy and hard ones, and use the practice questions below where they fit.`,
      "- Wait for my answer. Then tell me if I'm right, why the correct option is right and why the others are wrong, in two or three sentences, then ask the next question.",
      "- At the end, give me a score card: my score out of six, which topics I'm ready on, which I should revise, and one exam tip for this domain.",
      "",
      "Teach only from the facts below. If I ask about something they don't cover, say you're not sure instead of guessing.",
      "",
      "Topics:",
      ...topics,
      "",
      "Key facts to teach:",
      ...facts,
      "",
      `Start now with Part 1: greet me${ml ? " in Malayalam" : ""}, then read me the full lesson.`,
    ].join("\n");
  };
  const copyText = (text) => {
    // Synchronous copy first, so it completes before the link navigates away.
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:0;left:-9999px;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, text.length);
    let ok = false;
    try { ok = document.execCommand("copy"); } catch {}
    ta.remove();
    if (!ok && navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
    return ok || !!navigator.clipboard;
  };
  if (examCode) {
    document.querySelectorAll('section.domain[id^="d"]').forEach((sec) => {
      if (!/^d\d+$/.test(sec.id)) return;
      const card = document.createElement("div");
      card.className = "gm-card";
      card.innerHTML = `
        <a class="gm-btn" data-lang="en" target="_blank" rel="noopener"><span aria-hidden="true">✨</span> Practise with Gemini</a>
        <a class="gm-btn alt" data-lang="ml" target="_blank" rel="noopener" lang="ml">മലയാളത്തിൽ</a>
        <span class="gm-status" aria-live="polite">Copies a prompt and opens Gemini: the full lesson first, then exam-style questions and a score card.</span>
        <details class="gm-prompt"><summary>See the prompt</summary><textarea readonly rows="9" aria-label="Gemini prompt"></textarea></details>`;
      const status = card.querySelector(".gm-status");
      const ta = card.querySelector("textarea");
      let prompts = null;   // built on first use
      const get = (lang) => { prompts ??= { en: buildPrompt(sec, "en"), ml: buildPrompt(sec, "ml") }; return prompts[lang]; };
      card.querySelector(".gm-prompt").addEventListener("toggle", () => { if (!ta.value) ta.value = get("en"); });
      card.querySelectorAll(".gm-btn").forEach((link) => {
        link.href = geminiHref;
        link.addEventListener("click", () => {
          const text = get(link.dataset.lang);
          ta.value = text;
          const ok = copyText(text);
          status.textContent = ok
            ? "✓ Prompt copied. In Gemini, paste and send. To listen, choose Listen (read aloud) in the reply's ⋮ menu; to answer by voice, use Gemini Live."
            : "Couldn't copy automatically. Open \"See the prompt\", copy it, and paste it into Gemini.";
          status.classList.toggle("ok", ok);
        });
      });
      (sec.querySelector(":scope > .audio-note") || sec.querySelector(".domain-head"))?.after(card);
    });
  }

  /* 8. Quizzes: <div class="quiz" data-answer="B"> -------------------------- */
  document.querySelectorAll(".quiz[data-answer]").forEach((quiz) => {
    const answer = quiz.dataset.answer.trim().toUpperCase().charCodeAt(0) - 65;
    const opts = [...quiz.querySelectorAll("ol > li")];
    opts.forEach((li, i) => {
      li.tabIndex = 0;
      const pick = () => {
        if (quiz.classList.contains("answered")) return;
        quiz.classList.add("answered");
        opts[answer]?.classList.add("correct");
        if (i !== answer) li.classList.add("wrong");
      };
      li.addEventListener("click", pick);
      li.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), pick()));
    });
  });
})();
