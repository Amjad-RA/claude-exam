/* Claude Exam Visual Notes — small, dependency-free behaviours.
   1. Theme toggle   2. Auto table of contents + scroll spy
   3. Section search 4. "Done" progress tracking (localStorage)
   5. Practice quizzes                                          */
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

  /* 2. TOC + scroll spy -------------------------------------------------- */
  const toc = document.querySelector("[data-toc]");
  if (toc && domains.length) {
    domains.forEach((sec) => {
      const a = document.createElement("a");
      a.href = `#${sec.id}`;
      a.textContent = sec.querySelector("h2")?.textContent ?? sec.id;
      a.dataset.target = sec.id;
      toc.appendChild(a);
    });
    const links = [...toc.querySelectorAll("a")];
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) links.forEach((l) => l.classList.toggle("active", l.dataset.target === e.target.id));
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
    const pct = domains.length ? Math.round((done.filter((id) => domains.some((d) => d.id === id)).length / domains.length) * 100) : 0;
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

  /* 6. "Learn with Gemini": every exam domain gets a button that copies a
        Malayalam lesson prompt built from that domain's own notes (diagram
        captions, callouts, flashcards, practice questions), then opens
        Gemini — the app on Android, gemini.google.com elsewhere. */
  const examCode = document.querySelector(".hero .exam-code")?.textContent.trim();
  const examName = document.querySelector(".hero h1")?.textContent.trim();
  const isAndroid = /Android/i.test(navigator.userAgent);
  const GEMINI_WEB = "https://gemini.google.com/app";
  const geminiHref = isAndroid
    ? "intent://gemini.google.com/app#Intent;scheme=https;package=com.google.android.apps.bard;S.browser_fallback_url="
      + encodeURIComponent(GEMINI_WEB) + ";end"
    : GEMINI_WEB;
  const clean = (el) => {
    const c = el.cloneNode(true);
    c.querySelectorAll(".label, svg").forEach((e) => e.remove());
    return c.textContent.replace(/\s+/g, " ").trim();
  };
  const buildPrompt = (sec) => {
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
    return [
      `You are my friendly exam tutor. I am a complete beginner preparing for the "${examName}" (${examCode}) certification exam. Teach me Domain ${num}: ${title}${weight ? ` (${weight} of the exam)` : ""}, in simple Malayalam.`,
      "",
      "Part 1: the full lesson. Do this first, and ask me no questions yet.",
      "- Teach the whole domain from start to finish: every topic and every key fact below, in order.",
      "- Write it like a lesson a teacher reads aloud in class: warm, flowing spoken Malayalam in full paragraphs, as if you are talking to me. I will listen to it with the read-aloud (Listen) option.",
      "- Because it will be read aloud: no tables, bullet points, headings, bold, emoji or code blocks. Write numbers and percentages in words. Move to each new topic with a spoken line, like \"ഇനി നമുക്ക് അടുത്ത കാര്യം നോക്കാം\".",
      "- Keep English technical terms (prompt, context window, API and so on) in English, and explain each one in Malayalam the first time.",
      "- Give a small everyday example for each main idea, and clearly warn me about each exam trap listed below.",
      "- If the lesson is too long for one reply, stop at the end of a topic, tell me to type \"continue\", and carry on from there when I do.",
      "- Finish the lesson with a short three-point recap.",
      "",
      "Part 2: questions, only after the full lesson is done.",
      "- Quiz me with five questions in Malayalam, one at a time. Use the practice questions below where they fit.",
      "- After each answer, tell me if I am right and why in one or two sentences, then ask the next question.",
      "- At the end, give me my score and tell me which topics to revise.",
      "",
      "Teach only from the facts below. If I ask about something they don't cover, say you're not sure instead of guessing.",
      "",
      "Topics:",
      ...topics,
      "",
      "Key facts to teach:",
      ...facts,
      "",
      "Start now with Part 1: greet me in Malayalam, then read me the full lesson.",
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
      const prompt = buildPrompt(sec);
      const card = document.createElement("div");
      card.className = "gm-card";
      card.innerHTML = `
        <a class="gm-btn" target="_blank" rel="noopener"><span aria-hidden="true">✨</span> Learn this domain in Malayalam with Gemini</a>
        <span class="gm-status" aria-live="polite">Copies a lesson prompt and opens Gemini: the full lesson first, then questions.</span>
        <details class="gm-prompt"><summary>See the prompt</summary><textarea readonly rows="9" aria-label="Gemini prompt"></textarea></details>`;
      const link = card.querySelector(".gm-btn");
      const status = card.querySelector(".gm-status");
      link.href = geminiHref;
      card.querySelector("textarea").value = prompt;
      link.addEventListener("click", () => {
        const ok = copyText(prompt);
        status.textContent = ok
          ? "✓ Prompt copied. In Gemini, paste and send. To listen, choose Listen (read aloud) in the reply's ⋮ menu."
          : "Couldn't copy automatically. Open \"See the prompt\", copy it, and paste it into Gemini.";
        status.classList.toggle("ok", ok);
      });
      sec.querySelector(".domain-head")?.after(card);
    });
  }

  /* 5. Quizzes: <div class="quiz" data-answer="B"> -------------------------- */
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
