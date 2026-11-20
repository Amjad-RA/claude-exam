"""Diagrams for index.html and components.html."""
import html

from dglib import Diagram, place, place_html

# Home: how the three exams relate ----------------------------------------------
d = Diagram("ex-ladder", 760, 220, "The three exams as rising steps: Associate Foundations, Architect Foundations, Architect Professional")
steps = ((20, 130, "c1", ["CCAO-F · Associate", "~use Claude well at work", "~60 q · 120 min · $99"]),
         (270, 80, "c2", ["CCAR-F · Architect", "~build systems with Claude", "~60 q · 120 min · $125"]),
         (520, 30, "c3", ["CCAR-P · Architect Pro", "~design and run at scale", "~63 q · 120 min · $175"]))
for x, y, k, lines in steps:
    d.box(x, y, 220, 70, lines, k=k)
d.ln([(240, 165), (270, 115)])
d.ln([(490, 115), (520, 65)])
d.text(20, 40, ["~Pass mark on all three:", "^720 / 1000"])
place("index.html", 're:<div class="exam-tiles">', d,
      "Each exam adds depth, from using Claude well to designing production systems. None is a formal prerequisite "
      "for the next.", mode="before")

# Components: a small diagram with its markup -----------------------------------
d = Diagram("demo", 560, 110, "Example diagram: input, process, output", minw=420)
d.box(10, 30, 140, 50, ["Input", "~what arrives"])
d.ln([(150, 55), (210, 55)], lab="sends")
d.box(210, 30, 140, 50, ["Process", "~the step that matters"], k="a")
d.ln([(350, 55), (410, 55)], lab="returns")
d.box(410, 30, 140, 50, ["Output"], k="ok")
fig = d.figure("A caption that states what the picture shows.")
section = f'''<section class="domain" id="diagram">
          <div class="domain-head"><h2>Diagram (SVG)</h2></div>
          <p class="muted">Inline SVG styled by the site's theme, so it follows dark mode and the page's exam colour. Describe diagrams in <code>tools/dg_*.py</code> and run <code>python3 tools/build_diagrams.py</code>; the markup below is what the build writes.</p>
{fig}
          <details class="qa code-toggle"><summary>Show HTML</summary><div class="a"><pre><code>{html.escape(fig)}</code></pre></div></details>
        </section>
'''
place_html("components.html", "demo", 're:<section class="domain" id="code">', section, mode="before")
