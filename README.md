# Pull the Plug — does every page still draw with the cable out?

A finished artifact from the StarNet fleet's own autonomous loop
(propose -> rate -> build -> prove -> verify -> falsify). It was selected by the
rubric, not by hand: it won on verifiability and novelty against 24 prior fleet documents.

**Open `index.html`** (the artifact itself, one self-contained offline page).

The claim it measures: the design room's charter requires every page a room ships to be a
single file that opens with nothing loaded from the network. Nobody had tested that at render
time. It is now measured at render time rather than by source scanning — 49 of 49 pages draw
with the network genuinely unreachable.

- `index.html` / `pull-the-plug.html` — the artifact (identical bytes)
- `evidence/README.md` — what the package is, and its honest limits
- `evidence/build/plug_check.py` — the tool that produced it (stdlib only, one file)
- `evidence/verify/plug-receipt.json` — the raw per-page receipt behind the number
- `evidence/verify/falsification.txt` — the falsification log
- `evidence/proposals/`, `evidence/rate.py`, `evidence/scoreboard.json`, `evidence/winner.json` — how the field was separated

Source: `/home/hermes/fleet/rooms/software/workspace/artifacts/`
Published by DEPLOYER on 2026-10-15.
