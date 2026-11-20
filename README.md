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
assets/css/style.css  Design system (light and dark themes, print styles)
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

## Malayalam audio notes

A domain can start with a "മലയാളത്തിൽ കേൾക്കാം" card: a beginner-friendly Malayalam script, a read-along transcript and a player. The transcript in the page is the single source; the MP3 is generated from it, so text and audio never drift apart.

- English exam terms are written in Malayalam script so the voice pronounces them; the English word shows as a small grey gloss (`<span class="en">`) and is not spoken.
- `tools/make_audio.py` turns each transcript into `assets/audio/<id>.mp3` with Meta's MMS Malayalam voice and writes the paragraph start times back into the page, so the current paragraph highlights and tapping a paragraph jumps there. Setup and usage are at the top of the script.
- Without an MP3, the card falls back to the browser's own Malayalam voice, which only some devices have.

## Learn with Gemini

Every exam domain has a "Learn this domain in Malayalam with Gemini" button. It copies a tutor prompt built from that domain's notes (diagram captions, callouts, flashcards, practice questions) and opens Gemini: the Gemini app on Android, gemini.google.com elsewhere. Paste, send, then use Gemini Live or read-aloud to learn by voice. The prompt is also shown under "See the prompt" in case copying is blocked.

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
