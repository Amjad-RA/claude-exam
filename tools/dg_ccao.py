"""Diagrams for exams/ccao-f.html (Claude Certified Associate – Foundations)."""
from dglib import Diagram, place

P = "exams/ccao-f.html"

# 1.1 Where each part of a grounded prompt goes ---------------------------------
d = Diagram("ao-prompt", 760, 340, "Layout of a document-grounded prompt: long documents on top, instructions with reasons, one example, the question last")
d.box(40, 12, 380, 318, [], k="frame")
d.box(60, 30, 340, 100, ["<document>", "~long source material,", "~in its own tags"], k="a")
d.box(60, 142, 340, 78, ["<instructions>", "~task · audience · format", "~constraints · depth + why"])
d.box(60, 232, 340, 44, ["<example> × 1"])
d.box(60, 288, 340, 30, ["The question, last"])
for cy, lines in ((80, ["Long documents go on top", "~have Claude quote the relevant", "~passages before it answers"]),
                  (181, ["Give the reason for each rule", "~Claude generalises from the why"]),
                  (254, ["Start with one example", "~add more only if it still misses"]),
                  (303, ["Say what you want, in that style", "~\"use prose\", not \"no markdown\""])):
    d.ln([(448, cy), (406, cy)])
    d.text(456, cy, lines)
place(P, 're:<div class="callout trap"><div><strong class="label">Exam trap</strong>Answers like', d,
      "Where each part of a document-grounded prompt goes. Long material sits on top, the question comes last, "
      "and the prompt is written in the style you want back.", mode="before")

# 1.2 Chain vs parallel ----------------------------------------------------------
d = Diagram("ao-chain", 760, 330, "A sequential prompt chain with checks between stages, compared with parallel parts that are merged")
d.text(20, 22, ["Sequential chain: each stage needs the previous output"])
for i, lines in enumerate((["Extract", "~key clauses"], ["Compare", "~point by point"], ["Draft", "~risk memo"], ["Review", "~final check"])):
    x = 20 + i * 200
    d.box(x, 44, 120, 48, lines, k="a" if i == 3 else "")
    if i < 3:
        gx = x + 160
        d.ln([(x + 120, 68), (gx - 14, 68)])
        d.circle(gx, 68, 13, ["✓"], k="ok")
        d.ln([(gx + 14, 68), (x + 200, 68)])
d.text(380, 116, ["~check each hand-off: an unchecked early error is inherited by every later stage"], anchor="middle")
d.text(20, 160, ["Parallel: independent parts, merged at the end"])
d.box(20, 226, 120, 48, ["Split", "~by topic"])
for cy, name in ((199, "A"), (250, "B"), (301, "C")):
    d.box(220, cy - 19, 150, 38, [f"Cluster {name} → FAQs"])
    d.ln([(140, 250), (220, cy)])
    d.ln([(370, cy), (450, 250 + (cy - 250) // 5)])
d.box(450, 226, 120, 48, ["Merge"])
d.ln([(570, 250), (620, 250)])
d.box(620, 226, 120, 48, ["One FAQ"], k="a")
place(P, "sub:1.2", d,
      "Chain the stages that depend on each other and check each hand-off; run independent parts in parallel and merge. "
      "Chaining adds calls, so it is slower, but every step is easier and can be inspected.")

# 2.2 Classify the flaw ----------------------------------------------------------
d = Diagram("ao-flaw", 620, 420, "Decision tree: hallucination, inconsistency, bias or miscalibration", minw=520)
d.box(20, 10, 180, 40, ["Flawed output"])
d.ln([(110, 50), (110, 63)])
d.dia(110, 105, 220, 84, ["Any basis in", "a source?"])
d.dia(110, 205, 220, 84, ["Contradicts itself", "or another run?"])
d.dia(110, 305, 220, 84, ["Leans one way?"])
for cy, lab, lines in ((105, "no", ["Hallucination", "~invented: fake citation, \"email sent\""]),
                       (205, "yes", ["Inconsistency", "~two values, no new input between"]),
                       (305, "yes", ["Bias", "~skewed default · missing view · framing"])):
    d.ln([(220, cy), (300, cy)], lab=lab)
    d.box(300, cy - 24, 300, 48, lines, k="bad" if lab == "no" else "warn")
d.ln([(110, 147), (110, 163)], lab="yes", at=(118, 158), anchor="start")
d.ln([(110, 247), (110, 263)], lab="no", at=(118, 258), anchor="start")
d.ln([(110, 347), (110, 362)], lab="no", at=(118, 358), anchor="start")
d.box(10, 362, 200, 48, ["Miscalibrated?", "~confidence not backed by evidence"])
place(P, "sub:2.2", d,
      "Name the kind of wrong from what you can observe, then choose the fix. Two values for one fact with nothing new "
      "in between is an inconsistency; calling it a hallucination needs evidence of which one was invented.")

# 2.4 Review depth -------------------------------------------------------------
d = Diagram("ao-review", 760, 320, "Two by two: review depth by stakes and audience")
d.box(130, 20, 250, 120, ["Qualified reviewer", "~checks the substance"], k="warn")
d.box(380, 20, 250, 120, ["Qualified, accountable", "~approves before release"], k="bad")
d.box(130, 140, 250, 120, ["Light review", "~you check it yourself"])
d.box(380, 140, 250, 120, ["Careful read", "~before it goes out"])
d.lab(120, 84, "high", anchor="end")
d.lab(120, 204, "low", anchor="end")
d.text(60, 144, ["Stakes"], anchor="end")
d.lab(255, 280, "internal")
d.lab(505, 280, "external or affected people")
d.text(380, 304, ["Audience"], anchor="middle")
d.box(648, 20, 102, 240, ["Not a", "substitute", "~self-check", "~2nd Claude", "~citations", "~polished tone", "~AI label"], k="dash")
place(P, "sub:2.4", d,
      "Who reviews, and how deeply, scales with the stakes and who will see the output. High-stakes output reaches no one "
      "until a qualified, accountable person has checked the substance.")

# 2.6 Output format --------------------------------------------------------------
d = Diagram("ao-format", 760, 300, "Decision tree for choosing JSON, an artifact or an inline answer")
d.dia(100, 150, 180, 88, ["Who reads", "the output?"])
d.ln([(100, 106), (100, 60), (560, 60)], lab="a program", at=(330, 52))
d.box(560, 36, 190, 48, ["JSON + schema", "~valid ≠ correct values"], k="a")
d.ln([(190, 150), (290, 150)], lab="a person", at=(240, 142))
d.dia(405, 150, 230, 96, ["Stands alone,", "15+ lines, reused?"])
d.ln([(520, 150), (560, 150)], lab="yes", at=(540, 142))
d.box(560, 126, 190, 48, ["Artifact", "~SVG · Mermaid · React · doc"], k="ok")
d.ln([(405, 198), (405, 236)], lab="no", at=(413, 222), anchor="start")
d.box(315, 236, 180, 44, ["Inline answer"])
d.box(560, 236, 190, 44, ["Inline visual?", "~save as an artifact to keep"], k="dash")
place(P, "sub:2.6", d,
      "The format follows the destination: a program gets schema-checked JSON; a person gets an artifact only when the "
      "piece stands alone and will be reused or edited.")

# 3.1 Feature picker -------------------------------------------------------------
d = Diagram("ao-feature", 870, 230, "Decision path from plain chat to Research, Project or Artifact")
d.box(10, 40, 110, 48, ["Plain chat", "~start here"])
d.ln([(120, 64), (140, 64)])
qs = ((230, ["Dozens of", "sources?"], ["Research", "~5+ tool calls, 1–3 min", "~cited report"]),
      (430, ["Same docs in", "every chat?"], ["Project", "~knowledge + instructions", "~Team/Ent. can share"]),
      (630, ["Editable", "deliverable?"], ["Artifact", "~side panel", "~version history"]))
for i, (cx, q, out) in enumerate(qs):
    d.dia(cx, 64, 180, 84, q)
    d.ln([(cx, 106), (cx, 150)], lab="yes", at=(cx + 8, 132), anchor="start")
    d.box(cx - 90, 150, 180, 64, out, k="a")
    nxt = 340 if i == 0 else 540 if i == 1 else 750
    d.ln([(cx + 90, 64), (nxt, 64)], lab="no", at=(cx + 90 + (nxt - cx - 90) / 2, 56))
d.box(750, 40, 110, 48, ["Stay in chat", "~+ web search"])
place(P, "sub:3.1", d,
      "Start in chat and move only when you can name the gap: breadth across many sources → Research, the same context "
      "every time → Project, a deliverable you will keep editing → Artifact.")

# 3.2 Model tiers ----------------------------------------------------------------
d = Diagram("ao-tiers", 760, 300, "Haiku, Sonnet and Opus on one trade-off line with output prices to scale")
for cx, name, h, price, lat, use in ((150, "Haiku", 3, "from $0.10 / $0.50", "Fastest", "classify · route · extract"),
                                     (380, "Sonnet", 40, "$2 / $10", "Fast", "everyday workhorse"),
                                     (610, "Opus", 80, "$4 / $20", "Moderate (slowest)", "long agentic work")):
    d.rect(cx - 22, 110 - h, 44, h, k="seg-a")
    d.lab(cx, 110 - h - 8, price + " per MTok")
    d.circle(cx, 160, 34, [name], k="a")
    d.text(cx, 216, [lat], anchor="middle")
    d.text(cx, 240, ["~" + use], anchor="middle")
d.ln([(40, 272), (720, 272)], both=True)
d.lab(40, 292, "faster · cheaper", anchor="start")
d.lab(720, 292, "more reasoning depth", anchor="end")
place(P, "sub:3.2", d,
      "One family, one trade-off: moving right buys reasoning depth with latency and price (bars show output price to "
      "scale). Choose by how hard the task is, not by subject. Fable 5.1 sits above Opus as the frontier model.")

# 3.4 Context window vs usage allowance -----------------------------------------
d = Diagram("ao-limits", 760, 330, "Context window per chat compared with the usage allowance across chats")
d.text(40, 20, ["Length limit: one chat"])
d.box(60, 36, 200, 244, [], k="frame")
d.text(160, 64, ["~room left"], anchor="middle")
d.box(64, 90, 192, 34, ["Claude's reply"])
d.box(64, 124, 192, 64, ["Conversation", "~so far"])
d.box(64, 188, 192, 46, ["Attached files"])
d.box(64, 234, 192, 42, ["Instructions"])
d.ln([(284, 272), (284, 46)], k="bad")
d.text(296, 160, ["Recall drops", "~as it fills"])
d.text(160, 304, ["^Full → new chat, or a Project"], anchor="middle")
d.text(420, 20, ["Usage limit: across chats"])
for y, name in ((46, "Chat A"), (94, "Chat B"), (142, "Claude Code")):
    d.box(420, y, 130, 36, [name])
    d.ln([(550, y + 18), (600, 112 + (y - 94) // 4)])
d.box(600, 70, 150, 84, ["Usage allowance", "~5-hour session", "~+ weekly limits"], k="a")
d.text(675, 192, ["^Hit it: wait, upgrade,", "^or use usage credits"], anchor="middle")
d.box(600, 226, 150, 36, ["New chat: no help"], k="bad")
place(P, "sub:3.4", d,
      "Two separate budgets. The context window caps one conversation and cannot be enlarged; the usage allowance caps "
      "total use over time, is shared by claude.ai, Claude Code and Desktop, and resets.")

# 5.1 Project layers (replaces the text stack) ----------------------------------
d = Diagram("ao-project", 760, 300, "A Project gives every chat the same instructions and knowledge; chats do not share conversations")
d.box(20, 14, 570, 272, [], k="frame")
d.text(36, 34, ["Project"])
d.box(60, 48, 220, 50, ["Instructions", "~how to behave"], k="a")
d.box(330, 48, 220, 50, ["Knowledge", "~files · RAG when large"], k="a")
d.ln([(170, 98), (170, 144)], k="a", head=False)
d.ln([(440, 98), (440, 144)], k="a", head=False)
d.ln([(115, 144), (495, 144)], k="a", head=False)
for cx in (115, 305, 495):
    d.ln([(cx, 144), (cx, 190)], k="a")
    d.box(cx - 65, 190, 130, 48, [f"Chat {'ABC'[(cx - 115) // 190]}"])
d.lab(305, 136, "every chat starts with both")
for x in (210, 400):
    d.ln([(x - 30, 214), (x + 30, 214)], k="d bad", head=False)
    d.xmark(x, 208)
d.lab(305, 266, "chats don't see each other's conversations")
d.box(615, 48, 135, 50, ["Name and", "~description"], k="dash")
d.text(682, 120, ["!Claude can't see"], anchor="middle")
d.box(615, 190, 135, 48, ["Sharing", "~Team & Enterprise"])
place(P, "sub:5.1", d,
      "Every chat in a Project starts with the same instructions and knowledge, and nothing from sibling chats. "
      "Anything that must carry over belongs in knowledge or instructions.", mode="replace_next")

# 5.2 Upload vs connector --------------------------------------------------------
d = Diagram("ao-connector", 760, 250, "An upload is a fixed copy; a connector is live access narrowed by your account and your organisation")
d.text(20, 22, ["Upload"])
d.box(20, 40, 140, 48, ["Your file"])
d.ln([(160, 64), (240, 64)], lab="copied once")
d.box(240, 40, 200, 48, ["Fixed copy", "~in the chat or project"])
d.text(460, 64, ["~doesn't follow later edits"])
d.text(20, 122, ["Connector"])
d.box(20, 140, 140, 48, ["Drive or Gmail"])
d.ln([(160, 164), (210, 164)], lab="live")
d.box(210, 140, 150, 48, ["Your account's", "~own access"], k="dash")
d.ln([(360, 164), (400, 164)])
d.box(400, 140, 150, 48, ["Org allows", "~admin + restrictions"], k="dash")
d.ln([(550, 164), (600, 164)])
d.box(600, 140, 140, 48, ["Claude"], k="a")
d.box(210, 206, 340, 36, ["^Gmail: body + metadata, never attachments"], k="warn")
place(P, "sub:5.2", d,
      "An upload is a frozen copy. A connector is live access, narrowed first by what your own account can reach and "
      "then by what your organisation allows.")

# 6.1 Fit and autonomy -----------------------------------------------------------
d = Diagram("ao-autonomy", 760, 240, "Decision: is the use case recoverable, and how much autonomy fits")
d.dia(120, 90, 210, 96, ["Errors caught", "before harm?"])
d.ln([(120, 138), (120, 178)], lab="no", at=(128, 162), anchor="start")
d.box(20, 178, 200, 48, ["Wrong use case", "~however good the prompt"], k="bad")
d.ln([(225, 90), (290, 90)], lab="yes")
d.dia(395, 90, 210, 96, ["Mistake cheap", "to undo?"])
d.ln([(500, 90), (530, 90), (530, 46), (560, 46)])
d.ln([(530, 90), (530, 154), (560, 154)])
d.lab(536, 64, "yes", anchor="start")
d.lab(536, 130, "no", anchor="start")
d.box(560, 22, 190, 48, ["Grant autonomy", "~research · forms · tests"], k="ok")
d.box(560, 130, 190, 48, ["Require approval", "~send · buy · edit records"], k="warn")
place(P, "sub:6.1", d,
      "The recoverable-work test decides whether Claude fits at all; how easily a mistake can be undone then decides "
      "how much autonomy an agent gets.")

# 6.2 Retention timeline ---------------------------------------------------------
d = Diagram("ao-retention", 790, 230, "Consumer retention timeline: immediately, 30 days, 2 years, 5 years, 7 years")
d.ln([(40, 115), (775, 115)])
pts = ((90, "above", ["Delete a chat", "~gone from history now"]),
       (230, "below", ["Within 30 days", "~purged from back end"]),
       (390, "above", ["Up to 2 years", "~flagged chat content"]),
       (550, "below", ["Up to 5 years", "~opt-in training · feedback"]),
       (700, "above", ["Up to 7 years", "~flagged: safety scores"]))
for x, pos, lines in pts:
    d.dot(x, 115, 6)
    if pos == "above":
        d.ln([(x, 103), (x, 92)], head=False)
        d.text(x, 68, lines, anchor="middle")
    else:
        d.ln([(x, 127), (x, 138)], head=False)
        d.text(x, 162, lines, anchor="middle")
d.text(20, 214, ["~Consumer plans (Free, Pro, Max). Not to scale."])
place(P, "re:<div class=\"grid cols-2\">\\s*<div class=\"card accent\"><h4>🏥", d,
      "Consumer-plan retention: each number belongs to one trigger. A flagged chat's safety scores are kept longer "
      "than the chat itself.", mode="before")

# 7.1 Diagnose ladder ------------------------------------------------------------
d = Diagram("ao-ladder", 760, 250, "Five causes of poor output, checked in order from prompt to model tier")
steps = (["1 · Prompt", "~generic or thin?"], ["2 · Knowledge", "~confident, wrong?"], ["3 · Conversation", "~long, mixed chat?"],
         ["4 · Effort", "~skipped steps?"], ["5 · Model tier", "~still fails?"])
for i, lines in enumerate(steps):
    d.box(20 + i * 146, 150 - i * 30, 140, 56, lines, k="ok" if i == 0 else "warn" if i == 4 else "")
d.ln([(20, 236), (744, 236)])
d.lab(382, 228, "check in this order: most common and cheapest to change first")
place(P, "sub:7.1", d,
      "Five causes look alike from outside. Check them in order: the prompt is the most common cause and the cheapest "
      "to change; move up a model tier only after ruling out the rest.")
