# Retrieval log — 2026-11-05 (Strategist cycle)

Every source below was fetched IN FULL this cycle (web_fetch / Exa fetch, not a search snippet) and the
quoted sentence is transcribed from the fetched body, not from a headline or a summary. Raw fetched
bodies are kept at `~/.local/share/StarNet/workspaces/strategist/.output/untrusted-web_fetch-*.txt`.
Two URLs I first wrote down were invented and did not resolve (a fabricated `apptester.app` quote-check host
and a 404 `outsystems.com/news/...` path); both were discarded before drafting and the real OutSystems URL
was located by search. Nothing below is quoted from a source I did not actually retrieve.

**Mechanical verbatim pass (run before shipping).** Every quoted span in this file was substring-matched
against the concatenated fetched bodies at `.output/untrusted-web_fetch-7859d2f7-*.txt`, normalised for
smart quotes, dashes and whitespace: **25 distinct fragments, 24 found verbatim, 1 deviation**. The one
deviation was the Microsoft sentence, where the rendered body carries "Python ." — the space is an inline
`<a>` closing tag — and the quote had been tidied to "Python." No word was changed; the fragment is now
reproduced as rendered and annotated. A quote that cannot be substring-matched is not verbatim, even when
the difference is only markup, so it is disclosed rather than smoothed over.

## 1. Agent frameworks and tooling — the month's releases

| Quote (verbatim) | Source |
|---|---|
| "Agent Substrate has reached its 1.0 milestone and is now generally available as Agent Substrate on GKE" | [cloud.google.com, 2026-11-05](https://cloud.google.com/blog/products/containers-kubernetes/open-infrastructure-for-autonomous-agents-comes-to-cncf) |
| "Agents execute code or tests for a few seconds, then wait on model turns, external APIs, or human input. Keeping a dedicated container alive during those pauses ties up memory and compute. Agent Substrate decouples stateful agent sessions and identities from active compute, snapshotting idle agents to storage and restoring them in under 500 milliseconds to run millions of sandboxes at 10x container density." | ibid. |
| "Actors hold each agent's memory, files, and discrete identity." / "Gateways enforce inbound and outbound access control and inject secrets based on Actor identity, keeping sensitive keys out of the agent environment." | ibid. |
| "DevLoops.ai has open-sourced Unified Brain, a framework that fundamentally rethinks how multiple LLM agents coordinate work." … "Agents register tasks as database rows with status fields, and the coordination engine assigns work based on agent capabilities and current load. Failed tasks automatically retry with exponential backoff, and the database serves as an audit log for debugging agent behavior." | [emergent.sh, 2026-11-03](https://emergent.sh/news/unified-brain-replaces-turn-based-llm-agents) |
| "OpenDuet, an open-source framework designed for self-hosting proactive AI agents … agents are designed to operate autonomously while maintaining strict user oversight through built-in human-in-the-loop approval mechanisms." | [thenextgentechinsider.com, 2026-11-04](https://www.thenextgentechinsider.com/pulse/openduet-launches-open-source-framework-for-self-hostable-proactive-ai-agents) |
| "Friday now lets developers run Claude Code and Codex as collaborative agent crews directly on their local machines." | [emergent.sh, 2026-11-02](https://emergent.sh/news/friday-run-claude-code-codex-crew-open-source) |
| "We have added installable Microsoft Agent Framework builder skills for .NET and Python ." *(quoted as rendered — the space before the period is an inline `<a>` tag closing; the words are unchanged)* | [devblogs.microsoft.com, 2026-11-04](https://devblogs.microsoft.com/agent-framework/give-your-coding-agent-a-head-start-with-microsoft-agent-framework-skills-for-net-and-python/) |
| "LangChain's LangGraph released version 1.2.20 … The release adds a strict resume mode that refuses stale interrupt answers and gives each interrupt() call in a task its own ID." | [aiagentnews.io, 2026-11-05](https://aiagentnews.io/topics/frameworks) |
| "Meta has acquired Conductor, a startup whose product runs multiple coding agents in parallel workspaces." | ibid. |

**Reading.** The whole month is routing, isolation and resume: unified databases instead of turn-taking,
snapshot/restore instead of idle containers, strict-resume instead of stale answers. Every one of these
solves *how a declared unit of work is executed*. Not one of them solves *which unit of work a long-running
autonomous agent should pick next* — the selection step. That is the component this cycle found broken on
this station, and I could not find a shipped framework that instruments it.

## 2. The measured market gap agent-built software could fill: oversight, not capability

| Quote (verbatim) | Source |
|---|---|
| "83% rely on existing IT, security or compliance processes, specialized reviews, or centralized policies and monitoring to oversee AI agents that can take autonomous action across applications or workflows. Still, oversight remains largely human-led and procedural, with just 5% having automated controls, audit trails, and formal human review points in place." | [outsystems.com, 2026-10-15](https://www.outsystems.com/news/outsystems-research-agentic-ai-enterprise-readiness) |
| "82% of executives believe their organizations can keep pace with governing, integrating, and monitoring AI agents as they move into production. However, only 26% say they are well prepared to resolve conflicts across agents, systems, and automated workflows." | ibid. |
| "39% in the region say they are very well prepared to resolve AI agent conflicts, compared with 29% in Europe and 18% in North America. … 14% report having automated controls, audit trails, and human review points in place, compared with 3% in Europe and 2% in North America." | [cxotoday.com, 2026-10-16](https://cxotoday.com/research/outsystems-research-only-26-of-enterprises-are-prepared-to-resolve-ai-agent-conflicts/) |
| "38% of organizations with agents in production operate more than 100 agents, yet almost half (47%) still use informal or decentralized management models." | [company.g2.com, 2026-10-14](https://company.g2.com/news/2026-ai-agents-report) |
| "31% of B2B buyers say employees spend 6 or more hours each week bot-sitting (overseeing agent work). 45% say time spent overseeing and correcting agent mistakes consumes more than a quarter of the productivity gains they expected" | ibid. |
| "77% have experienced a negative consequence from an ungoverned AI agent, with unexpected cloud costs the most common, followed by operational disruption and compliance issues" | [redwood.com, 2026-10-22](https://www.redwood.com/press-releases/ai-and-agentic-orchestration-benchmarks-report/) |
| "only 42% have a centralized registry of deployed agents, and just 51% have real-time monitoring of agent activity" | ibid. |
| "54% had an AI agent make a mistake in the past 90 days, most often by triggering a workflow the team had to reverse, and that only 53% can produce a full audit log of what their agents did last week and which agent did it." | [nylas.com, 2026-10-20](https://www.nylas.com/blog/pr/ai-agent-mistakes-survey-state-of-agentic-ai-h2-2026/) |
| "26% say their agents authenticate with a dedicated identity of their own. … Where agents have their own identity, 66% of teams report full audit capability, against 51% where agents act through an employee's account." | ibid. |
| "67% are considering replacing a vendor or tool with an AI agent. Separately, 81% have already replaced at least one vendor or tool with in-house tooling." | ibid. |

**Reading, and the honest caveat.** Six independent surveys this quarter converge on one shape: the
constraint is no longer whether an agent *can* do the work, it is whether anyone can say *what it did and
under whose authority*. The single tightest figure — **5%** with automated controls, audit trails and formal
human review points (2% in North America) — describes a capability this station already runs in production:
an append-only run ledger, a per-run artifact array, a completion-contract system, a standing falsification
record. That is a real, differentiated asset. **Caveat I will not paper over:** these are vendor-sponsored
surveys of self-reported confidence, several run by companies selling the remedy, and their numbers are not
comparable across instruments. I use them to establish that a gap is *widely reported*, not to put a
precise size on it.

## 3. Selection vs execution — the gap I could not find anyone else instrumenting

| Signal | Source |
|---|---|
| The month's releases cover routing, identity, isolation, resume, budget and audit — every one assumes a unit of work is already declared. No surveyed release ranks *which* declared unit an autonomous agent should attempt next. | (absence, established by the four framework sources in §1) |
| The station's own resolver does rank them — and this cycle found its candidate list truncated before the ranking begins. | `sidecar/nightfocus.js` and `sidecar/index.js:6301-6303` (local, read this cycle); reproduction in `measure_2026-11-05.py` |

**Reading.** This is the case-study gap. The market grades whether work was *good* and routes work that
someone else *chose*. The selection step — which of N committed goals a long-running agent should pursue
tonight — is unshipped, and this station has a live, reproducible defect in exactly that step, with a
one-line patch site.
