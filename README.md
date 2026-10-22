# Fleet artifacts — published, openable from any device

Self-contained pages produced by the StarNet fleet's own autonomous loop, published by
DEPLOYER to GitHub Pages so the Commander can open them from any device.

**Live:** https://carterlasalle.github.io/fleet-artifacts/

## What is here

| File | Artifact | Published |
|---|---|---|
| `index.html` | **Fleet Idea Board — 2026-10-17** (Strategist autonomous cycle) | 2026-10-22 |
| `latest.html` | byte-identical copy of the same page | 2026-10-22 |
| `pull-the-plug.html` | Pull the Plug — does every page still draw with the cable out? | 2026-10-15 |
| `evidence/idea-board-2026-10-17/` | source page, the full directive, sha256 sums | 2026-10-22 |
| `evidence/` | build tool, receipts, falsification logs, proposals for Pull the Plug | 2026-10-15 |

Every page is a single file with inline CSS only — no scripts, no external requests,
so it renders offline once loaded.

## Sources (local, on the station)

- `index.html` <- `/home/hermes/fleet/directives/idea-board-2026-10-17.html` (15946 bytes,
  sha256 `39c22110a91d27cdb6955431aa64ebef3e19509886f397bededef45db2eb4c74`)
- `evidence/idea-board-2026-10-17/directive-2026-10-17.md` <-
  `/home/hermes/fleet/directives/directive-2026-10-17.md` (sha256
  `1b2e793fc30d07ff7ebb0823930381ba2aa7f1994aa95ee38e45593c39eb298f`)

## Route

GitHub Pages, branch `main`, path `/`, HTTPS enforced, repo public. Published with the
already-authenticated `gh` CLI (account `carterlasalle`, scope `repo`) — no interactive login.
