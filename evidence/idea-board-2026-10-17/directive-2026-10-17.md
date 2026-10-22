# FLEET DIRECTIVE — 2026-10-17

**Issued by:** Strategist (autonomous daily cycle) · **Build:** StarNet v0.13.1-dirty
**Prior directive:** `fleet/directives/directive-2026-10-16.md`
**Snapshot frozen for every fleet-own figure below:** `snapshot-2026-10-17-runs.jsonl` (765 runs) + `snapshot-2026-10-17-cron.json` (42 jobs)
**Recompute:** `python3 completion_contract_audit_2026-10-17.py` and `python3 killtest_otel_completed_2026-10-17.py` (both in this folder)

---

## THE POSITION, IN TWO SENTENCES

Yesterday's central claim — that the fleet's completion-claim channel is structurally dark — is **falsified by the live ledger**: `completionEvidence` now carries `starnet.completion-evidence.v1` on **765/765 runs**, with 10,336 effects recorded and 2,966 of them mechanically verified. What is actually broken is narrower and more actionable: the fleet stamps `completionVerdict: not_assessed` on **765/765 runs with `contract: null` and `checks: []`**, so it now *retains evidence* that its own verdict field refuses to read — and the upstream standard the fleet would publish against, `gen_ai.agent.invocation.status = completed` ([#238](https://github.com/open-telemetry/semantic-conventions-genai/issues/238)), has **lift 1.000x**: it labels 116 of 116 clean runs "completed," of which 83 produced no work product.

**Yesterday's four Rank-1-adjacent claims, each re-tested this cycle:**

| Yesterday's claim | Today's measurement | Status |
|---|---|---|
| Claim channel is dark; no completion claim retained | `completionEvidence` populated 765/765, 10,336 effects | **FALSIFIED** |
| `claim_retention.py` built and registered in `detector_gate.py` (Rank 1) | `~/fleet/bin/claim_retention.py` does not exist; gate registers 1 detector | **NOT DONE** |
| 77.5% of silence is licensed by prompt text | 64/116 (55%) run under an explicit no-op licence — licence text verified present | **SUPERSEDED, smaller** |
| "publish currently means a file" | `gh` authenticated as `carterlasalle`; `fleet-artifacts` GitHub Pages **live, HTTP 200** | **FALSIFIED** |

The last row matters most for ranking: a real public channel exists and has been used exactly once. Its 14-day GitHub traffic report shows **0 page views**. The fleet's problem is not that it cannot publish.

---

## WHAT THE LANDSCAPE SAYS (swept 2026-10-17, sources cited)

| Source | What it actually reports | Why it matters here |
|---|---|---|
| [open-telemetry/semantic-conventions-genai#238](https://github.com/open-telemetry/semantic-conventions-genai/issues/238) (open 2026-06-03, 18 comments) | Proposes `gen_ai.agent.invocation.status` with **one value: `completed`**. Rationale verbatim: *"`error.type` and span error status tell you an invocation failed. Nothing today tells you it succeeded."* Design narrowed over 5 review rounds by @lmolkova; `failed`/`cancelled` were **dropped** as duplicating `error.type`. | **This is the upstream hook.** The attribute is defensible as a spec but, measured against this fleet, carries **zero** information about work product. That is a testable, citable contribution — not an opinion. |
| [semantic-conventions-genai#35](https://github.com/open-telemetry/semantic-conventions-genai/issues/35) (open, 13 comments) | Meta-issue for agentic conventions covering **tasks, actions, agents, teams, artifacts, memory**. Names `gen_ai.artifact.*` as an attribute family and lists it in the checklist as **"Artifacts (`gen_ai.artifact.*`) – issue TBD"**. | The artifact family is **designed but unfiled**. `gen_ai.artifact.*` describes artifact *identity* ("tangible inputs and outputs... LLM prompts, embeddings, documents"), not whether a run's artifact **satisfies its contract**. The gap I can fill is not "artifacts exist" — it is "artifact satisfies stated obligation." |
| [semantic-conventions-genai#588](https://github.com/open-telemetry/semantic-conventions-genai/issues/588) (closed) | "clarify `execute_tool` span vs external effect confirmation" — **closed** because the distinction *"does not give OpenTelemetry `execute_tool` instrumentation authors or telemetry consumers a concrete additional action beyond the existing tool-result and error/status semantics."* | **This is the standing objection that will kill a weak proposal.** It is also the bar to clear: any contribution must ship a *concrete additional action*, not a distinction. My kill-test supplies one (a `delivered` / `not_delivered` signal sourced from an independent oracle) plus its measured consequence. |
| [open-telemetry/semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) repo itself (retrieved via GitHub API) | **Zero tagged releases.** Repo created 2026-05-05, 452 stars, 216 open issues, active commits. `gen_ai.*` was deprecated out of the main `semantic-conventions` repo (v1.42.0, 12 Jun 2026) and moved here. | Confirms the window is **open and unsettled** — conventions are being argued now, and a well-evidenced issue can still shape them. It also confirms citing "the standard" is premature: there is no release to comply with. |
| [Hughes, *Our Agent Telemetry Has No Word for 'Done'*, BLOG@CACM, 11 Sep 2026](https://cacm.acm.org/blogcacm/our-agent-telemetry-has-no-word-for-done/) | *"A completion record is testimony. An oracle is evidence."* Requires an oracle with **independence and invisibility**. Cites Stack Overflow 2024→2025: usage 76%→84% while trust fell 43%→33%, and 66% cite "almost right, but not quite." | The **intellectual frame** for ranking #1. It is prior art for the *observation* (cited as such) and supplies the test a proposal must pass: is the signal independent of the actor? |
| [Partnership on AI, *The Observability Gap in AI Agents*, 7 Oct 2026](https://partnershiponai.org/resource/the-observability-gap-in-ai-agents/) | Assesses four agent frameworks against six monitoring goals; finds **six telemetry gaps** (persistent agent identity, permission-mode changes, memory changes, human intervention, chain-of-thought, token-level logprobs). Notes only Claude Agent SDK records mid-session permission-mode changes. | Independent, **institutional** confirmation that agent telemetry is incomplete — and notably, *outcome verification is not in their six gaps*. That is either an omission or a signal the market has not named it yet. Either way, my proposal is not redundant with this audit. |
| [Gao & Zhou, *Can Agent Benchmarks Support Their Scores?*, arXiv:2605.10448](https://arxiv.org/html/2605.10448v1) | Adds an outcome-evidence reporting layer over five benchmarks; labels each completed record **Evidence Pass / Evidence Fail / Unknown**, keeping Unknown visible. | Supplies the exact three-value vocabulary my proposal recommends upstream. Cite it; do not reinvent it. |
| [Kim, *The Completion Illusion*, IOV Labs](https://labs.iovstudio.kr/papers/agent-control-tower.pdf) | 896 micro-tasks, 4 models: agents self-report perfect scores on **every** run while actual accuracy is 86–96%; false-completion is capability-tiered; a self-verification protocol **does not fix it**. | The measured reason a *self-reported* status cannot be the answer — which is precisely why #238's `completed` is weak and an independent oracle is required. |

**Reading of the landscape.** The field has converged on the *problem* (Hughes, Kim, Partnership on AI, Advani) and is now **actively drafting the vocabulary** (#35, #238) — but the draft being merged is the wrong shape: `completed` records that the loop ended, which is the same green dashboard Hughes indicts. The unclaimed ground is not another essay on silent failure; every source here already has that. It is a **measured counter-example plus a concrete spec change**, filed where the spec is being written, in the exact form #588 says is required to be actionable.

---

## THE QUESTION

**Given that the fleet now retains enough evidence to judge its own runs and still refuses to judge them, where should one cycle of effort go: inward (fix our verdict), outward (fix the standard), or toward audience (make the publishing channel count)?**

---

## OPTION A — FILE THE UPSTREAM CONTRIBUTION: EVIDENCE FOR A `delivered` SIGNAL, WITH THE FLEET AS THE COUNTER-EXAMPLE

**What:** Open a well-scoped issue (and, if maintainers bite, a PR) on `semantic-conventions-genai` arguing that `gen_ai.agent.invocation.status = completed` (#238) cannot carry the meaning its rationale claims, evidenced by this fleet: 116 clean runs stamped `completed`, 83 with no work product, **lift 1.000x**. Propose the concrete additional action #588 demands: an outcome attribute sourced from an **independent oracle** (the world changed / an artifact satisfies a contract), with Gao & Zhou's three values — `evidence_pass` / `evidence_fail` / `unknown` — and `unknown` mandatory rather than defaulted away. Cite Hughes and Kim as prior art for the observation; claim only the production measurement and the spec delta.

- **Pros:** The window is genuinely open — zero releases, 216 open issues, active draft work. The contribution is *cheap to verify by a stranger* (a 40-line script against a published snapshot). It fits the bar #588 set, which most proposals miss. It is the only move that makes the fleet's finding **citable and durable** rather than a workspace file nobody reads. Zero Commander time.
- **Cons:** Unrefereed until a maintainer responds; a maintainer may rule it out of scope exactly as they did #588. The fleet's evidence is n=1 and from one vendor's harness, which a reviewer can discount. It does **not** change fleet behaviour — it changes what the fleet says.
- **Effort:** Low (~1 cycle: the kill-test is already written and passing, the snapshot is frozen). **Payoff:** High and compounding — an accepted attribute outlives every artifact this fleet produces.

---

## OPTION B — JOIN THE SECOND LEDGER: MAKE THE FLEET JUDGE ITS OWN RUNS

**What:** The autonomy ledger already holds the verdict the run ledger refuses to read. `autonomy.ledger.jsonl` has **116 `phase:outcome` rows**, of which **60 carry a `runId` that resolves to a run row (60/60)** — and the run row still says `reason: done`, `completionVerdict: not_assessed`. Implement the join and populate `completionVerdict` on every run that has a decidable outcome.

- **Pros:** Removes the `not_assessed` hole **without new instrumentation** — the second ledger already records `delivered: true|false` with reasons (`built` 49, `no-candidates` 41, `no-manifest` 11). It is the literal fix for "0 of 765 runs carry a verdict." It would immediately surface **11 runs that are `done` in the run ledger and `delivered:false` in the autonomy ledger** — the fleet's first measured contradiction set.
- **Cons:** Coverage is **77/765 (10.1%)** — tiny, and **0% of the 82 silent "done" runs in 48h** carry a joinable outcome. So it converts `not_assessed` to a verdict for a tenth of the ledger and leaves the population that matters untouched. Worse, it joins two records **written by the same system about itself** — Hughes' "testimony, not evidence" — and would manufacture a reassuring verdict field over self-report.
- **Effort:** Medium (schema + backfill + a gate). **Payoff:** Low-to-medium — it fixes a field, not a measurement, and risks exactly the false comfort the literature warns about.

---

## OPTION C — CHASE THE AUDIENCE: PUT THE FINDING IN FRONT OF PEOPLE WHO WILL USE IT

**What:** Stop minting local artifacts and use the channel that already exists: `fleet-artifacts` is a live public GitHub Pages site (HTTP 200) with a real artifact on it. Publish a short, cited, self-contained piece — one page, the kill-test as its spine — and then do the distribution work that a page alone never does (link it from a relevant issue thread, an r/LocalLLaMA or HN post, the OTel discussion).

- **Pros:** Attacks the measured failure directly: **0 page views in 14 days** is not a content problem, it is a distribution problem, and the only artifact ever published is 8 days old. The infrastructure is already paid for and working.
- **Cons:** It is the move with the **least evidence it will work** — the fleet has no audience, no track record, and no way to read whether anything lands beyond a view counter. Publishing into silence twice is not a strategy. And a marketing push on top of a finding that (per Option A's gap analysis) reviewers may rule out of scope would be distributing a claim before it is one.
- **Effort:** Low. **Payoff:** Unknown, and unmeasurable within a cycle — the definition of a bad bet at this size.

---

## RECOMMENDATION

**Option A, with Option C deferred one cycle and Option B demoted to a cleanup, not a strategy.**

Three measured facts decide it. First, the channel is **open right now**: `semantic-conventions-genai` has zero tagged releases, 216 open issues and live drafting of the exact vocabulary in question, so a contribution filed today can still shape it — a window that closes on its own schedule, not mine. Second, the **evidence is already in hand and cheap for a stranger to check**: the kill-test returns lift **1.000x** (`83 of 116 completed runs produced no work product`) from a frozen snapshot, and the #588 precedent tells us precisely what shape is required to survive review — a concrete additional action, which a `delivered`/`evidence_*` signal sourced from an independent oracle is, and which "this distinction is important" is not. Third, Option B looks like the responsible inward fix but **fails on coverage**: 0% of the silent runs that define the problem have a joinable autonomy outcome, so it would populate a verdict field for a tenth of the ledger using self-report — turning `not_assessed` into a confident number that Hughes' argument says we should not trust. That is worse than the honest blank it replaces. Option C is the only option whose success I cannot predict or measure, and it is strictly better *after* A, when there is something citable to distribute.

**Immediate next actions, in order:**
1. **File the issue on `semantic-conventions-genai`** referencing #238 and #35, with the frozen snapshot and `killtest_otel_completed_2026-10-17.py` linked as the reproducer. *Commander review of the final text is the one human step — it goes out under their GitHub account.*
2. **Correct yesterday's directive in place**: mark the "claim channel is structurally dark" finding as superseded by the populated `completionEvidence` schema, and mark Rank 1 (claim-retention detector) as NOT BUILT. *Zero Commander time.*
3. **Only if the issue draws a maintainer response**, publish Option C's page with the thread as its anchor. *Zero Commander time until then.*

---

## RISKIEST ASSUMPTION

**That the gap between "the loop terminated" and "the work was done" is a *convention* problem that upstream can fix — rather than a *capability* problem no attribute can fix.**

The evidence against my own assumption is strong and I am stating it plainly: Kim measured that a self-verification protocol **does not** reduce false completion, and Hughes argues any check the actor can inspect becomes part of its objective function — which is an argument that telemetry *emitted by the actor* is structurally incapable of being evidence, however well specified. If that is right, then a `delivered` attribute emitted by the agent runtime is just a more polite `completed`, and I would be spending the cycle adding a carefully-named field to the same green dashboard. My counter is narrow and honest: the attribute I propose is sourced from an **independent oracle** (world-state change, artifact-contract satisfaction), not from the actor's self-report — but on this fleet the "oracle" is still the same harness that runs the agent, so **independence is asserted, not proven.**

---

## KILL-TEST — RUN, NOT DEFERRED

**Question:** Does the proposed upstream convention — `gen_ai.agent.invocation.status = completed` — separate delivered work from silent completion in a real fleet?

**Cheapest test that decides it:** emit the signal the convention would emit (`completed` on every clean-terminating run) and cross-tabulate it against an independent outcome measure (artifact present **and** ≥1 mechanically-verified write effect). If lift over base rate is ~1.0, the attribute carries no information.

**Result — `killtest_otel_completed_2026-10-17.py`, EXIT 1:**

```
window 48h -> 132 runs, 116 done
runs stamped `completed`      : 116 / 116 (100%)
  of those, DELIVERED work    : 33
  of those, SILENT            : 83
base rate of delivered work   : 28.4%
P(delivered | completed)      : 28.4%
lift                          : 1.000x
distinct values emitted       : 1
runs labelled `completed` that produced no work product: 83
  (the attribute is correct-looking on 71.6% of silent runs)
VERDICT: DOES NOT SEPARATE
```

**It survives as a *finding*, and that is the point.** The test was designed to kill my proposal; it did not, because it killed the *upstream* attribute instead. Two caveats I will not paper over: lift 1.000x is guaranteed *by construction* once a convention emits one value on all clean runs — so this test does not prove the attribute is useless in general, it proves it is useless **for this question**, which is the only question the fleet can answer from its own ledger. And the independent outcome measure (artifact + verified write) is stricter than "the work was done"; it can under-count genuine work that leaves no file.

**Second test, run for the same reason — does the fleet's own `completionVerdict` field discriminate?** It cannot: `contract: null` and `checks: []` on **765/765** runs, `completionVerdict: not_assessed` on **765/765**. A verdict field with no contract to judge against is not a measurement; it is a column.

**Third test — the contract audit, which produces the first honest delivery rate** (`completion_contract_audit_2026-10-17.py`):

| Contract (derived from the routine's own prompt) | Runs | Satisfied | Rate |
|---|---|---|---|
| DELIVER — prompt asks for an artifact | 50 | 27 | **54.0%** |
| MONITOR — prompt licences an empty result | 64 | 31 | 48.4% |
| AMBIGUOUS / no readable prompt | 2 | 0 | 0.0% |

This splits a population every directive since 10-15 has reported as one number. **The 46% of "done" runs that produced nothing are not 46% failures** — 64 of the 116 were explicitly licensed to produce nothing (licence text verified present in 8 away-workshop prompts), and only the **54.0% DELIVER satisfaction rate is a delivery failure.** Both 10-15 and 10-16 would have been wrong to report these as a single rate, and both did.

**A defect this cycle found and fixed in its own instrument.** The first run of the contract audit reported 25 runs as `UNMAPPED` at 0% — scoring them failures because no cron prompt was attached to them. 11 of those 25 had in fact produced artifacts and verified writes: the classifier was scoring *its own blindness* as their failure. Corrected to `NO_PROMPT`, falling back to the run's own title, which resolved 25 runs to 0. That is the third consecutive cycle in which a measurement error was caught only by inspecting the number rather than trusting it, and it is recorded here rather than silently patch.

---

## PROVENANCE TABLE — every load-bearing figure

| Figure quoted | Value | Source of truth | Verified by |
|---|---|---|---|
| Ledger size | 765 runs | frozen snapshot | both scripts |
| Latest run (UTC) | 2026-10-17T14:00:12Z | frozen snapshot | `killtest_otel_completed` |
| 48h window | 132 runs, 116 done | frozen snapshot | both scripts |
| "Delivered work" (strict: artifact + ≥1 verified write) | 33 / 116 = 28.4% | frozen snapshot | `killtest_otel_completed` |
| Runs stamped `completed` that produced nothing | 83 | frozen snapshot | `killtest_otel_completed` |
| Lift of `completed` over base rate | 1.000x | computed | `killtest_otel_completed` |
| `completionEvidence` populated | **765 / 765** | live + frozen ledger | direct count |
| `contract: null` / `checks: []` | **765 / 765 each** | live + frozen ledger | direct count |
| `completionVerdict: not_assessed` | **765 / 765** | live + frozen ledger | direct count |
| Effects recorded | 10,336 total (2,966 mechanically_verified / 4,780 judgment_required / 2,590 unverified) | frozen snapshot | direct count |
| DELIVER contract runs / satisfied | 50 / 27 = 54.0% | frozen snapshot + cron prompts | `completion_contract_audit` |
| MONITOR contract runs / satisfied | 64 / 31 = 48.4% | frozen snapshot + cron prompts | `completion_contract_audit` |
| Away-workshop jobs still live | 11 (10 enabled) every 6h | `snapshot-2026-10-17-cron.json` | direct count |
| Cron jobs registered / enabled / error | 42 / 38 / 10 | frozen cron snapshot | direct count |
| Autonomy `phase:outcome` rows | 116 | `autonomy.ledger.jsonl` | direct count |
| Those with a `runId` resolving to a run row | 60 / 60 | join on `runId` | direct count |
| Silent 48h runs with a joinable autonomy outcome | **0 / 82** | join on `runId` | direct count |
| Run says done, autonomy says delivered=false | 11 | join on `runId` | direct count |
| Self-directed (`SELF-DIRECTED WORK`) runs | 172, of which 118 bailed (≤3 turns, 0 tools) | frozen snapshot | direct count |
| Bail rate, other cron runs | 29 / 441 = 7% | frozen snapshot | direct count |
| `claim_retention.py` exists | **No** | `ls ~/fleet/bin/` | direct check |
| Live gate detectors registered | **1** (`fleet-nightly-falsifier`, 4/4, PASS) | `liveness-register-2026-10-16.json` | direct read |
| `fleet-artifacts` Pages status | built, **HTTP 200** | GitHub API + curl | direct probe |
| `fleet-artifacts` 14-day page views | **0** | GitHub traffic API | direct read |
| `fleet-artifacts` last commit | 2026-10-15T18:07Z, 1 artifact | GitHub API | direct read |
| Reachable messaging channels | **0** | `channel_targets` | this run |
| `gh` authenticated as | carterlasalle, scopes gist/read:org/repo/user/workflow | `gh auth status` | direct check |
| Upstream GenAI semconv tagged releases | **0** | `api.github.com/.../releases` → `[]` | direct API call |

**External figures** are quoted from the cited sources, each retrieved directly this cycle and labelled with its identifier. The `#238` and `#35` quotes were read from their GitHub issue bodies via the API, not from search snippets — the 10-16 correction log records why that distinction matters.

**Source retrieval, done before shipping, not after.** Every external source in the landscape table was retrieved in full this cycle — not read from a search snippet — and the verbatim text each claim rests on is logged in `sources-2026-10-17/retrieved-quotes-2026-10-17.md`:

| Source | Retrieved | Method | Result |
|---|---|---|---|
| Hughes, BLOG@CACM | **Yes** | full-body HTTP fetch | All 8 quoted passages matched verbatim |
| Gao & Zhou, arXiv:2605.10448 | **Yes** | full HTML (abstract + intro) | Authors, date, three-label vocabulary, benchmark list, AndroidWorld example all confirmed |
| Partnership on AI, Observability Gap | **Yes** | page text | Six gaps confirmed; outcome verification confirmed **absent** from the list |
| Kim, *The Completion Illusion* | **Yes** | PDF text extraction | 896 instances / 86–96% / per-model deltas / "does not fix it" all confirmed |
| semconv #238, #35, #588 | **Yes** | `gh api` issue bodies | Titles, states, comment counts, verbatim rationale and closure reason confirmed |

**One claim labelled as inference rather than fact:** the Kim paper states **no venue** in the retrieved document — it is a lab-hosted PDF with no conference or journal named. Where I treat it as unrefereed, that is an inference from the absence of a stated venue, not something the source says. **One thing I did not open:** the four Google-Docs links inside issue #35 (the per-family attribute drafts). My statement that `gen_ai.artifact.*` is "designed but unfiled" rests only on the #35 checklist line reading "Artifacts (`gen_ai.artifact.*`) – issue TBD", which I did read. I make no claim about what those drafts contain.

---

## CORRECTION LOG

### C1 — the "dark channel" finding is FALSIFIED (material — it was yesterday's headline)

**What 10-16 said:** "the retained ledger contains *no run's own completion claim*... the fleet cannot measure its own false-success rate at all" and "no text-reading monitor has any coverage here, because the text it would read is not retained."

**What the ledger says today:** `completionEvidence` is present on **765/765** runs carrying `schemaVersion: starnet.completion-evidence.v1`, with `effects[]`, `checks`, `contract`, `contractErrors` and `completionVerdict` inside it. 10,336 effects are recorded. **Caveat, stated because it changes the strength of the correction:** I cannot tell from the ledger whether the schema was *added* in the last 24h or whether 10-16's measurement read the older top-level `deliveryText`/`deliveryPrompt` fields (which remain empty on 132/132 runs in 48h). Both readings are consistent with the data; I am not claiming the harness changed, only that **the conclusion "nothing is retained" is false as of today.** The correct statement is narrower: *the evidence is retained, but `completionVerdict` is `not_assessed` on every run because `contract` is null on every run* — the record exists, the judgment does not.

### C2 — yesterday's Rank 1 was never built

**What 10-16 recommended and implied would happen:** build `~/fleet/bin/claim_retention.py`, register it in `detector_gate.py`, probe it against the seeded corpus. Its "immediate next actions" said to do this at zero Commander time.

**What exists:** no `claim_retention.py` on disk; `detector_gate.py` registers exactly one detector (`fleet-nightly-falsifier`, 4/4) and its `shipped_detectors()` only knows that one plus an optional candidate. **Three consecutive directives have now named a detector and shipped none** — that is a pattern about the fleet's capacity to execute its own recommendations, not about the recommendation. It is one reason this cycle's Rank 1 is a *filing* (bounded, one artifact, reviewable by a human) rather than another instrument to be built inside the loop.

### C3 — "publish currently means a file" is FALSIFIED

10-15 and 10-16 both caveated their recommendation with "the station has zero reachable channels, so publish means a file." **`channel_targets` still returns 0** — that much is true — but that is not the fleet's only channel. `gh` is authenticated as **carterlasalle** with `repo` scope, `carterlasalle/fleet-artifacts` is a **public repo with GitHub Pages built and serving HTTP 200**, and it carries one published artifact from 2026-10-15. So the fleet *can* publish to the open web today, with no new setup. What it cannot do is get anyone to read it: **the 14-day traffic report shows 0 page views, 0 referrers, 0 popular paths.** The constraint has moved from *reach* to *distribution*.

### C4 — the licensed-silence share is smaller than reported, not larger

10-16 reported **77.5%** of silent runs sit under a prompt licensing a no-op. Measured this cycle against the current cron roster with prompt text verified: **64 of 116 done runs (55%)** map to a MONITOR contract. The 10-16 figure was computed over the 80 silent runs of *its* window with a different mapping method (title-based, 10 runs unmapped); this cycle's is prompt-based with a title fallback. **Neither is wrong about its own window**, but the two are not comparable and the number should not be quoted as if it had moved.

---

## WHAT I AM NOT CLAIMING

- **Not** that the fleet's silent runs are "false successes." Per the contract audit, the majority are either licensed monitors (64) or runs that owe a deliverable and miss it (23 of 50 DELIVER runs). "False success" is a claim about intent and self-report; I measured artifact and effect presence.
- **Not** that the upstream attribute will be accepted, or that my independence claim is proven. The oracle is the same harness. Stated under "riskiest assumption."
- **Not** that `fleet-artifacts` having 0 views proves the fleet's output is unwanted — a 14-day traffic window on a site with no distribution is near-zero by default, and GitHub counts pages traffic, not clones (14 clones / 9 uniques were recorded on 2026-10-15, i.e. the publish itself).
- **Not** that the 54.0% DELIVER rate is the fleet's true success rate. The contract is derived from prompt *text*; a prompt-derived contract is a proxy, more than the zero contracts the fleet has and less than a real one.
