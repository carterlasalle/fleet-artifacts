#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_artifact.py -- stage 6/7 verification of the SHIPPED bytes.

Not the builder's opinion. This reads the artifact the Commander would open off
disk, plus the receipt the scan wrote, and holds them to declared invariants.
Then it falsifies itself: each check is re-run against a deliberately corrupted
copy and MUST fail. A check that cannot fail proves nothing.

Invariants (each named; each must hold):
  I1  the page's first heading equals the receipt's verdict line, character for character
  I2  I1's count equals the receipt's page total and clean total
  I3  the artifact loads nothing from the network (subresource scan)
  I4  the artifact renders with the network blackholed (real browser)
  I5  the artifact has no horizontal overflow at a 390px viewport
  I6  the artifact's named broken list equals the receipt's broken list
  I7  the verdict signature in the page equals the receipt's signature
Usage: python3 verify_artifact.py --page <artifact.html> --receipt <receipt.json>
Exit 0 = every invariant holds AND every declared fault was caught.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VW = 390
HERE = Path(__file__).resolve().parent


def subresources(html):
    """Remote references that a browser FETCHES to draw the page."""
    hits = []
    for m in re.finditer(r"<(img|script|iframe|source|video|audio|embed|object|link)\b([^>]*)>",
                         html, re.I | re.S):
        tag = m.group(1).lower()
        attrs = m.group(2) or ""
        for a in re.finditer(r"""(src|href|data|poster)\s*=\s*(["'])(.*?)\2""", attrs, re.I | re.S):
            val = a.group(3).strip()
            if not (val.startswith("http://") or val.startswith("https://") or val.startswith("//")):
                continue
            if tag == "link":
                rel = re.search(r"""rel\s*=\s*["'](.*?)["']""", attrs, re.I)
                r = (rel.group(1).lower() if rel else "")
                if not any(k in r for k in ("stylesheet", "preload", "prefetch", "icon", "manifest")):
                    continue
            hits.append("%s %s=%s" % (tag, a.group(1), val))
    for s in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.I | re.S):
        for u in re.finditer(r"url\(\s*['\"]?(https?://|//)", s.group(1), re.I):
            hits.append("style url()=%s" % u.group(1))
    for i in re.finditer(r"@import\s+(?:url\()?['\"]?(https?://|//)", html, re.I):
        hits.append("@import %s" % i.group(1))
    return hits


def first_heading(html):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()


def runs(chrome, page, dark):
    """Open a page and report its scrollWidth and the remote refs it tried."""
    tmp = Path(tempfile.mkdtemp(prefix="va-"))
    try:
        h = tmp / "_h.html"
        h.write_text("""<!doctype html><meta charset="utf-8">
<style>html,body{margin:0}#f{border:0;width:%(vw)dpx;height:844px}</style>
<iframe id="f" src="%(src)s"></iframe><div id="__o">pending</div>
<script>window.addEventListener('load',function(){setTimeout(function(){
 var w=document.getElementById('f').contentWindow,d=w.document,de=d.documentElement;
 var res=[];try{var e=w.performance.getEntriesByType('resource')||[];
 for(var i=0;i<e.length;i++){res.push({url:e[i].name,status:e[i].responseStatus||0,
 transfer:e[i].transferSize||0});}}catch(x){}
 document.getElementById('__o').textContent=JSON.stringify({vw:de.clientWidth,
 sw:de.scrollWidth,res:res,text:(d.body?d.body.innerText:'')});
},2500);});</script>""" % {"vw": VW, "src": page.resolve().as_uri()}, encoding="utf-8")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
               "--allow-file-access-from-files", "--disable-extensions"]
        if dark:
            cmd += ["--host-resolver-rules=MAP * ~NOTFOUND", "--proxy-server=127.0.0.1:1"]
        cmd += ["--virtual-time-budget=8000", "--window-size=%d,900" % VW,
                "--dump-dom", h.resolve().as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        m = re.search(r'<div id="__o">(.*?)</div>', r.stdout or "", re.S)
        if not m or m.group(1).strip() == "pending":
            return None
        raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
               .replace("&lt;", "<").replace("&gt;", ">").replace("&#x27;", "'"))
        return json.loads(raw)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_all(page_path, receipt, chrome):
    """Every invariant, evaluated against the SHIPPED page + receipt."""
    html = Path(page_path).read_text(encoding="utf-8")
    out = {}
    out["I1_heading_equals_receipt_verdict_line"] = (
        first_heading(html) == receipt["verdict_line"])
    m = re.search(r"(\d+)\s+of\s+(\d+)\s+pages", first_heading(html))
    out["I2_heading_counts_equal_receipt_counts"] = bool(
        m and int(m.group(2)) == receipt["pages"] and int(m.group(1)) == receipt["clean"])
    subs = subresources(html)
    out["I3_no_network_subresources"] = (len(subs) == 0)
    out["I3_detail"] = subs
    live = runs(chrome, Path(page_path), dark=True)
    out["I4_renders_blackholed"] = bool(live and live.get("text"))
    remote_tried = [r["url"] for r in (live or {}).get("res", [])
                    if r["url"].startswith(("http://", "https://"))]
    out["I4_remote_refs_attempted"] = remote_tried
    out["I5_no_overflow_at_390px"] = bool(live and live["sw"] <= live["vw"] + 1)
    out["I5_detail"] = {"viewport": (live or {}).get("vw"),
                        "scrollWidth": (live or {}).get("sw")}
    # the page must account for EXACTLY the broken pages the receipt names.
    # Counting only the "DENIED IN THE DARK" rows made this invariant vacuously
    # true: with an empty broken list, renaming the marker broke nothing. The
    # honest count is: rows the page marks BROKEN must equal the receipt's list,
    # and every one of them must actually be named there.
    marked = sorted(set(re.findall(r'<div class="row [^"]*"><div class="p">'
                                   r'<span class="tag">BROKEN</span>\s*([^<]+)</div>', html)))
    denied = sorted(set(re.findall(r"DENIED IN THE DARK:\s*([^<]+)</div>", html)))
    out["I6_marked_broken_equals_receipt_broken"] = (
        marked == sorted(receipt["broken"]) and denied == sorted(receipt["broken"]))
    out["I6_named"] = {"marked_broken": marked, "denied_rows": denied}
    out["I3b_no_broken_marker_without_a_denial"] = (
        bool(marked) == bool(denied))
    sig_in_page = re.search(r"<code>(\[.*?\])</code>", html, re.S)
    page_sig = re.sub(r"\s+", "", sig_in_page.group(1)) if sig_in_page else ""
    out["I7_signature_matches_receipt"] = (
        page_sig == re.sub(r"\s+", "", receipt["signature"]))
    return out


def corrupt(page_html, kind):
    """Declared faults. Each must make its named invariant FAIL."""
    if kind == "f1-wrong-count":
        return re.sub(r"(\d+)( of \d+ pages draw)", lambda m: str(int(m.group(1)) - 1) + m.group(2),
                      page_html, count=1)
    if kind == "f2-inject-remote-script":
        return page_html.replace("</body>", '<script src="https://cdn.example/x.js"></script></body>', 1)
    if kind == "f3-widen":
        return page_html.replace("max-width:940px", "max-width:2000px;width:2000px", 1)
    if kind == "f4-false-broken-row":
        # a page the receipt says is CLEAN, silently re-tagged BROKEN. The receipt
        # is the record; the page contradicts it; that must be caught.
        return page_html.replace('<span class="tag">CLEAN</span>',
                                 '<span class="tag">BROKEN</span>', 1)
    if kind == "f5-break-signature":
        # target the signature block by ANCHOR (the <code>[ ... ]</code> block),
        # never by a literal that a schema change can silently invalidate. The
        # first version anchored on '[{"page"' and, after the signature was made
        # sort_keys, matched nothing -- so this mutant was a NO-OP that got
        # reported as an escaped fault. A no-op is a harness defect and the
        # caller now checks for it.
        def swap(m):
            inner = m.group(1)
            return m.group(0).replace(inner, inner.replace("CLEAN", "XLEAN", 1), 1)
        return re.sub(r"<code>(\[.*?\])</code>", swap, page_html, count=1, flags=re.S)
    if kind == "control-inert":
        return page_html.replace("max-width:940px", "max-width: 940px", 1)
    raise ValueError(kind)


# name -> (mutant kind, the ONE invariant it must break)
MUTANTS = {
    "wrong count in the first line": ("f1-wrong-count", "I1_heading_equals_receipt_verdict_line"),
    "a remote script injected into the page": ("f2-inject-remote-script", "I3_no_network_subresources"),
    "the page widened past 390px": ("f3-widen", "I5_no_overflow_at_390px"),
    "a page falsely marked BROKEN with no denial": ("f4-false-broken-row", "I6_marked_broken_equals_receipt_broken"),
    "the signature mangled": ("f5-break-signature", "I7_signature_matches_receipt"),
}
CONTROLS = {"an inert whitespace change (must escape)": ("control-inert", None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()
    chrome = "/usr/bin/google-chrome"
    page = Path(args.page)
    receipt = json.loads(Path(args.receipt).read_text())

    print("=" * 74)
    print("STAGE 6 -- INVARIANTS ON THE SHIPPED BYTES")
    print("page:    %s (%d bytes)" % (page, page.stat().st_size))
    print("receipt: %s" % args.receipt)
    print("=" * 74)
    res = check_all(page, receipt, chrome)
    failures = []
    for k in sorted(res):
        if k.endswith(("_detail", "_named")) or k.startswith("I4_remote"):
            continue
        ok = res[k]
        print("  %-52s %s" % (k, "PASS" if ok else "FAIL"))
        if not ok:
            failures.append(k)
    print("  detail: overflow=%s  remote_attempted=%s  named_broken=%s"
          % (res.get("I5_detail"), res.get("I4_remote_refs_attempted"), res.get("I6_named")))

    print("\n" + "=" * 74)
    print("STAGE 7 -- FALSIFY THE VERIFIER (each fault must be CAUGHT)")
    print("=" * 74)
    src = page.read_text(encoding="utf-8")
    tmpdir = Path(tempfile.mkdtemp(prefix="vf-"))
    escaped = []
    try:
        for label, (kind, owner) in MUTANTS.items():
            mut = tmpdir / "mut.html"
            mutated = corrupt(src, kind)
            if mutated == src:
                # an identical mutation is a mutation that does not exist. Report
                # it as a harness defect rather than as a fault that got through.
                print("  %-46s %s" % (label, "NO-OP MUTATION -- anchor did not match "
                                             "(harness defect, not a finding)"))
                escaped.append(label + " [no-op mutation: the anchor no longer matches]")
                continue
            mut.write_text(mutated, encoding="utf-8")
            if kind == "f3-widen":
                live = runs(chrome, mut, dark=True)
                broke = not (live and live["sw"] <= live["vw"] + 1)
                detail = live and "%s>%s" % (live["sw"], live["vw"])
            else:
                r2 = check_all(mut, receipt, chrome) if kind != "f2-inject-remote-script" else {
                    "I3_no_network_subresources": len(subresources(mut.read_text())) == 0}
                broke = not r2.get(owner, True)
                detail = r2.get(owner)
            print("  %-46s owner=%-46s %s  (owner tripped=%s)"
                  % (label, owner, "CAUGHT" if broke else "ESCAPED", broke))
            if not broke:
                escaped.append(label)
        for label, (kind, _owner) in CONTROLS.items():
            mut = tmpdir / "ctl.html"
            mutated = corrupt(src, kind)
            mut.write_text(mutated, encoding="utf-8")
            r2 = check_all(mut, receipt, chrome)
            broke = [k for k in r2 if k.startswith("I")
                     and not k.endswith(("_detail", "_named")) and r2[k] is False]
            print("  %-46s %s  (invariants broken=%s)"
                  % (label, "CONTROL PASS" if not broke else "CONTROL CAUGHT (BAD)", broke))
            if broke:
                escaped.append(label + " [control was caught -- harness reports faults that are not there]")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("\n" + "=" * 74)
    if failures or escaped:
        print("VERDICT: FAIL")
        for f in failures:
            print("   invariant failed: %s" % f)
        for e in escaped:
            print("   escaped/control: %s" % e)
        return 1
    print("VERDICT: PASS -- %d invariant(s) hold on the shipped bytes; "
          "%d declared fault(s) caught; %d control(s) escaped cleanly"
          % (len([k for k in res if k.startswith("I")
                  and not k.endswith(("_detail", "_named"))]),
             len(MUTANTS), len(CONTROLS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
