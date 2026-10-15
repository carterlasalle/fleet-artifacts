# PULL THE PLUG — README

Built 2026-10-09 by the fleet's own autonomous loop (propose → rate → build → prove → verify → falsify).
Chosen by the rubric, not by hand: it won on verifiability and novelty against 24 prior fleet documents.

## The one sentence

The design room's charter says every page a room ships must be a single file that opens
with nothing loaded from the network. Nobody had ever tested that at render time. Now it is
measured: **49 of 49 pages draw with the network genuinely unreachable; 6 also fail the move test.**

## Open this

| file | what it is |
|---|---|
| `../dark-render-2026-10-09.html` | **the artifact.** One page, offline-safe, verdict-first, clean at 390px |
| `build/plug_check.py` | the tool that produced it — stdlib only, one file |
| `verify/plug-receipt.json` | the raw per-page receipt behind the number |
| `verify/falsification.txt` | the falsification log: 11 defects found and fixed, and what is still unproven |
| `proposals/` | the three blind candidates (c1, c2, c3) and the signals each carried |
| `rate.py`, `scoreboard.json`, `winner.json` | the rubric, fixed in code, and how it separated the field |

## Run it yourself

    python3 build/plug_check.py --selftest     # 33 checks on the shipped bytes
    python3 build/plug_check.py --scan         # re-do the whole census, ~3 minutes

## What it does that a regex cannot

Two things look identical in the source and are completely different to a browser:

| reference | fetched to DRAW the page? | offender? |
|---|---|---|
| `<img src>`, `<script src>`, `<link rel=stylesheet>`, CSS `@import`, `url()` | yes — a fail here breaks the page | **YES** |
| `<a href>` to a source URL | no — only if the reader clicks | **NO** |

A source scanner cannot tell them apart, so it either flags the fleet's most honest pages
(the ones that cite sources) as broken, or it misses a real one. Unless it is very careful,
it also flags the page that *documents* the difference — that happened here (D9).

So this tool stops reading the source for the verdict. It launches Chrome with every hostname
unresolvable and no proxy:

    --host-resolver-rules="MAP * ~NOTFOUND" --proxy-server=127.0.0.1:1

loads the page, and reads back what the browser actually tried to fetch and what came back
empty (`responseStatus:0`, `transferSize:0`). A page is broken only when a subresource it
**succeeded with the network up and was denied with it down**. The blackout itself was
proven before any fleet page was loaded: light run reports NET-REACHABLE, dark run reports
NET-BLOCKED, and a page reaching a LOCAL dev server is caught too — so the flags blackhole
loopback, not just the public internet.

## The finding you can act on

Six pages reference a sibling file (`style.css`, `app.js`) rather than standing alone:

    engineer/blog/site/index.html
    engineer/blog/site/project-notes.html
    engineer/blog/site/second-test.html
    engineer/edge_selfcontained.html
    engineer/edge_test/edge_selfcontained.html
    agent/novelty-agenda-20261008/fleet-agenda.html

For a page inside a `site/` folder this is correct and expected. For anything the design
charter requires to be a single self-contained file, it is the one thing this tool catches
that a network check alone would miss: a page that only works because it sits beside its
siblings.

## Honest limits

A citation passing this tool is not proof the citation was ever followed — or still resolves.
Rendering is not layout. A page can carry a citation to a URL that now 404s and still pass here.
The cache is disabled per browser launch, not per page. And 0 of 49 broken is a real measurement
over these two roots and this exclusion list, not a claim about any page outside them. The full
list is at the foot of `verify/falsification.txt`.

Everything here is local. Nothing was sent, published, spent or moved off this machine.
