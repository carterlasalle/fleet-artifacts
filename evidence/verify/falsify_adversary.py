#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
falsify_adversary.py -- STAGE 7. No fault list is handed to this file.

Stage 6 pinned five faults and caught them, but that list can only contain faults
its author imagined. This stage is handed a CONTRACT instead: named invariants that
must hold after every step, and it picks its own steps -- seeded, so any hole it
finds is reproducible from the printed seed.

The core under test is not a re-implementation. It is the logic module sliced
VERBATIM out of the shipped `plug_check.py`, between its own markers.

Invariants (each must hold after EVERY step):
  V1  the verdict is exactly one of CLEAN or BROKEN
  V2  BROKEN  iff  at least one URL was fetched with the network up AND denied
      with it down  (this is the tool's entire claim)
  V3  every URL named broken was in fact denied in the dark run
  V4  a URL dead in BOTH runs is never named broken (a dead URL is not an outage)
  V5  the verdict line's leading count equals total minus the broken count
  V6  the signature is stable under row reordering, and never carries a timer

Declared handed breaks (the adversary must FIND these, or report them REDUNDANT):
  H1  a page whose only remote reference is an <a href> citation is reported BROKEN
  H2  a URL dead in both runs is reported BROKEN
  H3  the verdict line's count drifts from the row count

Usage: python3 falsify_adversary.py --seed 20261009 [--steps 400]
Exit 0 = 0 blind (every break found or shown redundant), 0 violations on the clean core.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

SHIPPED = Path("/home/hermes/fleet/rooms/software/workspace/artifacts/plug_check.py")
FALLBACK = Path(__file__).resolve().parent.parent / "build" / "plug_check.py"
OPEN_MARK = "# @@PLUG-LOGIC-" + "BEGIN@@"
CLOSE_MARK = "# @@PLUG-LOGIC-" + "END@@"

HOSTS = ["cdn.example", "fonts.example", "api.example", "static.example", "img.example"]
NAMES = ["a.css", "x.js", "p.png", "w.woff2", "m.mp4", "f.svg"]


def slice_core(path):
    src = Path(path).read_text(encoding="utf-8")
    assert src.count(OPEN_MARK) == 1 and src.count(CLOSE_MARK) == 1, \
        "the shipped markers are not unique anchors -- refusing to slice"
    a, b = src.find(OPEN_MARK), src.find(CLOSE_MARK)
    assert 0 < a < b
    block = src[a:b]
    ns = {"re": re, "json": json}
    exec(compile(block, "<shipped-slice>", "exec"), ns)  # noqa: S102
    ns["_block"] = block          # the exact bytes under test, for mutation
    return ns


def rand_world(rng):
    """One random step: a page made of citations and subresources, plus what each
    URL did in the light run and the dark run. Nothing here is pinned."""
    page = []
    urls = []
    for _ in range(rng.randint(0, 4)):                      # citations
        u = "https://%s/%s" % (rng.choice(HOSTS), rng.choice(["doc", "paper", "src", "ref"]))
        page.append('<a href="%s">source</a>' % u)
        urls.append((u, "nav"))
    for _ in range(rng.randint(0, 4)):                      # subresources
        u = "https://%s/%s" % (rng.choice(HOSTS), rng.choice(NAMES))
        tag = rng.choice(["img", "script", "link", "iframe"])
        if tag == "link":
            page.append('<link rel="stylesheet" href="%s">' % u)
        else:
            page.append('<%s src="%s"></%s>' % (tag, u, tag))
        urls.append((u, "sub"))
    if rng.random() < 0.15:                                 # a local sibling file
        page.append('<script src="app.js"></script>')
    # the network: for each remote URL decide light/dark outcomes
    light, dark = [], []
    for u, kind in urls:
        if kind == "nav":
            continue                                        # never fetched to draw
        rolled = rng.random()
        if rolled < 0.45:                                   # loaded, then denied
            light.append({"url": u, "status": 200, "transfer": rng.randint(1, 9000)})
            dark.append({"url": u, "status": 0, "transfer": 0})
        elif rolled < 0.70:                                 # loaded in both (blackout failed)
            light.append({"url": u, "status": 200, "transfer": rng.randint(1, 9000)})
            dark.append({"url": u, "status": 200, "transfer": rng.randint(1, 9000)})
        else:                                               # dead in both
            light.append({"url": u, "status": 0, "transfer": 0})
            dark.append({"url": u, "status": 0, "transfer": 0})
    return "\n".join(page), {"ok": True, "resources": light}, {"ok": True, "resources": dark}


def invariants(core, page, light, dark, rows_ctx):
    """Return a list of (name, holds, detail)."""
    got = core["classify"](light, dark)
    v = got["verdict"]
    lr = {r["url"]: r for r in light["resources"]}
    dr = {r["url"]: r for r in dark["resources"]}
    fetched_light = {u for u, r in lr.items()
                     if (r.get("status", 0) or r.get("transfer", 0))}
    denied_dark = {u for u, r in dr.items()
                   if not (r.get("status", 0) or r.get("transfer", 0))}
    expected = sorted(fetched_light & denied_dark)
    out = []
    out.append(("V1_verdict_is_a_known_word", v in ("CLEAN", "BROKEN"), v))
    out.append(("V2_broken_iff_fetched_light_and_denied_dark",
                (v == "BROKEN") == bool(expected),
                "expected=%s got=%s" % (expected, got["broken"])))
    out.append(("V3_every_broken_url_was_denied_in_the_dark",
                all(u in denied_dark for u in got["broken"]), str(got["broken"])))
    out.append(("V4_a_url_dead_in_both_is_not_named_broken",
                not (set(got["broken"]) & set(got["dead_in_both"])),
                "broken=%s dead=%s" % (got["broken"], got["dead_in_both"])))
    n_rows = len(rows_ctx["rows"])
    n_broken = len([r for r in rows_ctx["rows"] if r["verdict"] == "BROKEN"])
    line = core["verdict_line"](n_rows - n_broken, n_rows,
                                [1] * n_broken, [r for r in rows_ctx["rows"] if r["moved"]])
    m = re.match(r"(\d+) of (\d+) pages", line)
    out.append(("V5_verdict_line_count_equals_total_minus_broken",
                bool(m) and int(m.group(2)) == n_rows and int(m.group(1)) == n_rows - n_broken,
                line))
    sig = core["summary_signature"](rows_ctx["rows"])
    out.append(("V6_signature_stable_under_reordering_and_carries_no_timer",
                sig == core["summary_signature"](list(reversed(rows_ctx["rows"])))
                and "cost" not in sig and "time" not in sig, sig[:60]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261009)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "falsify_report.json"))
    args = ap.parse_args()

    path = SHIPPED if SHIPPED.is_file() else FALLBACK
    core = slice_core(path)
    print("=" * 74)
    print("STAGE 7 -- ADVERSARIAL FALSIFICATION (no fault list handed in)")
    print("core sliced verbatim from: %s" % path)
    print("seed %d, %d steps" % (args.seed, args.steps))
    print("=" * 74)

    rng = random.Random(args.seed)
    violations = []
    rows_ctx = {"rows": []}
    inspected = {}
    for i in range(args.steps):
        page, light, dark = rand_world(rng)
        fetch, nav = core["split_refs"](page)
        rel = core["relative_subresources"](page)
        cls = core["classify"](light, dark)
        cls["page"] = "adv-%d" % i
        cls["moved"] = bool(rel)
        rows_ctx["rows"].append(cls)
        if len(rows_ctx["rows"]) > 12:
            rows_ctx["rows"].pop(0)
        # record the shapes this step exercised, so coverage is countable
        key = (bool(fetch), bool(nav), bool(rel), cls["verdict"])
        inspected[key] = inspected.get(key, 0) + 1
        for name, holds, detail in invariants(core, page, light, dark, rows_ctx):
            if not holds:
                violations.append({"step": i, "invariant": name, "detail": detail,
                                   "seed": args.seed})

    print("\nclean-core attack: %d step(s), %d invariant violation(s)"
          % (args.steps, len(violations)))
    for v in violations[:10]:
        print("   %s at step %d -- %s" % (v["invariant"], v["step"], v["detail"]))
    print("\nshapes exercised (subresource? citation? sibling? verdict) : count")
    for k in sorted(inspected, key=lambda x: -inspected[x]):
        print("   %-40s %d" % (str(k), inspected[k]))

    # ---- handed breaks: the adversary must FIND these, or show them redundant
    print("\n" + "-" * 74)
    print("HANDED BREAKS -- injected into the core; the invariant SUITE must catch each")
    print("-" * 74)
    # A first version of this section asked the CLEAN core to produce the breaks
    # and reported both as BLIND when it correctly did not. That was a defect in
    # the question, not a coverage hole: the honest stage-7 move is to BREAK the
    # core and see whether the declared invariants notice. The owner column names
    # the ONE invariant that must trip; a break caught by a neighbour invariant is
    # reported separately and does not count as a pass.
    BLOCK = core["_block"] if "_block" in core else None
    HANDED = [
        ("HB1 a citation is counted as a fetch",
         "V2", "        if not is_remote(url):\n            continue\n        got = r.get(\"status\", 0) or r.get(\"transfer\", 0)\n        if got:\n            remote_in_light.append(url)",
         "        if not is_remote(url):\n            continue\n        remote_in_light.append(url)"),
        ("HB2 a URL dead in both runs is named broken",
         "V4", "    broken = sorted(set(remote_in_light) & set(denied_in_dark))",
         "    broken = sorted(set(dr))"),
        ("HB3 the verdict line count drifts from the rows",
         "V5", 'line = "%d of %d pages draw with the network genuinely unreachable" % (clean, total)',
         'line = "%d of %d pages draw with the network genuinely unreachable" % (clean + 1, total)'),
        ("HB4 a timer is smuggled into the signature",
         "V6", "    ], sort_keys=True)",
         "    ] + [{\"cost\": __import__(\"time\").time()}], sort_keys=True)"),
        ("CONTROL: a local parameter renamed, changing nothing",
         "CONTROL", "def is_remote(url):", "def is_remote(url_arg__):\n    url = url_arg__"),
    ]
    results = []
    for label, owner, marker, repl in HANDED:
        hit = core["_block"].count(marker)
        if hit != 1:
            print("  %-52s ANCHOR NOT UNIQUE (%d) -- harness defect" % (label, hit))
            results.append((label + " [anchor]", False))
            continue
        mns = {"re": re, "json": json}
        err = ""
        try:
            exec(compile(core["_block"].replace(marker, repl), "<hb>", "exec"), mns)  # noqa: S102
        except Exception as exc:  # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, exc)
        tripped = set()
        if not err:
            mrng = random.Random(args.seed)
            mrows = {"rows": []}
            for _ in range(120):
                p, lt, dk = rand_world(mrng)
                c = mns["classify"](lt, dk)
                c["page"] = "hb"
                c["moved"] = bool(mns["relative_subresources"](p))
                mrows["rows"].append(c)
                if len(mrows["rows"]) > 12:
                    mrows["rows"].pop(0)
                for name, holds, _d in invariants(mns, p, lt, dk, mrows):
                    if not holds:
                        tripped.add(name.split("_")[0])
        if owner == "CONTROL":
            ok = not tripped and not err
            print("  %-52s %s  (invariants tripped=%s)"
                  % (label, "CONTROL PASS" if ok else "CONTROL CAUGHT (BAD)", sorted(tripped)))
        else:
            ok = (owner in tripped) and not err
            neighbour = sorted(tripped - {owner})
            state = "CAUGHT" if ok else ("ERROR: " + err if err else "ESCAPED")
            note = ("   (also tripped: %s -- a neighbour invariant is not the owner)"
                    % neighbour) if neighbour else ""
            print("  %-52s owner %-4s %s%s" % (label, owner, state, note))
        results.append((label, ok))

    blind = [n for n, found in results if not found]
    print("\n" + "=" * 74)
    verdict = "PASS" if (not violations and not blind) else "FAIL"
    print("%s -- %d invariant violation(s) on the clean core; "
          "%d of %d handed break(s) FOUND; %d BLIND"
          % (verdict, len(violations), len(results) - len(blind), len(results), len(blind)))
    if blind:
        print("BLIND (a real coverage hole -- nothing trips when this break is made):")
        for b in blind:
            print("   %s" % b)
    print("=" * 74)

    Path(args.out).write_text(json.dumps({
        "seed": args.seed, "steps": args.steps, "core": str(path),
        "verdict": verdict, "violations": violations,
        "handed_breaks": [{"name": n, "found": f} for n, f in results],
        "blind": blind,
        "shapes_exercised": {str(k): v for k, v in inspected.items()},
        "invariants": ["V1 verdict is a known word",
                       "V2 BROKEN iff fetched light and denied dark",
                       "V3 every broken URL was denied in the dark",
                       "V4 a URL dead in both runs is never named broken",
                       "V5 verdict line count equals total minus broken",
                       "V6 signature is order-stable and carries no timer"],
    }, indent=2), encoding="utf-8")
    print("report: %s" % args.out)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
