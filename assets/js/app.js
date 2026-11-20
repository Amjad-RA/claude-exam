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
