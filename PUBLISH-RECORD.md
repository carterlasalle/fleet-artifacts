# PUBLISH RECORD — Fleet Idea Board (2026-10-17)

**Published:** 2026-10-22 · **Agent:** deployer (StarNet) · **Status:** PUBLISHED AND VERIFIED

## The live address

    https://carterlasalle.github.io/fleet-artifacts/

Verified 2026-10-22T18:17Z: `HTTP/2 200`, 15,946 bytes served, live body **byte-identical**
to the staged file (sha256 `39c22110a91d27cdb6955431aa64ebef3e19509886f397bededef45db2eb4c74`),
renders at 1280px and 390px, real evidence file fetches over the network with an unchanged
sha256.

## What was published

| | |
|---|---|
| artifact | `idea-board-2026-10-17.html` — titled **"Fleet Idea Board — 2026-10-17"** |
| source | `/home/hermes/fleet/directives/idea-board-2026-10-17.html` |
| produced | 2026-10-17 07:15 by the Strategist's autonomous cycle, StarNet v0.13.1-dirty |
| size | 15,946 bytes |
| sha256 | `39c22110a91d27cdb6955431aa64ebef3e19509886f397bededef45db2eb4c74` |
| why this one | it is the **newest finished artifact** on the station (the 10-17 directive cycle; nothing newer exists in `fleet/` under `rooms/*/workspace/artifacts/`), it is one self-contained page with inline CSS and zero external requests, and it is the fleet's own ranking pass — a real measurement, not a description |

The page's content, in short: the fleet retains the evidence to judge its own runs and still
refuses to — `completionEvidence` is populated on 765/765 runs, `completionVerdict` is
`not_assessed` on 765/765 with `contract: null`; upstream's draft attribute
`gen_ai.agent.invocation.status = completed` scores **lift 1.000x**, labelling 83 of 116 runs
"completed" that produced no work product. It ranks three next moves and kills two of them.

Bundled alongside it: the full directive (`directive-2026-10-17.md`, 28,644 bytes) and
sha256 sums for both files.

## The route used, and why

Routes were probed quietest-first. Findings on this machine today (2026-10-22):

| # | route | result |
|---|---|---|
| 1 | **`gh` CLI → GitHub Pages** | **AUTHENTICATED AND USED.** `gh` is logged in as `carterlasalle`, token scopes `gist, read:org, repo, user, workflow`. No interactive login needed. |
| 2 | Vercel CLI | NOT INSTALLED — `vercel: not found` (previously failed with "No existing credentials found"). |
| 3 | Cloudflare `wrangler` | NOT INSTALLED as `wrangler` (`cf-wrangler` exists in `~/.npm-global/bin`); no CF API token on the box. A `cloudflared` daemon is running but its ingress hostnames live in the Cloudflare dashboard. |
| 4 | Tailscale Funnel | **NOT PUBLIC** — `tailscale funnel status` returns `https://vmi3485649.tail5566e4.ts.net (tailnet only)` plus `:10000 (tailnet only)`. Reachable only from devices already on the Commander's tailnet. |
| 5 | The station's own app route | NOT APPLICABLE — `app.publish` sets data into a StarNet app page and produces no public URL. |

No credential had to be supplied by the Commander. Route 1 was already authorized.

### A real obstacle on route 1, and how it was routed around

The repo's Pages site was configured with `build_type: legacy`. The push landed on GitHub
(verified: `contents/index.html` is the new 15,946-byte file) but the **legacy Pages builder sat
in `status: building` for more than ten minutes across ~30 polls** while
`githubstatus.com` reported Pages operational — a wedged queue on the legacy builder, not a
repo problem.

Rather than wait, the deploy path was switched to the **Actions-based Pages pipeline**, which
does not use the legacy builder: `.github/workflows/pages.yml` (`actions/checkout@v4` →
`configure-pages@v5` → `upload-pages-artifact@v3` → `deploy-pages@v4`). That run
(`39829772490`, "Deploy fleet artifacts to Pages") completed **success** in about 30 seconds,
and the live URL switched to the new artifact immediately.

### Exact commands

    gh repo clone carterlasalle/fleet-artifacts repo -- --depth 1
    cp /home/hermes/fleet/directives/idea-board-2026-10-17.html repo/index.html
    cp ... idea-board-2026-10-17.html repo/latest.html          # byte-identical copy
    mkdir -p repo/evidence/idea-board-2026-10-17
    cp ... idea-board-2026-10-17.html repo/evidence/idea-board-2026-10-17/source.html
    cp ... directive-2026-10-17.md   repo/evidence/idea-board-2026-10-17/
    cd repo && git add -A && git commit -m "Publish Fleet Idea Board 2026-10-17 ..."
    git push origin main
    # legacy builder wedged -> switched to Actions:
    git add .github/workflows/pages.yml && git commit && git push origin main

Pages settings: repo **public**, branch `main`, path `/`, `https_enforced: true`.

## What was verified, and how

Per standing orders, the production bundle was reproduced locally first, then the live copy
was exercised.

**Local, before pushing** (server: `python3 -m http.server 8778 --bind 127.0.0.1`)

- `HTTP 200`, 15,946 bytes; `cmp` against the source artifact: **byte-identical**.
- `<title>Fleet Idea Board — 2026-10-17</title>`.
- Evidence path served: `HTTP 200`.
- Headless Chrome screenshots at 390×1700 and 1280×1400: page draws fully styled.
- Self-containment of the source: **0** remote `<script|link|img|iframe>` tags; 0 `localhost`
  or `127.0.0.1` references.

**Live, after publishing** — `https://carterlasalle.github.io/fleet-artifacts/`

| check | result |
|---|---|
| response | `HTTP/2 200`, `server: GitHub.com`, `content-type: text/html` |
| bytes served | **15,946** — `cmp` against the staged file: **IDENTICAL** |
| sha256 of live body | `39c22110a91d27cdb6955431aa64ebef3e19509886f397bededef45db2eb4c74` — matches source |
| title | `Fleet Idea Board — 2026-10-17` |
| render, desktop 1280px | headless Chrome screenshot: dark report, position callout, 6 stat cards, 3 ranked-move cards with For/Against panels, kill-test table all present |
| render, mobile 390px | single column, no horizontal overflow, no clipped text |
| remote subresources in the published copy | **0** |
| real backend path | `evidence/idea-board-2026-10-17/directive-2026-10-17.md` fetched over the network: `HTTP 200`, 28,644 bytes, sha256 `1b2e793fc30d07ff7ebb0823930381ba2aa7f1994aa95ee38e45593c39eb298f` — identical to the local file |
| path checklist | `/`, `/latest.html`, `/pull-the-plug.html`, `/README.md`, `/evidence/idea-board-2026-10-17/directive-2026-10-17.md`, `.../source.html`, `.../SHA256SUMS.txt`, `/evidence/verify/plug-receipt.json`, `/evidence/build/plug_check.py` — **9/9 returned 200** |

The artifact is a static page with no backend, so the "one real backend path" check was
satisfied by fetching a real evidence file over the network and confirming its bytes were
unchanged — a stronger check than a 200 on a static path.

## What is live in the repository

    https://github.com/carterlasalle/fleet-artifacts   (public, branch main)

| path | what it is |
|---|---|
| `index.html` | the artifact — identical bytes to `latest.html` and to the source |
| `latest.html` | the same page under a stable name |
| `pull-the-plug.html` | the previously published fleet artifact, kept in place |
| `evidence/idea-board-2026-10-17/` | source page, full directive, `SHA256SUMS.txt` |
| `evidence/` | build tool, receipts, falsification log, proposals for Pull the Plug |
| `.github/workflows/pages.yml` | the Actions deploy pipeline now serving this site |

## Settings the Commander must apply — none required

The publish is complete and public as it stands. Two optional notes, not blockers:

1. The repository is **public**. A public Pages URL cannot be private on a free plan; say so
   and I will unpublish instead.
2. The site now deploys from a **GitHub Actions workflow** rather than the legacy builder.
   Settings → Pages → Source should read "GitHub Actions". No action needed from the
   Commander unless they prefer the legacy builder back.
3. If the Commander later wants a different host (a `netlify`, `vercel` or `wrangler` login),
   that is a one-time interactive sign-in only they can perform. GitHub Pages works today
   without it.

## Nothing was faked

The route that worked was already authenticated on this machine. The routes that did not work
are recorded above with the exact output each returned, and none was reported as a success.
Source artifacts were **read-only**: they were copied, never modified.

## Evidence files

    verify/publish-2026-10-22/live-index.html      raw body served by the live URL
    verify/publish-2026-10-22/live-directive.md    evidence file fetched over the network
    verify/publish-2026-10-22/live-headers.txt     live response headers
    verify/publish-2026-10-22/live-desktop.png     live render, 1280px
    verify/publish-2026-10-22/live-390.png         live render, 390px
    verify/publish-2026-10-22/proof.jpg            cropped proof frame embedded in the HTML record
