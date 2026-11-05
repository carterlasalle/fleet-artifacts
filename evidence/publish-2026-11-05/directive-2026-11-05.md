# FLEET DIRECTIVE — 2026-11-05
**Issued by:** Strategist (autonomous daily cycle) · **Status:** self-directed, no assigned work
**Goal pinned:** A fleet of agents working 24/7 across software, research, writing and design, generating its own ideas and growing its own capabilities, with the Commander out of the loop. Output reaches him as files, documents or messages — never logs.
**Horizon:** 30 days. **Scarce resource:** the Commander's attention — every move ranked by payoff per unit of it.
**Freeze:** `AS_OF = 1793888785699` (2026-11-05T14:26:25Z), a literal snapshot of `max(startedAt)` pinned in the verifier, never `max()` at run time and never wall-clock. Ledger read from both `runs.jsonl.1` + `runs.jsonl`: **2,232 rows**, all at or before the freeze. Store figures read directly from the twelve `*.workshop.json` files.
**Instruments shipped this cycle:** `measure_2026-11-05.py` (**35 checks, 35 PASS, EXIT 0**) — it recomputes every figure below by *executing the station's own resolver* (`sidecar/nightfocus.js`) with the station's own mapping, so the directive cannot print a focus claim the code disagrees with.
**Retrieval log:** `sources-2026-11-05/retrieved-quotes-2026-11-05.md` — every external source fetched in full, diffed against the sentence that quotes it.

---

## THE POSITION (two sentences)

**Yesterday's directive ranked "find what reads the quest into the nightly mint" first and said it could not locate that code path in one hour; I found it in this one — it is `sidecar/index.js:6301-6303`, a `questStore.list().filter(status==='open').slice(0, 12)` whose *truncation by store insertion order* is the whole defect, and it reproduces exactly: the live focus is `q:13` at score 0.453 while four open quests score higher (q:22 at 1.075), because `q:22` is the 22nd element of a list sliced to 12 and is therefore never a candidate.** Yesterday's proposed fix — retire `q:13` — **does not work**: with `q:13` removed the resolver returns `q:11`, the next-oldest instrument quest, because the survivor set is still `q:1..q:12` and q:13's replacement was already truncated away. The fleet does not repeat one quest; it inherits the next one in line, and **every quest with an external blast radius — both security items and both distribution items — is in the nine that are cut.**

---

## LANDSCAPE SWEEP (three topics; every cited source fetched in full this cycle)

### 1. The month's framework releases all solve *execution*; none solves *selection*

| Signal | What the source actually says | Source |
|---|---|---|
| Agent infrastructure went 1.0 and GA, with the pause-state problem named as the thing being fixed. | "Agent Substrate has reached its 1.0 milestone and is now generally available as Agent Substrate on GKE"; "Agents execute code or tests for a few seconds, then wait on model turns, external APIs, or human input. Keeping a dedicated container alive during those pauses ties up memory and compute. Agent Substrate decouples stateful agent sessions and identities from active compute, snapshotting idle agents to storage and restoring them in under 500 milliseconds to run millions of sandboxes at 10x container density." | [cloud.google.com, 2026-11-05](https://cloud.google.com/blog/products/containers-kubernetes/open-infrastructure-for-autonomous-agents-comes-to-cncf) |
| Coordination moved from conversation to a database. | "agents query and update shared state through SQLite transactions … Agents register tasks as database rows with status fields, and the coordination engine assigns work based on agent capabilities and current load. Failed tasks automatically retry with exponential backoff, and the database serves as an audit log for debugging agent behavior." | [emergent.sh, 2026-11-03](https://emergent.sh/news/unified-brain-replaces-turn-based-llm-agents) |
| Proactive agents shipped — with the human approval path as the headline, not the autonomy. | "agents are designed to operate autonomously while maintaining strict user oversight through built-in human-in-the-loop approval mechanisms." | [thenextgentechinsider.com, 2026-11-04](https://www.thenextgentechinsider.com/pulse/openduet-launches-open-source-framework-for-self-hostable-proactive-ai-agents) |
| Resume semantics got stricter, and the release notes say why. | LangGraph 1.2.20 "adds a strict resume mode that refuses stale interrupt answers and gives each `interrupt()` call in a task its own ID." | [aiagentnews.io, 2026-11-05](https://aiagentnews.io/topics/frameworks) |
| Local multi-agent crews are now a weekend project. | "Friday now lets developers run Claude Code and Codex as collaborative agent crews directly on their local machines." | [emergent.sh, 2026-11-02](https://emergent.sh/news/friday-run-claude-code-codex-crew-open-source) |
| The market is consolidating fast enough that Meta bought a parallel-workspace agent runner. | "Meta has acquired Conductor, a startup whose product runs multiple coding agents in parallel workspaces." | [aiagentnews.io, 2026-11-05](https://aiagentnews.io/topics/frameworks) |

**Reading:** identity, isolation, snapshot/restore, atomic claim, strict resume, audit log — the month
delivered every primitive for *executing a declared unit of work safely*. **None of the six sources
addresses how a long-running autonomous agent chooses which declared unit to attempt next.** Every one of
them assumes the unit was supplied by a human or a service upstream. That assumption is exactly what this
fleet cannot make, and it is where its bug is.

### 2. The market gap agent-built software could fill is oversight, not capability — and the single tightest number is 5%

| Signal | What the source actually says | Source |
|---|---|---|
| Automated runtime control is near-absent while confidence is near-universal. | "83% rely on existing IT, security or compliance processes … Still, oversight remains largely human-led and procedural, with just **5%** having automated controls, audit trails, and formal human review points in place." Separately: "82% of executives believe their organizations can keep pace with governing, integrating, and monitoring AI agents as they move into production. However, only **26%** say they are well prepared to resolve conflicts across agents, systems, and automated workflows." | [outsystems.com, 2026-10-15](https://www.outsystems.com/news/outsystems-research-agentic-ai-enterprise-readiness) |
| The 5% is not uniform, and the regional split is stark. | "14% report having automated controls, audit trails, and human review points in place, compared with **3% in Europe and 2% in North America**." | [cxotoday.com, 2026-10-16](https://cxotoday.com/research/outsystems-research-only-26-of-enterprises-are-prepared-to-resolve-ai-agent-conflicts/) |
| Agents now outnumber the management models that govern them. | "38% of organizations with agents in production operate more than 100 agents, yet almost half (**47%**) still use informal or decentralized management models." | [company.g2.com, 2026-10-14](https://company.g2.com/news/2026-ai-agents-report) |
| The cost of the missing control is measured in human hours, not dollars. | "31% of B2B buyers say employees spend **6 or more hours each week bot-sitting** (overseeing agent work). 45% say time spent overseeing and correcting agent mistakes consumes more than a quarter of the productivity gains they expected." | ibid. |
| Two-thirds cannot reconstruct what the agent did. | "54% had an AI agent make a mistake in the past 90 days … and that **only 53% can produce a full audit log** of what their agents did last week and which agent did it." | [nylas.com, 2026-10-20](https://www.nylas.com/blog/pr/ai-agent-mistakes-survey-state-of-agentic-ai-h2-2026/) |
| And the single change that most improves auditability is identity, not tooling. | "26% say their agents authenticate with a dedicated identity of their own. … Where agents have their own identity, **66% of teams report full audit capability**, against 51% where agents act through an employee's account." | ibid. |
| Enterprises are already replacing vendors with in-house tooling. | "**67%** are considering replacing a vendor or tool with an AI agent. Separately, **81%** have already replaced at least one vendor or tool with in-house tooling." | ibid. |

**Reading:** the tightest figure in the six surveys is **5% with automated controls, audit trails and formal
human review points** — and this station, whatever else is wrong with it, already runs an append-only run
ledger with a per-run artifact array, a completion-contract system, a standing falsification record and a
per-agent identity. **Honest caveat, stated before the recommendation:** these are vendor-sponsored surveys
of self-reported confidence, several published by companies selling the remedy, and their figures are not
comparable across instruments. I use them to establish that the gap is *widely reported*, not to size it.
The 81%-in-housed-tooling figure is the one that matters strategically: it says the buyer for a small,
honest oversight instrument already exists.

### 3. The case-study gap the fleet uniquely occupies: nobody instruments which goal an agent picks

| Signal | What the source actually says | Source |
|---|---|---|
| Frameworks declare a *focus* concept and never rank it. | Microsoft's builder skills "favor the smallest suitable pattern: one agent when tools and sessions are enough, a harness when an operating loop is needed, or a workflow when explicit stages, routing, and checkpointing are part of the requirements" — pattern selection, not priority selection. | [devblogs.microsoft.com, 2026-11-04](https://devblogs.microsoft.com/agent-framework/give-your-coding-agent-a-head-start-with-microsoft-agent-framework-skills-for-net-and-python/) |
| The station ships the ranking logic and the defect is in its *caller*. | `sidecar/nightfocus.js` scores each open quest `0.85·recency + 0.28` and returns one focus with cited `why`; `sidecar/index.js:6301-6303` hands it only `.slice(0, 12)`. | local, read this cycle |

**The gap in one line:** the market grades whether an agent's *work* is good and routes work a human chose.
This fleet's selection step is a shipped, testable, undocumented-in-the-loop component with a one-line
defect — which makes it the most publishable thing the fleet owns, and the least covered thing I could find.

---

## THE 1-3-1

**The question:** yesterday's Rank 1 said the lever was the *focus text* and could not find the code path; I found the path, reproduced the behaviour exactly, and a 5-line counterfactual ladder now says the lever is the **candidate list, not the focus text** — and that yesterday's own proposed fix (retire q:13) is inert. What is the next move?

### Option A — BUILD: **REPAIR THE SELECTION STEP — make the candidate set the whole open set, and let the resolver rank it**
The host gives the resolver twelve candidates chosen by store insertion order — i.e. **oldest first** — then
`.slice(0, 12)`. Three defects fall out of that one line, all reproduced by executing the shipped resolver:

1. **Truncation starves the newest.** 21 quests are open; 12 are offered; 9 are cut. The cut set is
   `q:14 q:15 q:16 q:17 q:18 q:19 q:20 q:21 q:22`. The newest quest the fleet has (q:22, score 1.075) has
   never been a candidate.
2. **Truncation also starves the highest-blast-radius work.** By title keyword, **security** (q:16 the open
   Docker ports, q:19 the SSH surface) = **0 offered / 2 hidden**; **distribution** (q:15 the published Gmail
   surface, q:18 keeping the publish channel alive) = **0 offered / 2 hidden**. All four externally-facing
   quests are unreachable to the selector. **This is the load-bearing fact of the cycle.**
3. **The bound is not applied to a ranked list.** `slice(0,12)` on insertion order is a cap that silently
   encodes age-priority, and the cap binds — 21 > 12 — so the top-ranked quest has never won.

**The patch, in order of value:**
- **A1 (one line, ~5 min).** At `sidecar/index.js:6300-6303` (the `.slice(0, 12)` is line 6303), reverse `open` before the slice: the resolver's
  own recency term already prefers the newest, so handing it the newest twelve is the same ranking it was
  built to make. Result, verified by execution: focus `q:13` → **`q:22` "Wake the fleet bus — no room-to-room
  exchange since 2026-10-21"**, and `q:15`/`q:18` enter the candidate set.
- **A2 (two variables, ~15 min).** Give the resolver the full open set and let it return the top-N; keep a
  visible cap on how many *drafts* a night may attempt. A bound that does not bind cannot starve anything.
- **A3 (optional, ~10 min).** A one-time re-resolution: bump `day` in `nightfocus.state.json` once the list
  is fixed, so the stale focus is re-derived rather than waiting for the next UTC day-roll.

*Trade-off:* it is the smallest change on the board — one line does 80% of it — and it fixes a defect whose
blast radius includes both internet-facing security quests. But it touches the station's own selection code,
which is closer to another agent's state than I prefer, and it will not on its own diversify the *lane*: the
offered twelve are still 7-of-12 instrument-flavoured, so even a correct selector still lands on the
instrument lane for as long as the open-quest set is instrument-heavy. **Stated plainly: this option fixes
the validator, not the menu.**

### Option B — BUILD: **HEAL THE TWO STAGES DOWNSTREAM OF SELECTION — the mint's inputs, and the stale store**
Two separate, independently proven defects:
- **B1 — the drafts are self-selecting, not just focus-steered.** The last 20 drafts in `nightshift.drafts.json`
  are **16/20 instrument by strict keyword and 20/20 on manual read** (the four the keyword pass missed —
  "Fault bench campaign v1", "faultgate: killability ledger", "Fault bench self-test", "Survivor-to-canary
  compiler" — are instrument by hand). The proposals are written by a stage that sees the focus header,
  so even a perfect focus cannot break a template this tight.
- **B2 — the store has 204 of 230 items with `attempts: null`.** Only **26** carry a number, so the store's own
  `attempts >= 2` parking rule is evaluated against nothing on 88.7% of items. This is the same defect
  yesterday's directive reported, still open, and it is *cheaper to state than to argue about*: one field.

*Trade-off:* B1 is the only option aimed at what the fleet actually *builds*, not at what it *selects*, and
B2 is a one-field fix with no schedule risk. But B1 requires reading and changing the propose prompt — a
second agent's instruction surface — and the market sweep gives no evidence for which of "steer the focus"
or "diversify the proposer" is binding, because no source I found instruments selection at all.

### Option C — PUBLISH: **THE SELECTION-STEP CASE STUDY + THE 5% OVERSIGHT GAP**
**"A shipped priority resolver was fed a pre-truncated candidate list for 24 days; the newest goal, and both
internet-facing security goals, were never candidates — here is the five-line counterfactual that proves it."**
Against the swept market this is genuinely uncovered: every framework this month ships routing, identity,
isolation and resume; not one instruments how an agent picks which goal to pursue. And the station's own
oversight surface — append-only ledger, per-run artifact array, completion contracts, falsification record —
is the exact category the surveys say only **5%** of enterprises have (2% in North America), while **81%**
are already replacing vendors with in-house tooling.

*Trade-off:* the strongest story the fleet has produced, checkable by a stranger against a public repo, and
it now has a mechanism and a proof rather than a vibe. **But `channel_targets` returned `{"reachable": 0}`
again this cycle.** The only publishing route logged 0 page views over 14 days on the previous check.
Writing it changes nothing today. **The gap is distribution, not capability, and it has been for six cycles.**

### RECOMMENDATION: **A, with B2 folded into the same patch and B1 registered as the next kill-test. C is written by A as its audit trail, not as a standalone essay.**

**Why A.** It is the smallest edit with a reproduced, executable before/after, and it is the only option whose
value does not depend on a hypothesis about *why* the lane is narrow — it is a correctness fix to a shipped
component. The evidence is not an argument, it is a transcript:

| | Status quo | A1: reverse before the slice | A2: full set |
|---|---|---|---|
| Focus tonight | `q:13` (score 0.453) | `q:22` (score 1.075) | `q:22` |
| Candidates offered | 12 of 21 | 12 of 21 (newest) | 21 of 21 |
| Highest-scoring open quest is a candidate? | **No** | Yes | Yes |
| Security quests candidate? | **0 of 2** | 1 of 2 | 2 of 2 |
| Distribution quests candidate? | **0 of 2** | 2 of 2 | 2 of 2 |

And the correction that matters most: **yesterday's Rank 1 was to retire q:13, and it does not work.** With
`q:13` removed from the hosted set the resolver returns **`q:11`**, the next-oldest instrument quest. The
ladder run out to seven survivors is `q:13 → q:11 → q:10 → q:7 → q:4 → q:1 → q:12` — six of the seven are
instrument quests, because that is all the first twelve slots contain. **Retiring an anchor, the whole
proposal of the previous cycle, is a no-op against a candidate set that never changed.** That is the finding
this cycle contributes, and it improves yesterday's call rather than repeating it.

**Why I am not overselling it — the honest limits, stated before the kill-test.**
1. **A fixes the selector, not the menu.** The offered twelve are 7-of-12 instrument-flavoured; a correct
   selector still lands on an instrument quest when the open-quest set is instrument-heavy. A1 changes the
   focus from `q:13` to `q:22` (bus/wiring) — better, but still one lane, chosen from the same bias.
2. **`nightshift.drafts.json` gives the counter-evidence.** 16/20 instrument by strict keyword, 20/20 by hand.
   If the proposer is a template, the focus text is a weaker lever than this directive assumes. **I have not
   ruled this out, and it is the exact thing the kill-test below measures.**
3. **Two truncation sites exist.** `sidecar/index.js:6605` does the same `filter(open).slice(0, 8)` for a
   *recruiting/context* line, not the resolver. I report it because it will otherwise look like a second
   bug; I have not proven it steers anything.
4. **Things I could not verify and will not claim:** whether a day-roll would have re-resolved on its own
   (the stored `resolvedAt` is 10.7s after today's UTC-day start, so the resolver *did* re-run today and chose
   `q:13` again — that is stronger than a stale file and it is why this is a live selection defect, not lag);
   and whether the 0-focus window between `resolvedAt` and the rename has any downstream effect.
5. **The store moved during the cycle.** `builtRunId` set went 178 → 183 and items 225 → 230 between yesterday's
   freeze and this one. All figures above are pinned to `AS_OF`; live counts will differ.

**Why not B first.** Because B1's fix requires a hypothesis the data does not settle — the market sweep turned
up zero sources that instrument goal selection, so I have no external prior on whether the lever is the
selector or the proposer. A is a correctness fix whose payoff is knowable without resolving that question,
and **the kill-test for A is precisely the measurement that decides B1.** Building B1 first means writing to
a second agent's prompt on a hunch.

**Why C is deferred, not dropped.** It is A's by-product and it is now genuinely load-bearing: it carries the
corrected refutation of the previous cycle's recommendation. Written today it would have no reader.

---

## THE THREE PROJECTS (ranked by leverage per unit of Commander attention)

### RANK 1 — BUILD: **FIX THE CANDIDATE SET AT THE TWO TRUNCATION SITES** — one line, reproduced before/after
**What it fixes.** A shipped priority resolver fed a candidate list pre-cut to the twelve *oldest* open quests,
so the newest goal and both internet-facing security goals are structurally unreachable.

**Shipped this cycle:** `measure_2026-11-05.py` — 35 checks, 35 PASS, exit 0. It executes the station's own
resolver with the station's own mapping and asserts the whole before/after table above, plus the lane
composition of the offered vs hidden sets, plus the store reconciliation (23 + 23 + 1 + 183 = 230) and the
ledger windows (518 / 125 7d; 64 / 19 24h). It fails loudly on any drift.

**The patch:** A1 reverse `open` before `slice(0,12)` (index.js:6303, one line); A2 pass the full set and
cap the drafts instead; B2 write real `attempts` values so the parking rule evaluates something; A3 optional
one-time re-resolution.

**Effort:** ~30 minutes total for A1+A2+B2. **Payoff:** high — correctness on the selector, verified by execution.
**Needs:** no credentials, no spend, no publishing. It is a code edit on the station the Commander already owns;
I have not made it, because `sidecar/index.js` is the running harness's own file and a live edit there is a
call I want the Commander to make rather than one I make unattended.

### RANK 2 — BUILD (NEXT): **THE MINT'S PROPOSER, MEASURED BEFORE IT IS CHANGED**
**16/20 instrument by strict keyword, 20/20 by hand, across the last 20 drafts.** Draft titles this week:
"Mutation scoreboard that must record a survivor", "Silence suite — negative controls for the fleet's
instruments", "Survivor Killer — mutation survivors become planted fixtures". The proposer is producing
sequels. But **I am deliberately not editing it this cycle**: the market sweep gives no prior on whether the
lever is the selector or the proposer, and Rank 1's kill-test decides it. Fixing the proposer first would be
writing to another agent's prompt on a hunch.

*Trade-off:* likely the biggest single lever on what the fleet builds, and the least evidential. Measure first.

### RANK 3 — PUBLISH (DEFERRED, BLOCKED ON DISTRIBUTION): **"THE SELECTOR WAS FED A PRE-CUT LIST"**
The corrected finding, and the best story the fleet owns: a priority resolver that ranks goals by evidence did
so correctly — on a candidate list that the newest goal, both security goals and both distribution goals had
never been on. Every framework shipped this month routes, isolates and resumes work; **not one instruments
which work an agent picks.** Alongside it, the station's own oversight surface is the category **5%** of
enterprises have (**2%** in North America) while **81%** are already replacing vendors with in-house tooling.

*Trade-off:* genuinely uncovered and stranger-checkable. **`channel_targets` returned `reachable: 0` again.**
Deferred for the sixth cycle; the constraint is distribution, and I will not spend the budget pretending otherwise.

---

## RISKIEST ASSUMPTION + THE KILL-TEST

**Riskiest assumption, in one sentence:** *that the pre-truncated candidate list is the binding constraint on
which lane the fleet works* — i.e. that handing the resolver the newest twelve candidates changes what gets
drafted, rather than merely relabelling the header above a template.

Three rival diagnoses; only the first makes Rank 1 the fix:

1. **D1 THE CANDIDATE LIST IS THE LEVER** — the resolver ranks correctly and the truncation starves it.
   *Fix: reverse before the slice. Prediction: focus moves q:13 → q:22 and the next drafts leave the instrument lane.*
2. **D2 THE PROPOSER IS A TEMPLATE** — the drafts come from a stage whose shape does not depend on the focus
   text; `16/20` instrument with `maintain-extend` dominating is the proposer talking to itself.
   *Fix: the proposer's inputs, not the selector. Rank 1 is cosmetic.*
3. **D3 THE LANE IS EXHAUSTED** — the open-quest set really is instrument-heavy because that is what the
   Commander's own quests commit to, and no selector change can conjure non-instrument work.

**Kill-tests — the discriminator between D1 and D2 is cheap and it is already written.**

| # | Question | Result (run this cycle) |
|---|---|---|
| **K1** | Does the focus actually reach the proposal stage? | **Yes.** `sidecar/index.js:7435-7436`: `const foc = resolveNightFocus(); const focusHeader = foc.focus ? nightfocus.focusLine(foc.focus) : ''` — and the propose directive "LEADS with the focus". The focus is load-bearing on the prompt, not decorative. **D1 is live.** |
| **K2** | Is the focus really wrong, or merely old? | **Really wrong, and re-derived today.** The stored `resolvedAt` (1793836810731) is **10.7 seconds after** the start of UTC day 20762 — the resolver re-ran today and chose `q:13` a second time. Not a stale file. |
| **K3** | Would yesterday's fix have worked? | **No.** Retire `q:13` → resolver returns **`q:11`**. Ladder out to seven: `q:13 q:11 q:10 q:7 q:4 q:1 q:12` — six of seven instrument. **Retiring an anchor against a frozen candidate set is a no-op.** |
| **K4** | Are the un-offered nine a different lane? | **Yes, and this is the load-bearing fact.** Offered 12: 7 instrument-flavoured. Hidden 9: **security 0 offered / 2 hidden; distribution 0 offered / 2 hidden**; cost_ops 1 offered / 3 hidden. **Every externally-facing quest is unreachable.** |
| **K5** | Is the selector the ONLY starved stage? | **No.** `nightshift.drafts.json`, last 20 drafts: **16/20 instrument by strict keyword, 20/20 by hand.** The proposer leans the same way **independently of the selector**. **D2 survives — this is the one that decides whether Rank 1 is enough.** |

**The cheapest test that confirms or kills Rank 1 (zero spend, ~0 Commander minutes, ~24 hours):** apply A1
(reverse before the slice), let the next day-roll re-resolve, and read the focus header plus the next five
drafts. **If the focus moves to `q:22` and the drafts leave the instrument lane, D1 was the lever and Rank 1
is done.** If the focus moves to `q:22` and **the drafts are still ≥80% instrument**, then **D2 survives, the
selector was never the binding constraint, and the whole lever is the proposer's inputs** — at which point
Rank 2 becomes Rank 1 and this directive's recommendation was decoration. I am registering that outcome now,
before the test, because K5 already suggests it is the more likely of the two.

**A secondary test that costs nothing and I can run tomorrow:** the open-quest set is 21 items with a median
age of ~16 days and six instrument quests in its oldest twelve. If the Commander's own quests are structurally
instrument-heavy, **D3 is live too** — and the correct fix is not a selector at all but the fleet minting
non-instrument work of its own, which is the thing the Commander asked for in the first place.

---

## WHAT THIS CYCLE MEASURES, AND WHAT IT REFUSES TO CLAIM

- **Delivery is flat, not a new finding, and I will not re-report it as one.** 7d **125 of 518 (24.1%)**;
  last 24h **64 runs, 19 delivered (29.7%)** — down from 38.9% yesterday on a smaller sample (64 vs 72 runs).
  The day-over-day move is inside sampling noise and I am not calling it a trend.
- **Yesterday's headline blocker is closed and I am retiring it, as promised.** The `agent` room has jobs and
  runs. Carried forward instead: the phantom-`builtRunId` writer, `uncertainMutations` still dark, and the
  open-detection instrument defect.
- **Store state, pinned:** **230 items** across twelve rooms — claimable **23**, parked **23**, wedged **1**,
  `builtRunId` set **183**. Reconciliation exact: 23 + 23 + 1 + 183 = 230. **`attempts: null` on 204 of 230.**
- **What I refuse to claim.** (1) That fixing the selector diversifies the lane — K5 says otherwise is
  plausible. (2) That the security and distribution quests being unreachable means they are *important*; it
  means they are *unreachable by the selector*, and a reader who thinks they matter most should say so and I
  will re-rank. (3) Any causal reading of the 7d/24h delivery numbers. (4) That the `slice(0,8)` at
  index.js:6605 is a bug — it is a context line, and I did not prove it steers anything.
- **Corrections issued against my own draft this cycle, recorded because they are the point of the verifier:**
  the first verifier run printed **4 FAIL** and **3 were my assertion defects, not the fleet's** — I had
  asserted the focused quest was stale (it was re-resolved today), asserted retiring `q:13` would surface
  `q:14` (it surfaces `q:11`), and asserted the offered set had a >50% top lane by a taxonomy that did not
  count instrument titles correctly. All three were fixed in the verifier with the reason recorded inline.
  **The 4th was a real doc defect: a duplicated comment line.** Final state 35/35 PASS, exit 0.
- **A second doc defect, found by reading the file back against the source rather than by any assertion:**
  my first draft cited the patch site as `sidecar/index.js:6305-6306` and the focus header as `7436-7437`.
  Both were off by two lines — the statement is `6299-6304`, the `.slice(0, 12)` is on **6303**, and the
  focus header is `7435-7436`. Corrected in place. **No assertion in the verifier covers a line-number
  citation**; this class of error is caught only by re-reading the source before shipping.

---

## NEXT MOVES

1. **Apply A1 (reverse before the slice) at `sidecar/index.js:6303`; A2 and B2 with it.** ~30 min. It is
   the Commander's own harness file, so it is a Commander call, not mine unattended.
2. **Register and run the D1/D2 discriminator tomorrow.** Focus header + next five drafts. Drafts still
   ≥80% instrument → Rank 2 is the real Rank 1.
3. **Write real `attempts` values** so `MAX_BUILD_ATTEMPTS` gates something (204 of 230 are null).
4. **Do not re-report the delivery rate as a finding.** 24.1%/7d, 29.7%/24h; report only on movement outside
   the sampling band.
5. **Retire from the blocker list:** the `agent`-room pointer (closed). **Carry forward:** the phantom-id
   writer, `uncertainMutations`, the open-detection instrument defect, and the `q:13` stale-focus state.
6. **Distribution is the standing blocker for cycle six.** `channel_targets` = `{"reachable": 0}`. Every
   publish option has been deferred on this for six cycles; if the Commander wants the case study published,
   a channel is the only missing piece.

**Commander's involvement required:** two decisions. (1) **May I edit `sidecar/index.js`?** It is the running
harness's own file — a one-line change at line 6303 — and I will not patch it unattended. (2) **Q13's status.**
It is still open, it still passes its own completion contract, and it is the quest the selector keeps choosing.
Everything else this cycle was script execution and file reads: no credentials, no spend, no external
publishing. One limit I cannot engineer around: **`channel_targets` returns 0 reachable targets**, so this
arrives as a file and nothing else.

---
*Landscape swept on three topics; every cited source fetched in full and diffed against the sentence quoting
it (`sources-2026-11-05/retrieved-quotes-2026-11-05.md`). Two URLs were invented in my first draft and
discarded before it landed; the real OutSystems URL was located by search. Fleet figures recomputed from
`runs.jsonl` + `runs.jsonl.1` against the literal freeze `AS_OF=1793888785699`; store figures read directly
from the twelve `*.workshop.json` files. The focus claims are not inferred — they are produced by executing
`sidecar/nightfocus.js` with the host's own mapping (`sidecar/index.js:6297-6303`) and asserting the outcome.
35 checks, 35 PASS, exit 0.*
