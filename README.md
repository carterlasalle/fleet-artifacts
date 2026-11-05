# Fleet artifacts — published, openable from any device

Self-contained pages produced by the StarNet fleet's own autonomous loop, published by
DEPLOYER to GitHub Pages so the Commander can open them from any device.

**Live:** https://carterlasalle.github.io/fleet-artifacts/

**Newest first.** The current front page is the 2026-11-05 idea board.

## What is here

| File | Artifact | Published |
|---|---|---|
| `index.html` | **Fleet Idea Board — 2026-11-05** (Strategist autonomous cycle) — current front page | 2026-11-05 |
| `latest.html` | byte-identical copy of the same page | 2026-11-05 |
| `idea-board-2026-11-05.html` | the same page under its dated source name | 2026-11-05 |
| `publish-record-2026-11-05.html` | standalone publish record for the 2026-11-05 publish | 2026-11-05 |
| `dark-render-2026-10-28.html` | Pull the Plug — does every page still draw with the cable out? (software room) | 2026-10-29 |
| `idea-board-2026-10-17.html` | Fleet Idea Board — 2026-10-17 (Strategist autonomous cycle) | 2026-10-22 |
| `pull-the-plug.html` | Pull the Plug — does every page still draw with the cable out? | 2026-10-15 |
| `evidence/publish-2026-11-05/` | source copy, full directive, fetched quotes, previous front page, sha256 sums | 2026-11-05 |
| `evidence/publish-2026-10-29/` | source copy, previous index, sha256 sums | 2026-10-29 |
| `evidence/idea-board-2026-10-17/` | source page, the full directive, sha256 sums | 2026-10-22 |
| `evidence/` | build tool, receipts, falsification logs, proposals for Pull the Plug | 2026-10-15 |

Every page is a single file with inline CSS only — no scripts, no external requests,
so it renders offline once loaded.

## Sources (local, on the station)

- `index.html`, `latest.html`, `idea-board-2026-11-05.html` <-
  `/home/hermes/fleet/directives/idea-board-2026-11-05.html` (18255 bytes,
  sha256 `5e13156bcbe44736523cf8cbf77734fe918cd9c53a3c3fd6f67af4df411a3481`)
- `index.html`, `latest.html`, `dark-render-2026-10-28.html` <-
  `/home/hermes/fleet/rooms/software/workspace/artifacts/dark-render-2026-10-28.html`
  (27794 bytes, sha256 `e3969e1ef89caf3dd512a23f1c85ad066dfae4a0243935b97012b7696ed78d39`)
- `idea-board-2026-10-17.html` <- `/home/hermes/fleet/directives/idea-board-2026-10-17.html`
  (15946 bytes, sha256 `39c22110a91d27cdb6955431aa64ebef3e19509886f397bededef45db2eb4c74`)
- `evidence/publish-2026-11-05/directive-2026-11-05.md` <-
  `/home/hermes/fleet/directives/directive-2026-11-05.md` (sha256
  `ee87b414b1ef843152a40cf0fd16406031797369021bf06b7ae6e1ad08d2756e`)
- `evidence/idea-board-2026-10-17/directive-2026-10-17.md` <-
  `/home/hermes/fleet/directives/directive-2026-10-17.md` (sha256
  `1b2e793fc30d07ff7ebb0823930381ba2aa7f1994aa95ee38e45593c39eb298f`)

## Route

GitHub Pages, branch `main`, path `/`, HTTPS enforced, repo public. Published with the
already-authenticated `gh` CLI (account `carterlasalle`, scope `repo`) — no interactive login.

Deploy state as of 2026-11-05: `build_type` is **`legacy`**, so GitHub Pages rebuilds the site
directly from `main` on every push and this is what serves the live URL. The `.github/workflows/pages.yml`
Actions pipeline exists but **cannot currently start** — GitHub annotates the run with
*"The job was not started because your account is locked due to a billing issue."* A push still
publishes correctly through the legacy builder; the Actions path will resume once the billing flag
is cleared.
