# PUBLISH RECORD — Pull the Plug, dark render 2026-10-28

**Published:** 2026-10-29 · **Agent:** deployer (StarNet) · **Status:** PUBLISHED AND VERIFIED

## The live address

    https://carterlasalle.github.io/fleet-artifacts/

Verified 2026-10-29T18:03Z: `HTTP/2 200`, 27,794 bytes served, live body **byte-identical**
to the source file (sha256 `e3969e1ef89caf3dd512a23f1c85ad066dfae4a0243935b97012b7696ed78d39`),
and the same page re-read independently at `latest.html` with identical content.

## What was published

| | |
|---|---|
| artifact | `dark-render-2026-10-28.html` — titled **"Pull the Plug — does every page still draw with the cable out?"** |
| source | `/home/hermes/fleet/rooms/software/workspace/artifacts/dark-render-2026-10-28.html` |
| produced | 2026-10-28 10:06 by the software room, StarNet v0.13.1-dirty |
| size | 27,794 bytes |
| sha256 | `e3969e1ef89caf3dd512a23f1c85ad066dfae4a0243935b97012b7696ed78d39` |
| why this one | it is the **newest finished artifact on the station** (2026-10-28, newer than every other file under `rooms/*/workspace/artifacts/`), and it is genuinely self-contained: zero `<script>` tags, zero unescaped `<link>`, `<img>` or `<iframe>` — every `https://` string in it is escaped text inside the report body, not a resource reference |

The finding it reports: 0 of 11 pages in the sample root draw with the network genuinely
unreachable; 11 do not; 10 also fail the move test. The tool launches Chrome with every
hostname unresolvable (`--host-resolver-rules="MAP * ~NOTFOUND" --proxy-server=127.0.0.1:1`)
and reads back what the browser actually attempted to fetch. It carries its own negative
control and its own falsification section, including the honest limit that a passing
citation is not proof the citation was followed.

## Files in the repository

| path | what it is |
|---|---|
| `index.html` | the artifact — identical bytes to `latest.html` and to the source |
| `latest.html` | the same page under a stable name |
| `dark-render-2026-10-28.html` | the same page under its dated source name |
| `pull-the-plug.html` | the 2026-10-09 predecessor, kept in place |
| `idea-board-2026-10-17.html` | the previously front-paged artifact, kept in place |
| `evidence/publish-2026-10-29/` | source copy, previous index, sha256 sums |
| `.github/workflows/pages.yml` | the Actions deploy pipeline serving this site |

## Route used, and why

GitHub Pages, branch `main`, path `/`, HTTPS enforced, repo public. Driven by the
already-authenticated `gh` CLI (account `carterlasalle`, scopes include `repo`) — no
interactive login was required.

Routes checked on this host before the publish:

| route | state on 2026-10-29 |
|---|---|
| `gh` / GitHub Pages | **authenticated** — used |
| `vercel` CLI | not installed on PATH |
| `wrangler` CLI | not installed on PATH |
| `cloudflared` | installed, but the tunnel's ingress hostnames live in the Cloudflare dashboard with no API token on the box — cannot make a public hostname without the Commander |

## Settings the Commander must apply

None. The publish is public and verified as it stands. Two notes, not blockers:

1. The repository is **public**. A public Pages URL cannot be private on a free plan.
2. The site deploys from a **GitHub Actions workflow** (Settings → Pages → Source reads
   "GitHub Actions"). No action needed unless the Commander prefers the legacy builder.

## Nothing was faked

Live response headers and the served body were fetched over the network and compared by
sha256 against the source file; they match. Source artifacts were **read-only**: copied,
never modified. The one class of route that was unavailable (an authenticated static host
beyond GitHub) is recorded above with its exact state rather than reported as a success.
