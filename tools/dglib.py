"""Helpers for the hand-placed SVG diagrams on the exam pages.

Diagrams are plain inline SVG with no styling of their own: every colour comes
from the `.dg` rules in assets/css/style.css, so they follow light/dark mode
and each page's exam colour.

Edit a tools/dg_*.py file, then run:

    python3 tools/build_diagrams.py

The build rewrites the block between <!-- dg:ID --> and <!-- /dg:ID --> in the
target page. On a first run it inserts the block at the given anchor.

Text conventions for box/diamond/text lines:
    "Title"    bold line          "^plain"   regular weight
    "~small"   small muted line   "`mono"    monospace line
    "!alert"   bold red line
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = []
esc = html.escape


def _n(v):
    if isinstance(v, float):
        s = f"{v:.1f}"
        return s[:-2] if s.endswith(".0") else s
    return str(v)


def _parse(line):
    if line.startswith("~"):
        return "s", line[1:], 15
    if line.startswith("^"):
        return "r", line[1:], 17
    if line.startswith("`"):
        return "m", line[1:], 17
    if line.startswith("!"):
        return "b x", line[1:], 17
    return "b", line, 17


class Diagram:
    def __init__(self, did, W, H, label, minw=None):
        self.id, self.W, self.H, self.label = did, W, H, label
        self.minw = round(W * 0.8) if minw is None else minw
        self.parts = []

    # -- text -------------------------------------------------------------
    def _block(self, x, cy, lines, anchor="middle"):
        if isinstance(lines, str):
            lines = [lines]
        parsed = [_parse(l) for l in lines]
        y = cy - sum(p[2] for p in parsed) / 2
        out = []
        for cls, txt, h in parsed:
            y += h
            out.append(
                f'<text x="{_n(x)}" y="{_n(y - 4.5)}" class="{cls}" '
                f'text-anchor="{anchor}">{esc(txt)}</text>')
        return out

    def text(self, x, cy, lines, anchor="start", k=""):
        """Free text block, vertically centred on cy."""
        self.parts += [f'<g class="tx {k}">', *self._block(x, cy, lines, anchor), "</g>"]

    def lab(self, x, y, s, anchor="middle", k=""):
        """Small muted label with a halo, for arrows and axes."""
        self.parts.append(
            f'<text x="{_n(x)}" y="{_n(y)}" class="lb {k}" text-anchor="{anchor}">{esc(s)}</text>')

    def xmark(self, x, y):
        self.parts.append(f'<text x="{_n(x)}" y="{_n(y)}" class="xm" text-anchor="middle">✗</text>')

    # -- shapes -----------------------------------------------------------
    def box(self, x, y, w, h, lines=(), k="", align="middle", rx=7):
        tx = x + w / 2 if align == "middle" else x + 10
        self.parts += [
            f'<g class="bx {k}"><rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="{rx}"/>',
            *self._block(tx, y + h / 2, lines, align), "</g>"]

    def dia(self, cx, cy, w, h, lines, k=""):
        pts = f"{_n(cx)},{_n(cy - h / 2)} {_n(cx + w / 2)},{_n(cy)} {_n(cx)},{_n(cy + h / 2)} {_n(cx - w / 2)},{_n(cy)}"
        self.parts += [f'<g class="dm {k}" data-maxw="{_n(w * 0.66)}"><polygon points="{pts}"/>',
                       *self._block(cx, cy, lines), "</g>"]

    def circle(self, cx, cy, r, lines=(), k=""):
        self.parts += [f'<g class="bx {k}" data-maxw="{_n(r * 1.7)}"><circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}"/>',
                       *self._block(cx, cy, lines), "</g>"]

    def dot(self, cx, cy, r=5, k="a"):
        self.parts.append(f'<circle class="dot {k}" cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}"/>')

    def rect(self, x, y, w, h, k=""):
        self.parts.append(f'<rect class="{k}" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"/>')

    def tri(self, x, y, k="bp"):
        self.parts.append(f'<polygon class="{k}" points="{_n(x - 6)},{_n(y - 10)} {_n(x + 6)},{_n(y - 10)} {_n(x)},{_n(y)}"/>')

    def ln(self, pts, k="", lab=None, at=None, anchor="middle", head=True, both=False):
        d = "M" + " L".join(f"{_n(x)},{_n(y)}" for x, y in pts)
        self._path(d, k, head, both)
        if lab:
            if at is None:
                (x1, y1), (x2, y2) = pts[0], pts[1]
                at = ((x1 + x2) / 2, (y1 + y2) / 2 - 6)
            self.lab(at[0], at[1], lab, anchor)

    def path(self, d, k="", head=True):
        self._path(d, k, head, False)

    def _path(self, d, k, head, both):
        ks = k.split()
        suf = "-a" if "a" in ks else "-x" if "bad" in ks else "-o" if "ok" in ks else ""
        m = f' marker-end="url(#ah-{self.id}{suf})"' if head else ""
        if both:
            m += f' marker-start="url(#ah-{self.id}{suf})"'
        self.parts.append(f'<path class="ln {k}" d="{d}"{m}/>')

    def raw(self, s):
        self.parts.append(s)

    # -- output -----------------------------------------------------------
    def svg(self):
        markers = "".join(
            f'<marker id="ah-{self.id}{suf}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
            f'markerHeight="6.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ah{cls}"/></marker>'
            for suf, cls in (("", ""), ("-a", " a"), ("-x", " bad"), ("-o", " ok")))
        body = "\n".join(self.parts)
        return (f'<svg viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{esc(self.label)}" '
                f'style="min-width:{self.minw}px;max-width:{round(self.W * 1.15)}px;margin:0 auto" xmlns="http://www.w3.org/2000/svg">\n'
                f"<defs>{markers}</defs>\n{body}\n</svg>")

    def figure(self, caption):
        return (f'<figure class="dg" id="fig-{self.id}">\n<div class="dg-scroll">\n{self.svg()}\n</div>\n'
                f"<figcaption>{caption}</figcaption>\n</figure>")


def place(page, anchor, d, caption, mode="after"):
    """Queue diagram d for page. anchor: 'sub:1.2' (after that subsection heading),
    're:<regex>' or a literal string. mode: after | before | replace_next (replaces
    the next .flow/.stack block after the anchor)."""
    REGISTRY.append((page, d.id, anchor, mode, d.figure(caption)))


def place_html(page, did, anchor, html_block, mode="after"):
    REGISTRY.append((page, did, anchor, mode, html_block))


BLOCK_RE = re.compile(r'(?P<ind>[ \t]*)<div class="(?:flow|stack)[^"]*">\n.*?\n(?P=ind)</div>\n', re.S)


def inject(page, did, anchor, mode, block):
    p = ROOT / page
    s = p.read_text()
    start, end = f"<!-- dg:{did} -->", f"<!-- /dg:{did} -->"
    full = f"{start}\n{block}\n{end}"
    if start in s:
        s = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: full, s, count=1, flags=re.S)
    else:
        if anchor.startswith("sub:"):
            pat = r'<h3 class="sub"><span>' + re.escape(anchor[4:]) + r"</span>.*?</h3>"
        elif anchor.startswith("re:"):
            pat = anchor[3:]
        else:
            pat = re.escape(anchor)
        found = list(re.finditer(pat, s, flags=re.S))
        if len(found) != 1:
            raise SystemExit(f"{page}: anchor for {did} matched {len(found)} times: {anchor[:70]}")
        m = found[0]
        if mode == "after":
            s = s[:m.end()] + "\n" + full + s[m.end():]
        elif mode == "before":
            s = s[:m.start()] + full + "\n" + s[m.start():]
        elif mode == "replace_next":
            b = BLOCK_RE.search(s, m.end())
            if not b:
                raise SystemExit(f"{page}: no flow/stack block after anchor for {did}")
            s = s[:b.start()] + full + "\n" + s[b.end():]
        else:
            raise SystemExit(f"unknown mode {mode}")
    p.write_text(s)
