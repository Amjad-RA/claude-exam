"""Diagrams for exams/ccar-f.html (Claude Certified Architect – Foundations)."""
from dglib import Diagram, place, place_html

P = "exams/ccar-f.html"

# 1.1 Agentic loop (replaces the text flow) -------------------------------------
d = Diagram("af-loop", 760, 270, "The agentic loop: send, Claude generates, branch on stop_reason, run tools, append results, send again")
d.box(20, 82, 140, 56, ["Send request", "~history + tools"])
d.ln([(160, 110), (180, 110)])
d.box(180, 82, 115, 56, ["Claude", "~generates"], k="a")
d.ln([(295, 110), (310, 110)])
d.dia(405, 110, 190, 84, ["stop_reason?"], k="a")
d.ln([(405, 68), (405, 39), (570, 39)], lab="anything else", at=(487, 31))
d.box(570, 14, 180, 50, ["Handle the exit", "~max_tokens · refusal · …"], k="warn")
d.ln([(500, 110), (570, 110)], lab="end_turn", at=(535, 102))
d.box(570, 88, 180, 44, ["Done: use the answer"], k="ok")
d.ln([(405, 152), (405, 196)], k="a", lab="tool_use", at=(413, 178), anchor="start")
d.box(335, 196, 140, 48, ["Run the tools"])
d.ln([(335, 220), (310, 220)], k="a")
d.box(110, 192, 200, 56, ["Append to history", "~turn + tool_result per id"])
d.ln([(110, 220), (90, 220), (90, 138)], k="a")
d.lab(84, 180, "next request", anchor="end")
place(P, "sub:1.1", d,
      "One field drives the loop: \"tool_use\" means run the tools, append the results and send again; any other "
      "stop_reason exits. A turn cap is a safety net, reported as error_max_turns, not success.", mode="replace_next")

# 1.2 Hub and spoke --------------------------------------------------------------
d = Diagram("af-hub", 760, 306, "Coordinator with three subagents: spawn prompts go down, only final messages come back")
d.box(270, 16, 220, 84, ["Coordinator", "~full history", "~the user's decisions"], k="a")
for cx, (dx, ux) in zip((120, 380, 640), ((330, 350), (370, 390), (410, 430))):
    d.ln([(dx, 100), (cx - 20, 206)], k="a")
    d.ln([(cx + 20, 206), (ux, 100)], k="d")
    d.box(cx - 100, 206, 200, 72, ["Subagent", "~fresh, empty context", "~own prompt + spawn prompt"])
d.lab(195, 150, "spawn prompt: all it gets", anchor="end")
d.lab(565, 150, "final message only", anchor="start")
for x in (250, 510):
    d.xmark(x, 248)
d.lab(380, 300, "subagents never talk to each other")
place(P, "sub:1.2", d,
      "Hub and spoke: each subagent starts empty, sees only its own system prompt plus what the coordinator writes into "
      "the spawn, and sends back only its final message. Several Task calls in one response run in parallel.")

# 1.4 Prerequisite gate (replaces the text flow) --------------------------------
d = Diagram("af-gate", 760, 256, "Prerequisite gate: PostToolUse records a verified lookup, PreToolUse blocks the refund until the record exists")
d.box(40, 20, 170, 44, ["get_customer"])
d.box(520, 20, 200, 44, ["process_refund"])
d.ln([(125, 64), (125, 110)], lab="succeeds", at=(131, 92), anchor="start")
d.ln([(620, 64), (620, 110)], lab="attempted", at=(626, 92), anchor="start")
d.box(40, 110, 170, 50, ["PostToolUse", "~after a successful call"], k="a")
d.box(520, 110, 200, 50, ["PreToolUse", "~before the call runs"], k="a")
d.box(290, 108, 150, 54, ["Session state", "~verified: cust_123"], k="dash")
d.ln([(210, 135), (290, 135)], lab="writes")
d.ln([(520, 135), (440, 135)], lab="reads")
d.ln([(580, 160), (515, 200)], k="bad")
d.ln([(660, 160), (685, 200)], k="ok")
d.lab(540, 178, "no record", anchor="end")
d.lab(678, 178, "verified", anchor="start")
d.box(430, 200, 170, 44, ["deny + reason"], k="bad")
d.box(620, 200, 130, 44, ["refund runs"], k="ok")
place(P, "sub:1.4", d,
      "The order is enforced outside the model: a record is written only after the lookup succeeds, and the refund "
      "tool is blocked until that record exists. A prompt can ask for this order; only the gate guarantees it.",
      mode="replace_next")

# 1.5 Hook path ------------------------------------------------------------------
d = Diagram("af-hooks", 800, 220, "Tool call path through PreToolUse and PostToolUse hooks")
d.box(10, 40, 120, 56, ["Claude", "~emits tool_use"])
d.ln([(130, 68), (165, 68)])
d.box(165, 40, 160, 56, ["PreToolUse", "~name match → callback"], k="a")
d.ln([(325, 68), (360, 68)], lab="allow", at=(342, 60))
d.box(360, 40, 110, 56, ["Tool runs"])
d.ln([(470, 68), (505, 68)])
d.box(505, 40, 150, 56, ["PostToolUse", "~updatedToolOutput"], k="a")
d.ln([(655, 68), (690, 68)])
d.box(690, 40, 100, 56, ["Claude", "~reads result"])
d.text(580, 120, ["~mixed formats in,", "~one format out"], anchor="middle")
d.ln([(245, 96), (245, 150)], k="bad", lab="deny", at=(251, 128), anchor="start")
d.box(150, 150, 190, 56, ["Blocked", "~reason names the next step"], k="bad")
d.ln([(340, 178), (390, 178)])
d.box(390, 150, 190, 56, ["Agent follows it", "~e.g. escalate_refund"])
place(P, "sub:1.5", d,
      "PreToolUse decides before a call runs (allow, deny with a reason, or ask); PostToolUse can rewrite the result "
      "before Claude reads it. Matchers test only the tool name; argument checks go in the callback.")

# 1.6 Decomposition decision -----------------------------------------------------
d = Diagram("af-decomp", 760, 246, "Decision: prompt chain, parallel sections or adaptive orchestrator")
d.dia(120, 110, 210, 96, ["Subtasks known", "before the run?"])
d.ln([(225, 110), (250, 110), (250, 64), (280, 64)], lab="yes", at=(256, 92), anchor="start")
d.dia(390, 64, 220, 90, ["Each step needs", "the last output?"])
d.ln([(500, 64), (530, 64), (530, 32), (560, 32)])
d.ln([(530, 64), (530, 104), (560, 104)])
d.lab(536, 50, "yes", anchor="start")
d.lab(536, 92, "no", anchor="start")
d.box(560, 8, 190, 48, ["Prompt chain", "~code sequences, gates"])
d.box(560, 80, 190, 48, ["Parallel sections", "~+ integration pass"])
d.ln([(120, 158), (120, 206), (300, 206)], lab="no", at=(126, 186), anchor="start")
d.box(300, 182, 230, 48, ["Adaptive orchestrator", "~next task from findings"], k="a")
place(P, "sub:1.6", d,
      "Ask one question first: can you write the subtask list before the run? If yes, your code sequences or "
      "parallelises the steps; if the work only reveals itself as you go, an orchestrator plans each next step from "
      "what it found.")

# 1.7 Sessions -------------------------------------------------------------------
d = Diagram("af-sessions", 780, 230, "Sessions as timelines: resume by name, continue picks the latest, fork creates a new branch")
d.ln([(200, 50), (500, 50)], head=False)
for x in (260, 380, 500):
    d.dot(x, 50, k="m")
d.text(200, 30, ["C · most recent"])
d.ln([(40, 120), (400, 120)], head=False)
for x in (80, 160, 240, 320, 400):
    d.dot(x, 120)
d.text(40, 100, ["A · payment-retry-bug"])
d.path("M240,120 L280,180 L500,180", k="a", head=False)
for x in (360, 440, 500):
    d.dot(x, 180)
d.text(310, 206, ["B · fork of A (A unchanged)"])
d.ln([(552, 120), (412, 120)], k="a")
d.text(560, 120, ["`--resume payment-retry-bug"])
d.ln([(552, 50), (512, 50)])
d.text(560, 50, ["`--continue → latest in dir"])
d.ln([(552, 180), (512, 180)], k="a")
d.text(560, 180, ["`fork_session() → resume"])
place(P, "sub:1.7", d,
      "continue takes whatever session is most recent in the directory; resume names the one you want; a fork copies "
      "history into a new session and leaves the original intact, without its \"allow for this session\" grants. A "
      "resumed session replays old tool results, so name any files that changed.")

# 2.2 Error routing --------------------------------------------------------------
d = Diagram("af-errors", 760, 250, "Decision tree for MCP tool results: success, transient, validation, business, permission")
d.dia(110, 80, 190, 90, ["Tool answered", "the question?"])
d.ln([(110, 125), (110, 176)], k="ok", lab="yes", at=(118, 156), anchor="start")
d.box(20, 176, 180, 56, ["Success", "~0 matches is fine"], k="ok")
d.ln([(205, 80), (305, 80)], k="bad", lab="isError: true", at=(255, 72))
d.dia(400, 80, 190, 90, ["Same request", "works later?"])
d.ln([(495, 80), (560, 80)], lab="yes", at=(527, 72))
d.box(560, 52, 190, 56, ["transient", "~isRetryable: true"], k="ok")
d.ln([(400, 125), (400, 152)], head=False)
d.ln([(305, 152), (635, 152)], head=False)
d.lab(410, 146, "no · isRetryable: false", anchor="start")
for cx, lines in ((305, ["validation", "~fix the input"]), (470, ["business", "~explain the policy"]),
                  (635, ["permission", "~new credential"])):
    d.ln([(cx, 152), (cx, 176)])
    d.box(cx - 75, 176, 150, 56, lines, k="warn")
place(P, "sub:2.2", d,
      "A query that ran and found nothing is a success. Real failures come back as isError results with a category, "
      "and isRetryable answers one question: would the identical request succeed if sent again?")

# 3.1 CLAUDE.md loading ----------------------------------------------------------
d = Diagram("af-claudemd", 760, 236, "Which CLAUDE.md files load at launch and which load on demand")
d.text(24, 18, ["Working directory: repo/"])
rows = (("`~/.claude/CLAUDE.md", "a", "launch · user level, only you"),
        ("`repo/CLAUDE.md", "a", "launch · project, the team via git"),
        ("`repo/api/CLAUDE.md", "dash", "on demand · when api/ files are read"),
        ("`repo/.claude/rules/tests.md", "a", "launch, or on match if it has paths:"),
        ("`@path import in a loaded file", "a", "loads whenever its importer loads"))
for i, (path, k, pill) in enumerate(rows):
    y = 54 + i * 38
    d.text(24, y, [path])
    d.box(380, y - 14, 360, 28, ["^" + pill], k=k, align="start", rx=14)
place(P, "sub:3.1", d,
      "Where a CLAUDE.md lives decides who gets it and when it loads: files at and above the working directory load at "
      "launch, files below it load only when Claude reads there. /memory shows what actually loaded.")

# 3.3 Glob matching table --------------------------------------------------------
GLOB = '''<div class="table-wrap"><table class="compare">
            <thead><tr><th>File</th><th><code>terraform/*</code></th><th><code>terraform/**/*</code></th><th><code>api/**/*.ts</code></th><th><code>src/api/**/*.ts</code></th></tr></thead>
            <tbody>
              <tr><th><code>terraform/main.tf</code></th><td class="yes">✓</td><td class="yes">✓</td><td class="no">✗</td><td class="no">✗</td></tr>
              <tr><th><code>terraform/modules/vpc/main.tf</code></th><td class="no">✗ nested</td><td class="yes">✓</td><td class="no">✗</td><td class="no">✗</td></tr>
              <tr><th><code>src/api/routes/user.ts</code></th><td class="no">✗</td><td class="no">✗</td><td class="no">✗ starts at repo root</td><td class="yes">✓</td></tr>
            </tbody>
          </table></div>'''
place_html(P, "af-glob", "---</code></pre>", GLOB)

# 4.4 Extraction + validation + retry (replaces the text flow) ------------------
d = Diagram("af-extract", 780, 220, "Extraction with a forced tool, validation in code, retry with feedback, or human review")
d.box(10, 30, 100, 56, ["Document"])
d.ln([(110, 58), (150, 58)])
d.box(150, 30, 170, 56, ["Forced extract tool", "~strict schema"], k="a")
d.ln([(320, 58), (360, 58)])
d.box(360, 30, 160, 56, ["Validate in code", "~sums · conflicts"])
d.ln([(520, 58), (620, 58)], k="ok", lab="pass", at=(570, 50))
d.box(620, 30, 150, 56, ["Accept"], k="ok")
d.ln([(440, 86), (440, 130)], k="bad", lab="fail", at=(446, 112), anchor="start")
d.dia(440, 170, 190, 80, ["Value is in", "the source?"])
d.ln([(345, 170), (300, 170)], lab="yes", at=(322, 162))
d.box(130, 146, 170, 48, ["Retry with", "~doc + output + errors"])
d.ln([(215, 146), (215, 86)], k="a")
d.ln([(535, 170), (620, 170)], lab="no", at=(577, 162))
d.box(620, 146, 150, 48, ["Human review", "~stop retrying"], k="warn")
place(P, "sub:4.4", d,
      "A strict schema removes syntax errors; your own code catches the semantic ones. Retry only when the value "
      "exists in the source, sending the document, the failed output and the exact errors.", mode="replace_next")

# 4.5 Batch SLA ------------------------------------------------------------------
d = Diagram("af-batch", 760, 220, "Worst-case batch timeline: wait one interval, then up to 24 hours, must fit the SLA")
d.text(380, 24, ["interval + 24 h ≤ SLA"], anchor="middle")
d.box(40, 66, 132, 32, ["^wait ≤ 6 h"], k="warn", rx=4)
d.box(172, 66, 528, 32, ["^batch may take the full 24 h"], k="a", rx=4)
for x in (40, 172, 700):
    d.ln([(x, 102), (x, 114)], head=False)
d.text(40, 134, ["~doc arrives just", "~after a submit"])
d.text(172, 128, ["~next submit"], anchor="middle")
d.text(700, 128, ["SLA: 30 h"], anchor="middle")
d.text(380, 186, ["^48 h SLA → a nightly batch works", "^30 h SLA → submit every 4 h, leaving slack"], anchor="middle")
place(P, 're:<div class="callout key"><div><strong class="label">SLA formula</strong>.*?</div></div>', d,
      "Plan for the unluckiest document: it just missed a submission, waits a full interval, then the batch uses the "
      "whole 24-hour window. The interval can be at most the SLA minus 24 hours.")

# 4.6 Review architecture --------------------------------------------------------
d = Diagram("af-review", 780, 300, "Independent reviewer with a fresh context, and a multi-pass review pipeline")
d.box(20, 40, 200, 60, ["Generator session", "~code + its own reasoning"])
d.path("M70,100 C70,132 170,132 170,100", k="bad")
d.text(120, 138, ["!✗ grades itself"], anchor="middle")
d.ln([(220, 70), (320, 70)], k="a", lab="code only")
d.box(320, 40, 200, 60, ["Reviewer", "~fresh context"], k="a")
d.box(560, 40, 200, 60, ["Not independent", "~more thinking, same session"], k="bad")
for i, name in enumerate("ABC"):
    cy = 178 + i * 46
    d.box(20, cy - 18, 150, 36, [f"File {name} pass"])
    d.ln([(170, cy), (240, 224 + (cy - 224) // 4)])
d.box(240, 200, 160, 48, ["Integration pass", "~cross-file"])
d.ln([(400, 224), (570, 224)], lab="findings + confidence")
d.box(570, 200, 190, 48, ["Verification pass", "~filters and routes"], k="a")
place(P, "sub:4.6", d,
      "A reviewer is independent only if it starts from a clean context and never sees the generator's reasoning. "
      "Large reviews run per-file passes, then a cross-file pass, then a separate verification pass that filters by "
      "confidence.")

# 5.2 Escalation -----------------------------------------------------------------
d = Diagram("af-escalate", 870, 296, "Escalation decision: explicit request, policy gap, or no progress; otherwise resolve")
qs = ((130, ["Asks for", "a human?"], ["Hand off now", "~no fix attempt first"]),
      (350, ["Policy silent", "or unclear?"], ["Escalate", "~don't invent a rule"]),
      (570, ["Stuck, no", "real progress?"], ["Escalate", "~structured summary"]))
for i, (cx, q, out) in enumerate(qs):
    d.dia(cx, 64, 200, 88, q)
    d.ln([(cx, 108), (cx, 150)], k="a", lab="yes", at=(cx + 8, 132), anchor="start")
    d.box(cx - 90, 150, 180, 56, out, k="a")
    nxt = (250, 470, 700)[i]
    d.ln([(cx + 100, 64), (nxt, 64)], lab="no", at=((cx + 100 + nxt) / 2, 56))
d.box(700, 40, 160, 48, ["Resolve it", "~offer a human too"], k="ok")
d.box(20, 232, 840, 52, ["^Not triggers: anger or sentiment · the agent's own confidence · how hard it feels",
                         "~Several customers match the lookup? Ask for another identifier; never pick one."], k="dash")
place(P, "sub:5.2", d,
      "Three observable triggers send a case to a person. A customer's frustration alone is not one: acknowledge it, "
      "resolve the issue and offer a human.")

# 5.5 Calibration ----------------------------------------------------------------
d = Diagram("af-calib", 760, 300, "Illustrative calibration chart: stated confidence against observed accuracy with a threshold")
X = lambda c: 80 + (c - 0.5) / 0.5 * 380
Y = lambda a: 240 - (a - 0.4) / 0.6 * 220
thr = X(0.957)
d.rect(thr, 20, 460 - thr, 220, k="zone")
d.ln([(80, 240), (460, 240)], k="ax", head=False)
d.ln([(80, 240), (80, 20)], k="ax", head=False)
for c in (0.5, 0.7, 0.9, 1.0):
    d.lab(X(c), 256, f"{c:.1f}")
for a in (0.4, 0.6, 0.8, 1.0):
    d.lab(72, Y(a) + 4, f"{int(a * 100)}%", anchor="end")
d.lab(270, 282, "stated confidence →")
d.lab(84, 12, "↑ observed accuracy", anchor="start")
d.ln([(X(0.5), Y(0.5)), (X(1.0), Y(1.0))], k="d", head=False)
d.lab(X(0.66), Y(0.7) - 4, "calibrated", anchor="middle")
curve = ((0.5, 0.47), (0.6, 0.53), (0.7, 0.61), (0.8, 0.70), (0.9, 0.82), (0.95, 0.89), (1.0, 0.96))
d.ln([(X(c), Y(a)) for c, a in curve], k="curve", head=False)
d.lab(X(0.72) + 4, Y(0.66) + 28, "model as stated", anchor="start")
d.ln([(80, Y(0.9)), (460, Y(0.9))], k="d ok", head=False)
d.lab(88, Y(0.9) - 6, "target 90%", anchor="start")
d.ln([(thr, 20), (thr, 240)], k="d", head=False)
d.box(490, 30, 260, 50, ["Above the cut-off", "~auto-accept + stratified samples"], k="ok")
d.box(490, 100, 260, 50, ["Below the cut-off", "~human review"], k="warn")
d.box(490, 170, 260, 50, ["Calibrate per field", "~and document type, on labeled data"], k="dash")
place(P, "sub:5.5", d,
      "Illustrative: a model's stated confidence is not a measurement. Plot it against observed accuracy on a labeled "
      "set and put the cut-off where accuracy meets the target, separately for each field and document type.")

# 5.6 Provenance -----------------------------------------------------------------
d = Diagram("af-prov", 760, 250, "Claim records with source, excerpt and date merged into established and contested sections")
d.box(20, 14, 270, 100, ["claim: revenue $420M", "~source: press release", "~excerpt: \"…$420 million…\"", "~date: March"], align="start")
d.box(20, 134, 270, 100, ["claim: revenue $460M", "~source: analyst report", "~excerpt: \"…$460 million…\"", "~date: May"], align="start")
d.ln([(290, 64), (330, 112)])
d.ln([(290, 184), (330, 138)])
d.box(330, 97, 150, 56, ["Coordinator", "~merges records"], k="a")
d.box(520, 10, 230, 230, [], k="frame")
d.text(532, 30, ["Report"])
d.box(535, 44, 200, 60, ["Established", "~agreed across sources"], k="ok")
d.ln([(480, 125), (535, 160)])
d.box(535, 118, 200, 108, ["Contested", "~$420M · press · March", "~$460M · analyst · May", "~never averaged"], k="warn")
place(P, "sub:5.6", d,
      "Every claim travels with its source, a supporting excerpt and a date, so the final report can show conflicting "
      "credible figures side by side instead of averaging them away.")
