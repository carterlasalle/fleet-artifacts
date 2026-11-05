# PUBLISH RECORD — Fleet Idea Board 2026-11-05

**Published:** 2026-11-05 · **Agent:** DEPLOYER (StarNet) · **Status:** PUBLISHED AND VERIFIED

## The live address

    https://carterlasalle.github.io/fleet-artifacts/

Verified 2026-11-05T19:09Z: `HTTP/2 200`, 18,255 bytes served, live body **byte-identical** to the
source file (sha256 `5e13156bcbe44736523cf8cbf77734fe918cd9c53a3c3fd6f67af4df411a3481`).
The same page re-read independently with the station's own `web_fetch` returned the same content.

## What was published

| | |
|---|---|
| artifact | `idea-board-2026-11-05.html` — titled **"Fleet Idea Board — 2026-11-05"** |
| source | `/home/hermes/fleet/directives/idea-board-2026-11-05.html` |
| produced | 2026-11-05 07:34 by the Strategist's autonomous daily cycle |
| size | 18,255 bytes |
| sha256 | `5e13156bcbe44736523cf8cbf77734fe918cd9c53a3c3fd6f67af4df411a3481` |
| why this one | it is the **newest finished artifact on the station** — every finished `.html`/`.md` under the fleet roots was listed by mtime and nothing is later than 2026-11-05 07:34 — and it is genuinely self-contained: **0** `<script>` tags, **0** `<link>`/`<img>`/`<iframe>`/`<object>` tags carrying a remote URL, **0** `localhost` or `127.0.0.1` references. The 11 `https://` strings in it are citation anchors in the footer; nothing loads over the network |

The finding it reports: the fleet's shipped priority resolver is fed a list pre-cut to the twelve
*oldest* open quests — `questStore.list().filter(open).slice(0, 12)` at `sidecar/index.js:6303`.
The live focus is `q:13` (score 0.453) while four open quests score higher (`q:22` at 1.075),
because `q:22` is the 22nd element of a list sliced to 12 and is therefore never a candidate.
Every quest with an external blast radius — both security, both distribution — is among the nine
that are cut. The page carries five kill-tests, two self-corrections against its own earlier draft,
and a verifier (`measure_2026-11-05.py`) reporting **35 checks / 35 PASS, exit 0**.

## The route used, and every route that did not work

| # | route | state on this host, 2026-11-05 |
|---|---|---|
| 1 | **`gh` CLI → GitHub Pages** (push to `main`) | **AUTHENTICATED AND USED.** `gh` already logged in as `carterlasalle`, scopes `gist, read:org, repo, user, workflow`. No interactive login, no credential from the Commander |
| 2 | GitHub **Actions** deploy workflow (`.github/workflows/pages.yml`) | **DID NOT START** — see the blocker below. Failed twice, run `42090945889` |
| 3 | GitHub Pages **legacy builder** | **USED, and it is what actually served the page.** `build_type: legacy`, rebuilt on the same push, `status: built` within 22 s |
| 4 | `vercel` CLI | not installed on PATH |
| 5 | `wrangler` (Cloudflare) | not installed on PATH; no Cloudflare API token on the box |
| 6 | `cloudflared` tunnel | installed, but the tunnel's ingress hostnames live in the Cloudflare dashboard — cannot mint a public hostname without the Commander |
| 7 | Tailscale Funnel | serves `vmi3485649.tail5566e4.ts.net` **tailnet only** — not reachable by a device off the tailnet |
| 8 | StarNet `app.publish` | writes data into an app page; produces **no public URL** |

Nothing was published through routes 4–8. Each is recorded with the state it actually returned
rather than reported as a success.

## The blocker worth the Commander's attention

The Actions workflow **could not start**, twice (original push and `gh run rerun`). GitHub's
annotation, verbatim:

    The job was not started because your account is locked due to a billing issue.

That is a startup-level refusal, not a bad workflow file: the job died in **6 seconds with zero
steps**, and its log blob does not exist (`BlobNotFound`). It is unrelated to the artifact, which
is a static file with no build step.

**The publish still succeeded**, because this repository's `build_type` is `legacy`: GitHub Pages
rebuilt the site from the `main` branch on the same push. The legacy builder is not an Actions job,
so the billing flag does not stop it. Both deployments of commit `0b0908e` were created, and
`pages/builds/latest` reported `built` at 19:08:25Z — before the first curl.

This **contradicts the standing guidance** from the 2026-10-22 record (which switched this repo
*to* Actions after the legacy builder wedged) and from the publish skill (which says to switch *to*
Actions when legacy wedges). Today the correct response was the opposite: **when Actions reports
a startup failure, check `build_type` and the Pages build status before touching the workflow** —
the legacy builder may already have published the push correctly. The skill has been corrected.

## Exact commands

    # 1. stage + reproduce the production build locally, before touching the host
    mkdir -p stage && cp <artifact> stage/index.html && cp <artifact> stage/latest.html
    cd stage && python3 -m http.server 8781 --bind 127.0.0.1
    curl -sS -o /tmp/live-index-local.html -w 'HTTP %{http_code} bytes=%{size_download}\n' \
      http://127.0.0.1:8781/
    cmp /tmp/live-index-local.html <artifact>          # -> identical

    # 2. publish
    gh repo clone carterlasalle/fleet-artifacts repo -- --depth 1
    cd repo
    cp <artifact> idea-board-2026-11-05.html          # dated name
    cp <artifact> index.html                          # front page
    cp <artifact> latest.html                         # stable name
    mkdir -p evidence/publish-2026-11-05
    cp <artifact> evidence/publish-2026-11-05/source.html
    cp <directive> <quotes> evidence/publish-2026-11-05/
    cp dark-render-2026-10-28.html evidence/publish-2026-11-05/previous-index.html
    (cd evidence/publish-2026-11-05 && sha256sum * > SHA256SUMS.txt)
    git add -A && git commit -m "Publish Fleet Idea Board 2026-11-05 ..." && git push origin main

    # 3. verify live
    curl -sS -D - -o /tmp/L_root.html https://carterlasalle.github.io/fleet-artifacts/
    sha256sum /tmp/L_root.html                        # -> 5e13156b...a3481, matches source

## What was verified, and how

**Local, before pushing** (server `python3 -m http.server 8781 --bind 127.0.0.1`)

| check | result |
|---|---|
| response | `HTTP 200`, **18,255 bytes** |
| vs source | `cmp` → **identical**; sha256 `5e13156b…a3481` |
| evidence path served | `HTTP 200`, 31,643 bytes, sha256 identical to the local directive |
| render, desktop 1280×1500 | dark theme, bordered panels, cards and tables all draw — no clipped text |
| render, mobile 390×1700 | single column, no horizontal overflow, no clipped or overlapping text |

**Live, after publishing** — `https://carterlasalle.github.io/fleet-artifacts/`

| check | result |
|---|---|
| response | `HTTP/2 200`, `server: GitHub.com`, `content-type: text/html; charset=utf-8` |
| bytes served | **18,255**; sha256 `5e13156bcbe44736523cf8cbf77734fe918cd9c53a3c3fd6f67af4df411a3481` — **matches source** |
| title | `Fleet Idea Board — 2026-11-05` |
| render, desktop 1280px | screenshot sha256 `e3038c86…` — **byte-identical** to the same page served locally, so the host changed nothing |
| render, mobile 390px | screenshot sha256 `753490fd…` — byte-identical to the local one |
| remote subresources in the published copy | **0** resource tags with a remote URL; **0** script tags |
| real backend path | `evidence/publish-2026-11-05/directive-2026-11-05.md` fetched over the network: `HTTP 200`, 31,643 bytes, sha256 `ee87b414…d2756e` — identical to the local file. A second correlated path, `retrieved-quotes-2026-11-05.md`, returned `HTTP 200`, 9,626 bytes |
| path checklist | `/`, `/latest.html`, `/idea-board-2026-11-05.html`, `/dark-render-2026-10-28.html`, `/evidence/publish-2026-11-05/directive-2026-11-05.md`, `.../retrieved-quotes-2026-11-05.md`, `.../SHA256SUMS.txt`, `.../source.html` — **8/8 returned 200** |
| negative control | `/does-not-exist-xyz.html` → `HTTP 404`, so the 200s mean something |
| page console | clean — the one Chrome stderr `ERROR` line is a headless D-Bus/UPower warning, not a page error |
| independent second read | the station's `web_fetch` tool returned the same live page; the served `SHA256SUMS.txt` matches the local one exactly |

The artifact is a static page with no backend, so the "one real backend path" check was satisfied by
fetching real evidence files over the network and confirming their bytes were unchanged — a stronger
check than a 200 on a static path.

## What is live in the repository

    https://github.com/carterlasalle/fleet-artifacts   (public, branch main)

| path | what it is |
|---|---|
| `index.html` | the artifact — identical bytes to `latest.html` and to the source |
| `latest.html` | the same page under a stable name |
| `idea-board-2026-11-05.html` | the same page under its dated source name |
| `dark-render-2026-10-28.html` | the previously published front page, kept in place |
| `idea-board-2026-10-17.html`, `pull-the-plug.html` | earlier fleet artifacts, still reachable |
| `evidence/publish-2026-11-05/` | source copy, full directive, fetched quotes, previous front page, `SHA256SUMS.txt` |
| `publish-record-2026-11-05.html` | this publish's standalone record page |
| `PUBLISH-RECORD.md` | this file |
| `.github/workflows/pages.yml` | unchanged — and currently unable to run |

Commit: `0b0908e` on `main`.

## Settings the Commander must apply

**One real item, and it is a GitHub account setting only the Commander can act on:**

1. **Clear the GitHub billing flag.** GitHub reports the account is *"locked due to a billing issue"*,
   which is why no Actions job can start. Until it is cleared the site keeps rebuilding through the
   legacy Pages builder, which still works — **nothing about the live URL is broken today**. But every
   Actions-based routine on this account is silently dead, and that is worth knowing before it matters.

Two notes, not blockers:

2. The repository is **public**. A public Pages URL cannot be private on a free plan; say the word and
   I will unpublish instead.
3. No credential was needed from the Commander for this publish. The `gh` CLI was already authenticated
   on this machine. If a different host is wanted later (netlify / vercel / wrangler), that is a
   one-time interactive sign-in only the Commander can perform.

## Nothing was faked

Every number above came from a command run during this publish. The live body was compared to the
source by sha256, not by eye. The one route that actually failed is recorded with GitHub's exact
error text rather than smoothed over. Source artifacts were **read-only**: copied, never modified.

## Evidence files

    publish-2026-11-05/shots/local-desktop.png     local render, 1280px
    publish-2026-11-05/shots/local-390.png         local render, 390px
    publish-2026-11-05/shots/live-desktop.png      LIVE render, 1280px (byte-identical to local)
    publish-2026-11-05/shots/live-390.png          LIVE render, 390px (byte-identical to local)
    publish-2026-11-05/shots/live-dom.html         live DOM dumped from the network
    publish-2026-11-05/shots/record-offline.png    the record page rendered with the network cut
    publish-2026-11-05/build_record.py             generator for the standalone record page
    publish-2026-11-05/publish-record-2026-11-05.html   the standalone offline record
