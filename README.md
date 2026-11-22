# Claude Exam Visual Notes

Short, visual study notes for the Anthropic Claude certification exams, published with GitHub Pages:

| Code | Exam | Page |
|---|---|---|
| CCAO-F | Claude Certified Associate – Foundations | `exams/ccao-f.html` |
| CCAR-F | Claude Certified Architect – Foundations | `exams/ccar-f.html` |
| CCAR-P | Claude Certified Architect – Professional | `exams/ccar-p.html` |

The site is plain HTML, CSS and JavaScript. There is no build step and nothing to install.

## Structure

```
index.html            Home page with a tile and progress bar for each exam
components.html       Every note component, shown live with copy-paste HTML
exams/*.html          One page per exam, one <section class="domain"> per domain
assets/css/style.css  Design system, mobile first (light and dark themes, print styles)
assets/js/app.js      Theme toggle, table of contents, search, progress, quizzes
.github/workflows/    GitHub Pages deploy
```

## Adding notes

1. Open the exam page, for example `exams/ccar-f.html`.
2. Fill in the hero details: summary, question count, time and passing score.
3. For each domain, edit its `<section class="domain" id="dN">`: set the title and the weight (`[xx]%` and the bar's `width:xx%`), then replace the placeholder with components copied from `components.html`.
4. To add a domain, copy a whole `<section>` block and give it a unique `id`. The table of contents and progress tracking pick it up automatically.

Components: concept cards, callouts (key, trap, tip, note), flow diagrams, comparison tables, do/don't lists, layer stacks, mnemonics, glossary, keyword chips, flashcards, practice MCQs, cheat sheets and code blocks.

## Features

- Mobile first: phones get the main layout, and wider screens build on it (sidebar from 960px)
  - a bar stuck to the top of the screen names the section you're reading and opens the section list
  - tables with three or more columns turn into one card per row
  - process steps stack top to bottom, and sit side by side once there's room
  - big tap targets for quiz answers, flashcards, "Done" and the Gemini button
  - wide diagrams scroll sideways, with a swipe hint only on the ones that need it
- Light and dark themes, following the system setting, with a toggle
- An auto-generated table of contents that highlights the current section
- A filter box on each page
- "Done" checkboxes per domain, saved in your browser, with progress shown on the home page
- Printing any page gives a compact cheat sheet with all flashcard answers expanded

## Diagrams

The SVG diagrams are plain inline SVG, styled by `assets/css/style.css`, so they follow light/dark mode and each exam's colour. They are described in Python so they stay consistent and easy to change:

```
tools/dglib.py            helpers: boxes, decisions, arrows, labels, placement
tools/dg_ccao.py          CCAO-F diagrams
tools/dg_ccarf.py         CCAR-F diagrams
tools/dg_ccarp.py         CCAR-P diagrams
tools/dg_site.py          home page and components page
tools/build_diagrams.py   writes every diagram into its page
```

After editing a `tools/dg_*.py` file, run:

```bash
python3 tools/build_diagrams.py
```

Each diagram sits between `<!-- dg:ID -->` and `<!-- /dg:ID -->` markers in its page, and only that block is rewritten. The site itself still needs no build step.

## Malayalam audio lessons

A domain can start with a "മലയാളത്തിൽ കേൾക്കാം" card: a beginner lesson in Malayalam with a player, speed buttons and a read-along transcript. The paragraph being read is highlighted, tapping a paragraph plays from there, and the phone's lock screen shows the lesson title.

`tools/make_lesson.py` makes them with the Gemini API, in two steps so the text can be checked before it is voiced:

```bash
python3 tools/make_lesson.py write exams/ccao-f.html d1
```

Gemini writes the lesson from the domain's notes into the page.

```bash
python3 tools/make_lesson.py speak exams/ccao-f.html d1
```

A Gemini voice reads it into `assets/audio/ccao-f-d1.mp3` and the paragraph times are written into the page.

It needs `beautifulsoup4`, `ffmpeg` and a Gemini API key in `GEMINI_API_KEY`. The models and voice can be changed with `GEMINI_TEXT_MODEL`, `GEMINI_TTS_MODEL` and `GEMINI_VOICE`; see the top of the script.

## Practise with Gemini

Every exam domain has a "Practise with Gemini" card with two buttons: English, and മലയാളത്തിൽ (Malayalam, with technical terms kept in English). Each copies a prompt built from that domain's notes (diagram captions, callouts, flashcards, practice questions) and opens Gemini: the Gemini app on Android, gemini.google.com elsewhere. Paste and send: Gemini first teaches the whole domain as one flowing lesson, written to be listened to with its Listen (read aloud) option, then asks six exam-style questions (scenarios with options A to D) one at a time, explains each answer, and ends with a score card of topics to revise. The prompt is also shown under "See the prompt" in case copying is blocked.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy

1. Push to `main`.
2. In the repo, go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
3. The workflow in `.github/workflows/pages.yml` publishes the site to `https://<user>.github.io/<repo>/`.

---

Personal study notes. Not affiliated with or endorsed by Anthropic.
