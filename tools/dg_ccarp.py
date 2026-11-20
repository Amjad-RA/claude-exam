"""Diagrams for exams/ccar-p.html (Claude Certified Architect – Professional)."""
from dglib import Diagram, place

P = "exams/ccar-p.html"

# 1.2 Who executes tools ---------------------------------------------------------
d = Diagram("ap-exec", 760, 256, "Client tools run in your application; server tools run inside the Anthropic API")
d.box(10, 10, 250, 236, [], k="frame")
d.text(24, 32, ["Your application"])
d.text(30, 92, ["~you run these, return tool_result"])
d.box(30, 110, 210, 48, ["Your custom tools"])
d.box(30, 170, 210, 56, ["bash · text_editor", "~computer: Anthropic schema"])
d.box(500, 10, 250, 236, [], k="frame")
d.text(514, 32, ["Anthropic API"])
d.box(520, 50, 210, 44, ["Claude"], k="a")
d.box(520, 150, 210, 56, ["web_search · web_fetch", "~code_execution · tool_search"], k="a")
d.ln([(600, 94), (600, 150)], k="a")
d.ln([(650, 150), (650, 94)], k="a")
d.lab(606, 126, "runs here", anchor="start")
d.text(625, 228, ["~loop cap hit → pause_turn: resend"], anchor="middle")
d.ln([(260, 64), (500, 64)], lab="request", at=(380, 56))
d.ln([(500, 104), (260, 104)], lab="tool_use (client tool)", at=(380, 96))
d.ln([(260, 144), (500, 144)], lab="tool_result", at=(380, 136))
place(P, "sub:1.2", d,
      "Who runs a tool decides who writes the loop. Client tools, including Anthropic-defined bash, text_editor and "
      "computer, run in your code; only server tools run inside the API, which returns pause_turn when its own loop "
      "hits the cap.")

# 1.3 The six patterns -----------------------------------------------------------
d = Diagram("ap-patterns", 780, 380, "Six patterns: prompt chaining, routing, sectioning, voting, orchestrator-workers, evaluator-optimizer", minw=640)


def node(x, y, w, label, k=""):
    d.box(x, y - 13, w, 26, ["^" + label], k=k, rx=6)


def io(x, y, label):
    d.circle(x, y, 13, ["~" + label], k="dash")


panels = ((0, 0, "Prompt chaining", "fixed steps, code gates"),
          (260, 0, "Routing", "one tuned path per category"),
          (520, 0, "Parallel: sectioning", "different tasks at once"),
          (0, 190, "Parallel: voting", "same task, several runs"),
          (260, 190, "Orchestrator-workers", "subtasks chosen at run time"),
          (520, 190, "Evaluator-optimizer", "LLM critique, then revise"))
for x0, y0, title, note in panels:
    d.box(x0 + 6, y0 + 6, 248, 178, [], k="frame")
    d.text(x0 + 18, y0 + 26, [title])
    d.text(x0 + 130, y0 + 168, ["~" + note], anchor="middle")

cy = 96  # prompt chaining
io(30, cy, "in")
node(56, cy, 58, "LLM 1", "a")
d.ln([(43, cy), (56, cy)])
d.ln([(114, cy), (122, cy)])
d.circle(134, cy, 11, ["✓"], k="ok")
d.ln([(145, cy), (154, cy)])
node(154, cy, 58, "LLM 2", "a")
d.ln([(212, cy), (221, cy)])
io(234, cy, "out")

x0 = 260  # routing
io(x0 + 24, cy, "in")
node(x0 + 46, cy, 66, "Router", "a")
d.ln([(x0 + 37, cy), (x0 + 46, cy)])
for dy, lab in ((-40, "billing"), (0, "bugs"), (40, "cancel")):
    node(x0 + 136, cy + dy, 62, lab)
    d.ln([(x0 + 112, cy), (x0 + 136, cy + dy)])
    d.ln([(x0 + 198, cy + dy), (x0 + 219, cy + dy // 8)])
io(x0 + 232, cy, "out")

for x0, y0, labels, merge in ((520, 0, ("vulns", "licence", "style"), "Merge"),
                              (0, 190, ("run 1", "run 2", "run 3"), "Vote")):
    c = y0 + cy
    io(x0 + 24, c, "in")
    for dy, lab in zip((-40, 0, 40), labels):
        node(x0 + 54, c + dy, 64, lab, "a")
        d.ln([(x0 + 37, c), (x0 + 54, c + dy)])
        d.ln([(x0 + 118, c + dy), (x0 + 146, c + dy // 5)])
    node(x0 + 146, c, 58, merge)
    d.ln([(x0 + 204, c), (x0 + 219, c)])
    io(x0 + 232, c, "out")

x0, y0 = 260, 190  # orchestrator-workers
io(x0 + 26, y0 + 56, "in")
node(x0 + 72, y0 + 56, 116, "Orchestrator", "a")
d.ln([(x0 + 39, y0 + 56), (x0 + 72, y0 + 56)])
for wx in (x0 + 40, x0 + 102, x0 + 164):
    d.box(wx, y0 + 88, 56, 24, ["^worker"], k="dash", rx=6)
    d.ln([(x0 + 130, y0 + 69), (wx + 28, y0 + 88)])
    d.ln([(wx + 28, y0 + 112), (x0 + 130 + (wx - x0 - 102) // 3, y0 + 128)])
node(x0 + 76, y0 + 141, 108, "Synthesizer")
d.ln([(x0 + 184, y0 + 141), (x0 + 213, y0 + 141)])
io(x0 + 226, y0 + 141, "out")

x0, y0 = 520, 190  # evaluator-optimizer
io(x0 + 26, y0 + 70, "in")
node(x0 + 52, y0 + 70, 100, "Generator", "a")
node(x0 + 52, y0 + 122, 100, "Evaluator")
d.ln([(x0 + 39, y0 + 70), (x0 + 52, y0 + 70)])
d.ln([(x0 + 124, y0 + 83), (x0 + 124, y0 + 109)])
d.ln([(x0 + 80, y0 + 109), (x0 + 80, y0 + 83)], k="a")
d.lab(x0 + 74, y0 + 100, "feedback", anchor="end")
d.ln([(x0 + 152, y0 + 122), (x0 + 213, y0 + 122)], k="ok", lab="pass", at=(x0 + 182, y0 + 116))
io(x0 + 226, y0 + 122, "out")
place(P, 're:<p>Everything is built from the <b>augmented LLM</b>.*?</p>', d,
      "The six building blocks, each made of augmented LLM calls. In the first four your code fixes the path; in "
      "orchestrator-workers the model chooses the subtasks at run time; evaluator-optimizer loops until an LLM judge "
      "passes the output.")

# 2.4 Context budget -------------------------------------------------------------
d = Diagram("ap-budget", 760, 240, "One context window shared by system prompt, tools, history, tool results, thinking and output")
d.text(20, 20, ["One context window (not to scale)"])
segs = ((20, 96, "System", "a"), (116, 120, "Tools", "a"), (236, 190, "History", "a"),
        (426, 140, "Tool results", ""), (566, 80, "Thinking", ""), (646, 94, "Output", ""))
for x, w, name, k in segs:
    d.box(x, 70, w, 44, [name], k=k, rx=0)
d.ln([(20, 64), (20, 52), (426, 52), (426, 64)], head=False)
d.lab(223, 44, "cached prefix: cheaper, still takes space")
d.ln([(744, 40), (744, 132)], k="bad", head=False)
d.lab(740, 148, "window limit", anchor="end")
d.box(20, 170, 230, 60, ["Input > window", "~400 error"], k="bad")
d.box(265, 170, 230, 60, ["Input + max_tokens > window", "~accepted; may stop early"], k="warn")
d.box(510, 170, 230, 60, ["Measure it", "~count_tokens · usage fields"])
place(P, "sub:2.4", d,
      "Everything in a request draws on one budget: system prompt, tool definitions, history, tool results, thinking "
      "and output. Caching changes the price of the prefix, not the space it takes.")

# 2.5 Cache prefix and invalidation ----------------------------------------------
d = Diagram("ap-cache", 760, 256, "Prompt cache prefix of tools, system and messages, with what each change invalidates")
d.box(20, 56, 110, 40, ["Tools"], k="a", rx=4)
d.box(134, 56, 110, 40, ["System"], k="a", rx=4)
for i in range(8):
    d.box(248 + i * 62, 56, 58, 40, [f"^m{i + 1}"], rx=4)
d.tri(244, 50)
d.tri(740, 50)
d.lab(740, 22, "▼ cache_control breakpoint (up to 4, free)", anchor="end")
d.box(20, 116, 720, 24, ["^Edit tool definitions → everything is re-processed"], k="bad", align="start", rx=4)
d.box(134, 148, 606, 24, ["^Edit the system prompt → system + messages"], k="warn", align="start", rx=4)
d.box(248, 180, 492, 24, ["^Change tool_choice → messages only"], k="warn", align="start", rx=4)
d.text(20, 232, ["^Lookback: up to 20 blocks back from a breakpoint, so long chats need another breakpoint"])
place(P, "sub:2.5", d,
      "Caching reuses a byte-identical prefix. Invalidation cascades from tools to system to messages, so order content "
      "from most to least stable and put variables last.")

# 3.2 MCP OAuth sequence (replaces the text flow) --------------------------------
d = Diagram("ap-oauth", 760, 350, "Sequence diagram: MCP authorization discovery, token issue, use and step-up")
for cx, name in ((110, "MCP client"), (380, "MCP server"), (650, "Auth server")):
    d.box(cx - 80, 10, 160, 36, [name], k="a")
    d.ln([(cx, 46), (cx, 340)], k="d", head=False)
msgs = ((76, 110, 380, "1 · request, no token", ""),
        (106, 380, 110, "2 · 401 + resource_metadata, scope", "bad"),
        (136, 110, 380, "3 · fetch protected-resource metadata", ""),
        (166, 110, 650, "4 · read AS metadata, register the client", ""),
        (196, 110, 650, "5 · authorize (scopes)", ""),
        (226, 650, 110, "6 · token, audience = this MCP server", "a"),
        (256, 110, 380, "7 · request + token → 200", "ok"),
        (286, 380, 110, "8 · 403 → step up: old ∪ new scopes", "bad"))
for y, x1, x2, label, k in msgs:
    d.ln([(x1, y), (x2, y)], k=k, lab=label, at=((x1 + x2) / 2, y - 6))
d.ln([(380, 322), (430, 322)], k="d bad")
d.box(430, 304, 200, 36, ["Never forward the token"], k="bad")
place(P, "sub:3.2", d,
      "Discovery starts from a 401 that points to the server's metadata. The token is bound to one MCP server's "
      "canonical URI; a 403 means step up to more scopes, and the server never passes the token on to another service.",
      mode="replace_next")

# 3.5 Contextual retrieval pipeline ---------------------------------------------
d = Diagram("ap-rag", 760, 300, "Contextual retrieval pipeline: ingest with chunk context into embeddings and BM25, then hybrid search")
d.text(20, 20, ["Ingest, once"])
d.text(560, 20, ["Each query"])
d.box(20, 36, 230, 40, ["Document"])
d.ln([(135, 76), (135, 96)])
d.box(20, 96, 230, 40, ["Chunks"])
d.ln([(135, 136), (135, 156)])
d.box(20, 156, 230, 52, ["Claude writes context", "~per chunk · document cached"], k="a")
d.ln([(135, 208), (135, 228)])
d.box(20, 228, 230, 40, ["Context + chunk"])
d.box(320, 100, 172, 120, [], k="frame")
d.box(328, 108, 156, 50, ["Embeddings", "~input_type=document"])
d.box(328, 164, 156, 50, ["BM25 index", "~exact terms"])
d.ln([(250, 248), (320, 190)], lab="same text to both", at=(300, 250), anchor="start")
d.box(560, 36, 190, 52, ["Query", "~input_type=query"])
d.ln([(560, 62), (406, 62), (406, 100)], lab="search both", at=(483, 54))
d.ln([(492, 160), (560, 160)])
d.box(560, 134, 190, 52, ["Hybrid merge", "~weights tuned to data"], k="a")
d.ln([(655, 186), (655, 228)])
d.box(560, 228, 190, 48, ["Top chunks → Claude"], k="ok")
place(P, "sub:3.5", d,
      "Claude writes a short context for each chunk; the same contextual text is embedded and indexed for BM25. Each "
      "query searches both indexes and a hybrid merge picks the chunks Claude answers from.")

# 3.6 Retrieval decision ---------------------------------------------------------
d = Diagram("ap-retrieval", 760, 310, "Decision: put the corpus in the prompt, or choose BM25, embeddings, hybrid or live search")
d.dia(110, 70, 200, 90, ["Corpus under", "200K tokens?"])
d.ln([(210, 70), (290, 70)], k="ok", lab="yes")
d.box(290, 46, 250, 48, ["Put it in the prompt", "~+ prompt caching, no RAG"], k="ok")
d.ln([(110, 115), (110, 155)], lab="no", at=(118, 138), anchor="start")
d.dia(110, 200, 170, 90, ["How do", "people ask?"])
for y, label in ((136, "Exact IDs, error codes → BM25"), (180, "Meaning, paraphrase → embeddings"),
                 (224, "Mixed traffic → hybrid blend"), (268, "Changes fast → agent searches live")):
    d.ln([(195, 200), (300, y + 17)])
    d.box(300, y, 300, 34, [label], k="a")
place(P, "sub:3.6", d,
      "Pick retrieval from the data and the queries. A corpus that fits goes straight into the prompt with caching; "
      "otherwise BM25 handles exact identifiers, embeddings handle meaning, and hybrid search blends both.")

# 3.8 Tool search ----------------------------------------------------------------
d = Diagram("ap-toolsearch", 760, 186, "Context used by loading every tool definition compared with tool search")
d.text(20, 56, ["Load every tool"])
d.box(200, 40, 520, 32, ["^≈55K tokens of definitions, every request"], k="bad", rx=4)
d.text(20, 116, ["Tool search"])
d.box(200, 100, 78, 32, [], k="a", rx=4)
d.text(290, 116, ["^search tool + the 3–5 definitions a request needs"])
d.text(20, 166, ["~Selection accuracy slips at around 30–50 loaded tools. Under ~10 small, always-used tools: load them all."])
place(P, "sub:3.8", d,
      "Tool search keeps a search tool in context and pulls in only the definitions a request needs, cutting tool "
      "context by over 85% in this example. Every full definition is still sent with the request.")

# 4.6 Trace ----------------------------------------------------------------------
d = Diagram("ap-trace", 760, 272, "Illustrative trace of one agent turn with spans for model requests, tools and a subagent")
rows = ((24, "Turn", 200, 740, "a", 20), (58, "Model request", 200, 300, "ok", 20), (92, "Tool: Grep", 300, 345, "warn", 20),
        (126, "Subagent: explore", 345, 600, "a", 20), (160, "└ model request", 360, 430, "ok", 36),
        (194, "└ tool: Read", 430, 590, "warn", 36), (228, "Model request (answer)", 600, 740, "ok", 20))
for y, label, x1, x2, k, lx in rows:
    d.text(lx, y + 10, ["^" + label])
    d.box(x1, y, x2 - x1, 20, [], k=k, rx=3)
d.lab(740, 266, "time →", anchor="end")
place(P, "sub:4.6", d,
      "Illustrative trace of one agent turn: a parent span with child spans for model requests, tools and a subagent "
      "with its own children. It shows where time and tokens went, which a flat list of API calls cannot.")

# 5.1 Trust boundaries -----------------------------------------------------------
d = Diagram("ap-trust", 760, 262, "Three input channels, their adversary, and the guard for each")
srcs = ((20, ["System prompt", "~operator: trusted"], "ok", ["Hardened rules", "~+ untrusted-content policy"]),
        (106, ["User message", "~may be an attacker"], "warn", ["Haiku pre-screen", "~is_harmful verdict, validation"]),
        (192, ["Web page, email, file", "~third-party content"], "bad", ["Inside tool_result only", "~as a JSON-encoded string"]))
for (y, src, k, guard), ty in zip(srcs, (116, 134, 152)):
    d.box(50, y, 210, 56, src, k=k)
    d.ln([(260, y + 28), (300, y + 28)])
    d.box(300, y, 230, 56, guard)
    d.ln([(530, y + 28), (580, ty)])
d.box(580, 96, 170, 76, ["Claude"], k="a")
d.ln([(50, 212), (26, 212), (26, 48), (50, 48)], k="d bad")
d.xmark(26, 140)
place(P, "sub:5.1", d,
      "Pick guards by who the adversary is. Users get a cheap pre-screen and repeat-offender handling; third-party "
      "content enters only as JSON-encoded tool_result data, never through the system prompt, which carries operator "
      "authority.")

# 5.3 Permission pipeline (replaces the text flow) ------------------------------
d = Diagram("ap-perms", 860, 214, "Permission pipeline: hooks, deny rules, ask rules, mode, allow rules, canUseTool", minw=700)
steps = (["1 Hooks", "~allow · deny · ask"], ["2 Deny rules", "~blocks"], ["3 Ask rules", "~asks"],
         ["4 Mode", "~per mode"], ["5 Allow rules", "~approves"], ["6 canUseTool", "~a person"])
exits = ((["^decides first", "~holds under bypass"], "a"), (["^blocked", "~nothing lifts it"], "bad"),
         (["^prompt the user"], "warn"),
         (["^bypass: approve", "~acceptEdits: files", "~plan: edits → 6"], ""),
         (["^tool approved", "~bare entry: all calls"], "ok"),
         (["^person decides", "~dontAsk: denied"], ""))
for i, (lines, (ex, k)) in enumerate(zip(steps, exits)):
    x = 10 + i * 140
    d.box(x, 34, 128, 54, lines, k="a" if i in (0, 5) else "")
    d.ln([(x + 64, 88), (x + 64, 124)])
    d.box(x, 124, 128, 70, ex, k=k)
    if i < 5:
        d.ln([(x + 128, 61), (x + 140, 61)])
d.text(430, 16, ["~undecided calls move right; the first step that decides settles the call"], anchor="middle")
place(P, "sub:5.3", d,
      "Every tool call walks this pipeline and the first step that decides settles it. A person is asked only if "
      "nothing earlier approved or denied the call; hooks and deny rules still apply under bypassPermissions, and "
      "dontAsk turns the last step into a denial.", mode="replace_next")

# 5.4 HIPAA vs ZDR ---------------------------------------------------------------
d = Diagram("ap-hipaa", 760, 236, "The same request with an ineligible feature is rejected under HIPAA readiness and accepted under ZDR")
d.box(20, 86, 200, 56, ["Ineligible feature", "~used in a request"])
d.ln([(220, 104), (290, 52)])
d.ln([(220, 124), (290, 178)])
d.box(290, 24, 180, 56, ["HIPAA-ready org", "~BAA + eligible only"], k="a")
d.box(290, 150, 180, 56, ["ZDR org", "~zero data retention"], k="a")
d.ln([(470, 52), (540, 52)], k="bad")
d.ln([(470, 178), (540, 178)])
d.box(540, 24, 210, 56, ["Rejected: 400", "~the API refuses it"], k="bad")
d.box(540, 150, 210, 56, ["Accepted", "~feature's own retention"], k="warn")
d.text(380, 226, ["~HIPAA readiness is permanent · Covered Model under ZDR: 30-day retention in one workspace"], anchor="middle")
place(P, "re:<tr><th>Amazon Bedrock, Google Cloud Agent Platform</th>.*?</table></div>", d,
      "The same request meets two different guards. HIPAA readiness makes the API reject features outside the BAA; "
      "zero data retention lets the request through, and that feature's own retention applies.")

# 7.1 Settings: scalar wins vs arrays merge --------------------------------------
d = Diagram("ap-settings", 760, 230, "Single-value settings take the highest scope; permission arrays merge and deny is checked first")
d.text(20, 20, ["One value: highest scope wins"])
for y, label, k in ((36, "managed: not set", "dash"), (78, "local: model = opus   ✓ wins", "ok"),
                    (120, "project: model = sonnet", ""), (162, "user: model = haiku", "")):
    d.box(20, y, 300, 36, ["^" + label], k=k, align="start")
d.text(400, 20, ["Permission rules: merged"])
d.box(400, 36, 170, 48, ["project", "`deny Bash(aws *)"], k="bad")
d.box(400, 110, 170, 48, ["local", "`allow Bash(aws s3 ls)"], k="ok")
d.ln([(570, 60), (600, 84)])
d.ln([(570, 134), (600, 110)])
d.box(600, 60, 150, 74, ["Merged set", "~checked deny → ask", "~→ allow"])
d.ln([(675, 134), (675, 168)], k="bad")
d.box(600, 168, 150, 48, ["`aws s3 ls", "~blocked"], k="bad")
place(P, "sub:7.1", d,
      "Single-value keys take the highest scope that sets them. Permission arrays merge across scopes and are checked "
      "deny first, so a narrow local allow cannot carve an exception out of a project deny.")
