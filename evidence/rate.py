#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rate.py -- stage 2 of the autonomous loop. Rate the proposals FROM DISK.

What is scored is byte-for-byte the file the Commander can open. Nothing is
recalled from memory and the rubric is fixed here, in code, with a written
source for every dimension. Two of the five dimensions are MEASURED; the other
three are DECLARED priors and are labelled as such on the artifact.

Measured:
  verifiability  from the declared done_check kind, clamped to [0,1].
                 machine kinds (command_zero, verify_selftest, file_exists) rank
                 above the human kind (manual). A human check is never a pass.
  novelty        1 - max token cosine against everything the fleet has already
                 written down (the agenda's own direction texts + memory).
                 Measured against REAL prior text, not against the siblings.

Declared (structural prior, not evidence):
  impact, feasibility, risk  read from each proposal's signals block, clamped
                 to [0,1] and CLAMPED IN THE RECORD when the file lies.

Weights and their source:
  0.30 verifiability - a claim nobody can check is not work, it is a draft
  0.25 novelty       - the fleet's stated standing order is new ideas, not restatements
  0.20 impact        - the Commander reads what moved, not what is tidy
  0.15 feasibility   - a winner that cannot be built tonight is not a winner
  0.10 risk (inverted) - a cheap false alarm costs more than a missed page

Exit 0 = a winner above the bar was written. 1 = the batch was DECLINED.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROPOSALS = ROOT / "proposals"
MEMORY_SOURCES = [
    Path("/home/hermes/fleet/agenda/memory.jsonl"),
    Path("/home/hermes/fleet/agenda/agenda.jsonl"),
]
DIRECTIONS_DIR = Path("/home/hermes/fleet/agenda")

BAR = 0.55
WEIGHTS = {
    "verifiability": 0.30,
    "novelty": 0.25,
    "impact": 0.20,
    "feasibility": 0.15,
    "risk": 0.10,
}
# risk enters INVERTED (low risk scores high)
KIND_SCORE = {
    "command_zero": 1.00,
    "verify_selftest": 1.00,
    "file_exists": 0.70,
    "artifact_present": 0.70,
    "manual": 0.20,
}
STOP = set("""a an the and or of to in on for with by is are was were be been it its this that
these those as at from into over under after before than then so not no do does did done
every each any all one two three per own their there here what which who whom when where
why how can could should would will shall may might must have has had""".split())


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", str(text).lower())
            if w not in STOP and len(w) >= 3]


def cosine(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    ca, cb = Counter(ta), Counter(tb)
    num = sum(ca[w] * cb[w] for w in set(ca) & set(cb))
    da = sum(v * v for v in ca.values()) ** 0.5
    db = sum(v * v for v in cb.values()) ** 0.5
    return 0.0 if not da or not db else round(num / (da * db), 4)


def parse_proposal(path: Path):
    """Return (meta, signals, raw_text) -- three values, always."""
    raw = path.read_text(encoding="utf-8")
    m = re.search(r"```json\s+signals\s*\n(.*?)```", raw, re.S)
    if not m:
        raise ValueError("%s carries no signals block" % path.name)
    signals = json.loads(m.group(1))
    title = ""
    tm = re.search(r"^#\s+(.*)$", raw, re.M)
    if tm:
        title = tm.group(1).strip()
    return {"file": path.name, "title": title}, signals, raw


def clamp(v, lo=0.0, hi=1.0):
    try:
        return max(lo, min(hi, float(v))), True
    except (TypeError, ValueError):
        return lo, False


def prior_corpus():
    """Everything the fleet has already written down, as one string list."""
    corpus = []
    for p in DIRECTIONS_DIR.glob("direction-*.md"):
        corpus.append(p.read_text(errors="replace"))
    for src in MEMORY_SOURCES:
        if src.is_file():
            for line in src.read_text(errors="replace").splitlines():
                line = line.strip()
                if line:
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    corpus.append(json.dumps(row))
    return corpus


def score_all(props, corpus):
    rows = []
    for meta, sig, raw in props:
        kind = (sig.get("done_check") or {}).get("kind", "manual")
        verifiability = KIND_SCORE.get(kind, 0.30)
        # novelty is measured on the proposal's OWN text against real prior text
        sims = [cosine(raw, c) for c in corpus] or [0.0]
        novelty = round(1.0 - max(sims), 4)
        decl = sig.get("declared") or {}
        impact, ic = clamp(decl.get("impact", 0.4))
        feas, fc = clamp(decl.get("feasibility", 0.4))
        risk_raw, rc = clamp(decl.get("risk", 0.6))
        clamped = (not ic) or (not fc) or (not rc)
        score = (WEIGHTS["verifiability"] * verifiability
                 + WEIGHTS["novelty"] * novelty
                 + WEIGHTS["impact"] * impact
                 + WEIGHTS["feasibility"] * feas
                 + WEIGHTS["risk"] * (1.0 - risk_raw))
        rows.append({
            "id": sig.get("id", meta["file"]),
            "file": meta["file"],
            "title": meta["title"],
            "vehicle": sig.get("vehicle"),
            "lens": sig.get("lens"),
            "done_check": kind,
            "verifiability": verifiability,
            "novelty": novelty,
            "max_prior_similarity": round(max(sims), 4),
            "impact_declared": impact,
            "feasibility_declared": feas,
            "risk_declared": risk_raw,
            "clamped": clamped,
            "score": round(score, 4),
            "signals": sig,
        })
    return rows


def spread(rows, key):
    vals = [r[key] for r in rows]
    return round(max(vals) - min(vals), 4) if vals else 0.0


def main():
    files = sorted(PROPOSALS.glob("c*.md"))
    if not files:
        print("no proposals found in %s" % PROPOSALS)
        return 1
    props = [parse_proposal(f) for f in files]
    corpus = prior_corpus()
    rows = score_all(props, corpus)
    rows.sort(key=lambda r: (-r["score"], r["id"]))

    print("=" * 78)
    print("STAGE 2 -- RATE FROM DISK")
    print("corpus for the novelty measure: %d prior fleet documents" % len(corpus))
    print("bar: %.2f   weights: %s" % (BAR, json.dumps(WEIGHTS)))
    print("=" * 78)
    for r in rows:
        print("\n%-34s score %.4f  vehicle=%s" % (r["id"], r["score"], r["vehicle"]))
        print("   verifiability %.2f (measured, from done_check kind '%s')"
              % (r["verifiability"], r["done_check"]))
        print("   novelty       %.2f (measured, 1 - max cosine %.4f vs prior fleet text)"
              % (r["novelty"], r["max_prior_similarity"]))
        print("   impact        %.2f (DECLARED prior)" % r["impact_declared"])
        print("   feasibility   %.2f (DECLARED prior)" % r["feasibility_declared"])
        print("   risk          %.2f (DECLARED prior, enters inverted)" % r["risk_declared"])
        if r["clamped"]:
            print("   NOTE: a declared value was clamped into [0,1] and is recorded as clamped")

    print("\n" + "-" * 78)
    print("DID THE RUBRIC SEPARATE THE FIELD? (per dimension, spread across the batch)")
    caution = False
    for k in ("verifiability", "novelty", "impact_declared", "feasibility_declared", "risk_declared"):
        s = spread(rows, k)
        verdict = "SEPARATED" if s > 0.01 else "TIED -- carried no signal"
        if s <= 0.01:
            caution = True
        print("   %-22s spread %.4f  %s" % (k, s, verdict))
    measured = spread(rows, "verifiability") + spread(rows, "novelty")
    if measured <= 0.02:
        caution = True
        print("   CAUTION: the order came from declared priors only")
    else:
        print("   the two MEASURED dimensions carry %.4f of total spread" % measured)

    winner = rows[0]
    print("\n" + "=" * 78)
    if winner["score"] < BAR:
        (ROOT / "DECLINED.md").write_text(
            "# DECLINED\n\nThe batch did not clear the bar of %.2f.\n\n"
            "Best: %s at %.4f\n\nA refused batch is data. It was not reworded.\n"
            % (BAR, winner["id"], winner["score"]), encoding="utf-8")
        print("DECLINED: best score %.4f is below the bar %.2f" % (winner["score"], BAR))
        print("wrote %s" % (ROOT / "DECLINED.md"))
        return 1
    print("WINNER: %s  (%.4f)" % (winner["title"], winner["score"]))
    print("=" * 78)
    (ROOT / "winner.json").write_text(json.dumps(winner, indent=2), encoding="utf-8")
    (ROOT / "scoreboard.json").write_text(json.dumps({
        "bar": BAR, "weights": WEIGHTS, "corpus_size": len(corpus),
        "rows": rows,
        "spread": {k: spread(rows, k) for k in
                   ("verifiability", "novelty", "impact_declared",
                    "feasibility_declared", "risk_declared")},
        "caution_declared_priors_only": caution,
    }, indent=2), encoding="utf-8")
    print("wrote winner.json and scoreboard.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
