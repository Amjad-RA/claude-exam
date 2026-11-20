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

  /* 6. Malayalam audio notes: <div class="audio-note" data-audio="file.mp3">
        With data-audio: a normal audio player; paragraphs with data-t="seconds"
        highlight as it plays and can be tapped to jump there.
        Without it: a preview read by the browser's own Malayalam voice, one
        sentence at a time (long utterances get cut off in some browsers). */
  document.querySelectorAll(".audio-note").forEach((note) => {
    const btn = note.querySelector(".an-play");
    const status = note.querySelector(".an-status");
    const script = note.querySelector(".an-script");
    const parts = [...note.querySelectorAll("[data-say]")];
    const speedBtns = [...note.querySelectorAll(".an-speed button")];
    const mark = (i) => parts.forEach((p, j) => p.classList.toggle("speaking", j === i));
    const spoken = (el) => {
      const c = el.cloneNode(true);
      c.querySelectorAll(".en").forEach((e) => e.remove()); // English glosses are for reading only
      return c.textContent.replace(/\s+/g, " ").trim();
    };
    let rate = 1;
    let audio = null;
    speedBtns.forEach((b) => b.addEventListener("click", () => {
      rate = parseFloat(b.dataset.rate);
      speedBtns.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      if (audio) audio.playbackRate = rate;
    }));

    if (note.dataset.audio) {
      audio = document.createElement("audio");
      audio.src = note.dataset.audio;
      audio.preload = "none";
      audio.controls = true;
      note.querySelector(".an-audio").appendChild(audio);
      btn.hidden = true;
      status.textContent = "";
      const times = parts.map((p) => parseFloat(p.dataset.t));
      audio.addEventListener("timeupdate", () => {
        let i = -1;
        times.forEach((t, j) => { if (!isNaN(t) && t <= audio.currentTime) i = j; });
        mark(i);
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
      return;
    }

    const synth = window.speechSynthesis;
    if (!synth) {
      status.textContent = "This browser can't play the preview. Read along below.";
      return;
    }
    // One queue item per sentence, remembering which paragraph it belongs to.
    const queue = [];
    const firstOf = [];
    parts.forEach((p, i) => {
      firstOf[i] = queue.length;
      spoken(p).split(/(?<=[.!?:;])\s+/).filter(Boolean).forEach((text) => queue.push({ i, text }));
    });
    let voice = null;
    let playing = false;
    let pos = 0;
    let run = 0; // invalidates callbacks from utterances that were cancelled
    const pick = () => {
      voice = synth.getVoices().find((v) => /^ml([-_]|$)/i.test(v.lang)) || null;
      btn.disabled = !voice;
      status.textContent = voice
        ? `Preview voice: ${voice.name}`
        : "No Malayalam voice on this device. It is usually available in Edge on Windows and Chrome on Android. You can read along below.";
    };
    const stop = () => {
      run++;
      playing = false;
      synth.cancel();
      mark(-1);
      btn.textContent = "▶ Play";
    };
    const speakNext = (r) => {
      if (r !== run || !playing) return;
      if (pos >= queue.length) return stop();
      const item = queue[pos];
      const u = new SpeechSynthesisUtterance(item.text);
      u.voice = voice;
      u.lang = voice.lang;
      u.rate = rate;
      u.onend = () => { if (r === run && playing) { pos++; speakNext(r); } };
      u.onerror = (e) => { if (r === run && e.error !== "interrupted" && e.error !== "canceled") stop(); };
      if (!parts[item.i].classList.contains("speaking")) {
        mark(item.i);
        parts[item.i].scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
      synth.speak(u);
    };
    const start = (i) => {
      if (!voice) return;
      run++;
      synth.cancel();
      pos = firstOf[i];
      playing = true;
      if (script) script.open = true;
      btn.textContent = "■ Stop";
      speakNext(run);
    };
    btn.addEventListener("click", () => (playing ? stop() : start(0)));
    parts.forEach((p, j) => p.addEventListener("click", () => start(j)));
    window.addEventListener("pagehide", () => synth.cancel());
    pick();
    if (synth.addEventListener) synth.addEventListener("voiceschanged", pick);
    else synth.onvoiceschanged = pick;
  });

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
