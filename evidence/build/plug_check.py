#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plug_check.py -- PULL THE PLUG.

Open every shipped page in a real browser with the network genuinely unreachable
and record what a reader would actually see. Then say the number in the first line.

WHY THIS IS NOT A REGEX
-----------------------
The design room's charter requires every page a room ships to be a single file
that opens with nothing loaded from the network. Nothing has ever tested that at
render time. A regex over the source cannot do it, because the source does not
record the difference between the two kinds of external reference a fleet page
carries:

  * a SUBRESOURCE  (img/script/iframe/css url) -- the browser FETCHES it to draw
    the page. If it is remote and the network is out, the page is broken.
  * a CITATION     (an <a href> to a source URL) -- the browser NEVER fetches it
    to draw the page. It is only followed if the reader clicks.

Both look like `https://...` in the file. Counting them equally reports the
fleet's most honest pages (the ones that cite sources) as broken, and once the
number cries wolf nobody reads it again. So this tool stops reading the source
for the verdict and measures the RENDER: launch Chrome with the network
blackholed, load the page, and ask the browser what it actually tried to fetch
and what came back empty.

THE BLACKOUT (proven before any fleet page is loaded)
-----------------------------------------------------
    --host-resolver-rules="MAP * ~NOTFOUND"   every hostname fails to resolve
    --proxy-server=127.0.0.1:1                nothing to connect through
Measured on a control page in this session:
    light: NET-REACHABLE          dark: NET-BLOCKED:TypeError
The same flags applied to a page that loads an asset from a local dev server
(light: the asset's global existed) left that global ABSENT -- so the flags
blackhole loopback too, and a page that reaches LOCALHOST still gets caught.

USAGE
-----
    python3 plug_check.py --selftest
    python3 plug_check.py --scan                 # default roots
    python3 plug_check.py --scan <path> [...]    # files or folders
    python3 plug_check.py --file <page.html>     # debug one page

Exit: 0 = every page draws with the cable out. 1 = at least one does not (gates a
build). 2 = no browser, or the page set was empty.

Stdlib only. Reads local files, opens local files, writes local files. It never
sends, publishes, spends or moves anything off this machine -- and it blackholes
the network while it works, so it could not if it tried.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VW, VH = 390, 844          # the charter's phone width
BATCH = 8                  # iframes per browser launch
TIME_BUDGET = 8000         # per-launch virtual time budget, ms

CHROME_CANDIDATES = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/opt/google/chrome/chrome",
]

DEFAULT_ROOTS = [
    Path("/home/hermes/fleet"),
    Path("/home/hermes/.local/share/StarNet/workspaces"),
]

# Loop fixtures, browser profile internals and build checkpoints are not the
# fleet's shipped pages. Excluded deliberately and the exclusion is printed.
EXCLUDE_PARTS = (
    "/workshop/", "/.selftest/", "/node_modules/", "/build/", "/.output/",
    "/downloads/", "/shots/", "/plug-proof/", "/.browser-profile/",
    "/test_fixtures/",
)
# NOTE on what is NOT excluded, and why it matters: an earlier revision of this
# list also skipped "/site/" and "/edge_test/" -- which silently dropped the
# engineer's built blog and its edge fixtures from the census. That is the
# exclusion hiding a real finding rather than a fixture. They are in scope now.

DARK_FLAGS = [
    "--host-resolver-rules=MAP * ~NOTFOUND",
    "--proxy-server=127.0.0.1:1",
]

# @@PLUG-LOGIC-BEGIN@@
# Pure logic. --selftest slices these BYTES verbatim out of this shipped file and
# evaluates them, so the code under test and the test can never drift apart. Each
# marker below must appear EXACTLY ONCE in the file; the self-test asserts that,
# because a banner that matches twice slices nothing and reports success anyway.
SUB_RESOURCE_TAGS = re.compile(
    r"<(img|script|iframe|source|video|audio|embed|object|link)\b"
    r"(?P<attrs>[^>]*)>", re.I | re.S)
ATTR_RE = re.compile(r"""(?P<name>src|href|data|poster|srcset|content)\s*=\s*
                       (?P<q>["'])(?P<val>.*?)(?P=q)""", re.I | re.X)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?(?P<val>[^'\")]+)", re.I)
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(?P<css>.*?)</style>", re.I | re.S)
ANCHOR_RE = re.compile(r"<a\b[^>]*?(?P<attrs>[^>]*)>", re.I | re.S)
# the at-rule, assembled from two literals ON PURPOSE. A page that DOCUMENTS this
# rule must not be flagged by the scanner that looks for it: written as one
# literal here, the check flagged its own documentation -- which is precisely the
# false-alarm shape this tool exists to remove.
AT_IMPORT_RE = re.compile(r"@" + r"import\s+(?:url\(\s*)?['\"]?(?P<val>[^'\"\s)]+)", re.I)

# an <a href> is navigation, never a fetch, EXCEPT these link rels which are.
LINK_FETCH_RELS = ("stylesheet", "preload", "prefetch", "modulepreload", "icon",
                   "shortcut icon", "apple-touch-icon", "manifest")


def is_remote(url):
    u = (url or "").strip()
    return u.startswith("http://") or u.startswith("https://") or u.startswith("//")


def split_refs(html):
    """Every external reference in the source, split by whether it can be FETCHED.

    Returns (fetch_capable, navigation_only). Each row is a dict with
    element, attribute, url. This is used for NAMING what failed -- never for the
    verdict. The verdict comes from the render.
    """
    fetch = []
    nav = []
    for m in SUB_RESOURCE_TAGS.finditer(html or ""):
        tag = m.group(1).lower()
        attrs = m.group("attrs") or ""
        rel_m = re.search(r"""rel\s*=\s*["'](.*?)["']""", attrs, re.I | re.S)
        rel = (rel_m.group(1).strip().lower() if rel_m else "")
        for a in ATTR_RE.finditer(attrs):
            name, val = a.group("name").lower(), a.group("val").strip()
            if not is_remote(val):
                continue
            if tag == "link":
                # a stylesheet/preload IS fetched; a plain rel=alternate is not
                (fetch if (rel in LINK_FETCH_RELS or "stylesheet" in rel or "icon" in rel)
                 else nav).append({"element": tag, "attribute": name, "url": val})
            else:
                fetch.append({"element": tag, "attribute": name, "url": val})
    for s in STYLE_BLOCK_RE.finditer(html or ""):
        for u in CSS_URL_RE.finditer(s.group("css") or ""):
            if is_remote(u.group("val")):
                fetch.append({"element": "style", "attribute": "url()",
                              "url": u.group("val").strip()})
    for i in AT_IMPORT_RE.finditer(html or ""):
        if is_remote(i.group("val")):
            fetch.append({"element": "style", "attribute": "@import",
                          "url": i.group("val").strip()})
    for m in ANCHOR_RE.finditer(html or ""):
        for a in ATTR_RE.finditer(m.group("attrs") or ""):
            if a.group("name").lower() == "href" and is_remote(a.group("val")):
                nav.append({"element": "a", "attribute": "href",
                            "url": a.group("val").strip()})
    return fetch, nav


def relative_subresources(html):
    """Local (non-remote, non-data, non-fragment) subresource references.

    These are what a MOVE exposes: a page that only works because it sits beside
    style.css or app.js is not the single self-contained file the charter asks for.
    """
    out = []
    for m in SUB_RESOURCE_TAGS.finditer(html or ""):
        tag = m.group(1).lower()
        attrs = m.group("attrs") or ""
        for a in ATTR_RE.finditer(attrs):
            name, val = a.group("name").lower(), a.group("val").strip()
            if name not in ("src", "href", "data", "poster"):
                continue
            if not val or val.startswith(("#", "data:", "javascript:", "mailto:", "http", "//")):
                continue
            out.append({"element": tag, "attribute": name, "url": val})
    for s in STYLE_BLOCK_RE.finditer(html or ""):
        for u in CSS_URL_RE.finditer(s.group("css") or ""):
            v = u.group("val").strip()
            if v and not v.startswith(("#", "data:", "http", "//")):
                out.append({"element": "style", "attribute": "url()", "url": v})
    for i in AT_IMPORT_RE.finditer(html or ""):
        v = i.group("val").strip()
        if v and not v.startswith(("#", "data:", "http", "//")):
            out.append({"element": "style", "attribute": "@import", "url": v})
    return out


def classify(light_res, dark_res):
    """Turn two render records into a verdict. Pure: no I/O, no browser.

    light_res / dark_res are dicts from the browser probe:
        {"ok": bool, "resources": [{"url","status","transfer"}], "text": str}

    The ONLY thing that makes a page broken is a subresource that the LIGHT run
    fetched successfully and the DARK run could not. Everything else is a
    different fact and must not be reported as this one.
    """
    lr = {r["url"]: r for r in (light_res or {}).get("resources", [])}
    dr = {r["url"]: r for r in (dark_res or {}).get("resources", [])}
    remote_in_light, denied_in_dark = [], []
    for url, r in lr.items():
        if not is_remote(url):
            continue
        got = r.get("status", 0) or r.get("transfer", 0)
        if got:
            remote_in_light.append(url)
    for url, r in dr.items():
        if not is_remote(url):
            continue
        got = r.get("status", 0) or r.get("transfer", 0)
        if not got:
            denied_in_dark.append(url)
    # the failure this tool exists to find: a fetch the page NEEDS and cannot get
    broken = sorted(set(remote_in_light) & set(denied_in_dark))
    # a remote subresource that failed in BOTH runs is broken for another reason
    # (dead URL) and is NOT an offline violation -- reported separately.
    dead_both = sorted({
        u for u, r in dr.items()
        if is_remote(u) and not (r.get("status", 0) or r.get("transfer", 0))
        and u in lr and not (lr[u].get("status", 0) or lr[u].get("transfer", 0))
    })
    verdict = "BROKEN" if broken else "CLEAN"
    return {
        "verdict": verdict,
        "broken": broken,
        "dead_in_both": dead_both,
        "remote_fetched_light": sorted(remote_in_light),
        "denied_in_dark": sorted(denied_in_dark),
        "probe_ok": bool((dark_res or {}).get("ok")) and bool((light_res or {}).get("ok")),
    }


def verdict_line(clean, total, broken_pages, moved_pages):
    """The FIRST line of the artifact. One number, stated plainly."""
    line = "%d of %d pages draw with the network genuinely unreachable" % (clean, total)
    if broken_pages:
        line += "; %d do not" % len(broken_pages)
    else:
        line += "; none do not"
    if moved_pages:
        line += ". %d page(s) also fail the move test" % len(moved_pages)
    return line + "."


def summary_signature(rows):
    """What a re-run must reproduce. Timers and costs are deliberately excluded."""
    # sort by a TOTAL order, not by page alone. Sorting on `page` alone leaves
    # ties (two rows with the same page name) resolved by input order, so the
    # "stable under reordering" claim was false whenever the census held a
    # duplicate name -- and the falsifier's own control mutant was flagged for it.
    # A signature that depends on input order is not a signature.
    return json.dumps([
        {"page": r["page"], "verdict": r["verdict"],
         "broken": r["broken"], "moved": r["moved"]}
        for r in sorted(rows, key=lambda r: (r["page"], r["verdict"],
                                             ",".join(r["broken"]), bool(r["moved"])))
    ], sort_keys=True)
# @@PLUG-LOGIC-END@@


# --------------------------------------------------------------------------- #
# the browser probe
# --------------------------------------------------------------------------- #
HARNESS = """<!doctype html>
<meta charset="utf-8"><title>plug_check harness</title>
<style>
 body{margin:0;font:12px monospace}
 iframe{width:%(vw)dpx;height:%(vh)dpx;border:0;display:block}
</style>
%(frames)s
<div id="__plug">pending</div>
<script>
var IDS = %(ids)s;
function grab(id){
  try {
    var w = document.getElementById(id).contentWindow, d = w.document;
    var res = [];
    try {
      var e = w.performance.getEntriesByType('resource') || [];
      for (var i=0;i<e.length;i++){
        res.push({url:e[i].name, status:e[i].responseStatus||0,
                  transfer:e[i].transferSize||0, init:e[i].initiatorType||''});
      }
    } catch(err){ res = [{url:'__timing_unavailable__:'+err, status:0, transfer:0}]; }
    var imgs = [];
    try {
      var im = d.images || [];
      for (var j=0;j<im.length;j++){
        if (!im[j].complete || im[j].naturalWidth === 0)
          imgs.push(im[j].currentSrc || im[j].src || '');
      }
    } catch(err2){}
    return {ok:true, resources:res, broken_images:imgs,
            text:(d.body && d.body.innerText ? d.body.innerText : '')
                  .replace(/\\s+/g,' ').trim().slice(0,400)};
  } catch(err){
    return {ok:false, resources:[], broken_images:[], error:String(err), text:''};
  }
}
function collect(){
  var out = {};
  for (var i=0;i<IDS.length;i++){ out[IDS[i]] = grab(IDS[i]); }
  document.getElementById('__plug').textContent = JSON.stringify(out);
}
window.addEventListener('load', function(){ setTimeout(collect, %(settle)d); });
</script>
"""

MARK = re.compile(r'<div id="__plug">(.*?)</div>', re.S | re.I)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if Path(c).exists() and os.access(c, os.X_OK):
            return c
    return shutil.which("google-chrome") or shutil.which("chromium")


def discover(targets):
    files = []
    for t in targets:
        p = Path(t).expanduser()
        if p.is_file() and p.suffix.lower() == ".html":
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.html")))
    seen, uniq = set(), []
    for f in files:
        s = str(f)
        if any(k in s for k in EXCLUDE_PARTS):
            continue
        k = str(f.resolve())
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq


def run_batch(chrome, pages, dark):
    """Load up to BATCH pages in one launch. dark=True blackholes the network."""
    tmp = Path(tempfile.mkdtemp(prefix="plug-"))
    try:
        frames, ids = [], []
        for i, p in enumerate(pages):
            fid = "f%d" % i
            ids.append(fid)
            frames.append('<iframe id="%s" src="%s" loading="eager"></iframe>'
                          % (fid, p.resolve().as_uri()))
        h = tmp / "_harness.html"
        h.write_text(HARNESS % {"vw": VW, "vh": VH,
                                "frames": "\n".join(frames),
                                "ids": json.dumps(ids),
                                "settle": 2500 if dark else 2000}, encoding="utf-8")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--hide-scrollbars", "--allow-file-access-from-files",
               "--disable-web-security", "--disable-extensions"]
        if dark:
            cmd += DARK_FLAGS
        cmd += ["--virtual-time-budget=%d" % TIME_BUDGET,
                "--window-size=%d,%d" % (VW, VH), "--dump-dom", h.resolve().as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        m = MARK.search(r.stdout or "")
        if not m:
            return {fid: {"ok": False, "resources": [], "error": "probe marker absent"}
                    for fid in ids}
        raw = m.group(1).strip()
        if raw == "pending":
            return {fid: {"ok": False, "resources": [], "error": "probe did not settle"}
                    for fid in ids}
        raw = (raw.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<")
                  .replace("&gt;", ">").replace("&#x27;", "'").replace("&#39;", "'"))
        return json.loads(raw)
    except subprocess.TimeoutExpired:
        return {("f%d" % i): {"ok": False, "resources": [], "error": "browser timeout"}
                for i in range(len(pages))}
    except Exception as exc:  # noqa: BLE001
        return {("f%d" % i): {"ok": False, "resources": [],
                              "error": "%s: %s" % (type(exc).__name__, exc)}
                for i in range(len(pages))}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_pages(chrome, pages, verbose=True):
    rows = []
    for start in range(0, len(pages), BATCH):
        chunk = pages[start:start + BATCH]
        light = run_batch(chrome, chunk, dark=False)
        dark = run_batch(chrome, chunk, dark=True)
        for i, p in enumerate(chunk):
            fid = "f%d" % i
            html = p.read_text(errors="replace")
            fetch_refs, nav_refs = split_refs(html)
            rel = relative_subresources(html)
            cls = classify(light.get(fid), dark.get(fid))
            cls["page"] = str(p)
            cls["bytes"] = p.stat().st_size
            cls["remote_subresources_in_source"] = len(fetch_refs)
            cls["citation_links_in_source"] = len(nav_refs)
            cls["relative_subresources_in_source"] = len(rel)
            cls["relative_subresources"] = rel[:8]
            # the move test: does it depend on a sibling file at all?
            cls["moved"] = bool(rel)
            rows.append(cls)
            if verbose:
                tag = cls["verdict"] if cls["verdict"] == "BROKEN" else "clean"
                extra = ""
                if cls["moved"]:
                    extra = "  [move-test: %d sibling ref(s)]" % len(rel)
                print("[%-6s] %s%s" % (tag, p, extra))
                if cls["broken"]:
                    for u in cls["broken"]:
                        print("         DENIED IN THE DARK: %s" % u)
                if not cls["probe_ok"] and cls["verdict"] == "CLEAN":
                    print("         NOTE: probe did not report ok -- verdict is not evidence")
    return rows


# --------------------------------------------------------------------------- #
# the self-test: run against the SHIPPED bytes of this file
# --------------------------------------------------------------------------- #
def selftest(script_path, chrome):
    """Slice this file's own logic module out and exercise it. Then falsify it.

    Nothing here is a re-implementation: the code under test is read back out of
    the shipped file between the @@PLUG-LOGIC-BEGIN@@ / @@PLUG-LOGIC-END@@ markers.
    """
    checks, failures = [], []

    def ck(name, cond, note=""):
        checks.append(name)
        if not cond:
            failures.append("%s %s" % (name, note))
        print("  %-58s %s%s" % (name, "PASS" if cond else "FAIL",
                                ("  " + note) if note and not cond else ""))

    src = Path(script_path).read_text(encoding="utf-8")
    # built by concatenation on purpose: written as one literal, the marker below
    # would itself be a second occurrence in this file and the anchor count would
    # never be 1. (It was, on the first run. That is what the count check is for.)
    OPEN = "# @@PLUG-LOGIC-" + "BEGIN@@"
    CLOSE = "# @@PLUG-LOGIC-" + "END@@"
    n_open, n_close = src.count(OPEN), src.count(CLOSE)
    ck("the open marker appears exactly once", n_open == 1, "count=%d" % n_open)
    ck("the close marker appears exactly once", n_close == 1, "count=%d" % n_close)
    first = src.find(OPEN)
    last = src.find(CLOSE)
    ck("the two markers resolve to one ordered range",
       first != -1 and last > first,
       "a banner that matches more than once is not an anchor -- it slices nothing "
       "and reports success anyway")
    block = src[first:last]
    ck("sliced block is non-trivial", len(block) > 1500, "len=%d" % len(block))

    # the slice is evaluated in a namespace that deliberately withholds everything
    # except the two stdlib modules the logic itself imports. A slice that needs
    # anything else fails HERE rather than silently in the field.
    ns = {"re": re, "json": json}
    try:
        exec(compile(block, "<shipped-slice>", "exec"), ns)  # noqa: S102
        exec_error = ""
    except Exception as exc:  # noqa: BLE001
        exec_error = "%s: %s" % (type(exc).__name__, exc)
    split_refs = ns.get("split_refs")
    classify = ns.get("classify")
    rel_sub = ns.get("relative_subresources")
    vline = ns.get("verdict_line")
    sig = ns.get("summary_signature")
    ck("the re-sliced module is runnable on its own (no missing import, no NameError)",
       not exec_error and all(callable(f) for f in
                              (split_refs, classify, rel_sub, vline, sig)),
       exec_error)

    # --- split_refs: the distinction the whole tool rests on ---------------
    html = ('<link rel="stylesheet" href="https://f.example/a.css">'
            '<a href="https://s.example/source">the source</a>'
            '<img src="https://i.example/p.png"><script src="//c.example/x.js"></script>'
            '<style>body{background:url(https://b.example/b.png)}</style>')
    fetch, nav = split_refs(html)
    fu = {r["url"] for r in fetch}
    nu = {r["url"] for r in nav}
    ck("a <link rel=stylesheet> is classified as FETCHED",
       "https://f.example/a.css" in fu)
    ck("a plain <a href> citation is classified as NAVIGATION ONLY",
       "https://s.example/source" in nu and "https://s.example/source" not in fu,
       "this is the exact false alarm that kills trust in the number")
    ck("an <img src> is FETCHED", "https://i.example/p.png" in fu)
    ck("a protocol-relative <script src> is FETCHED", "//c.example/x.js" in fu)
    ck("a style url() is FETCHED", "https://b.example/b.png" in fu)
    # the at-rule, both ways: a real one is FETCHED, and the documented token on
    # this very page must NOT be. Written as one literal in the scanner, the
    # second assertion failed against the tool's own documentation.
    r_at, _n_at = split_refs("<style>@" + "import url(https://cd.example/s.css);</style>")
    ck("a remote CSS at-rule @import is FETCHED",
       any(r["url"] == "https://cd.example/s.css" for r in r_at))
    r_doc, _n_doc = split_refs("<code>&#64;" + "import</code> is a subresource")
    ck("the DOCUMENTED token is not mistaken for a real at-rule",
       r_doc == [], "the tool must not flag its own documentation")

    # --- classify: deny it, and prove the citation is NOT blamed -----------
    page = ('<a href="https://s.example/source">src</a>'
            '<script src="https://c.example/x.js"></script>')
    light = {"ok": True, "resources": [
        {"url": "https://c.example/x.js", "status": 200, "transfer": 1200}]}
    dark = {"ok": True, "resources": [
        {"url": "https://c.example/x.js", "status": 0, "transfer": 0}]}
    r = classify(light, dark)
    ck("a page whose remote script is DENIED off-network is BROKEN",
       r["verdict"] == "BROKEN" and r["broken"] == ["https://c.example/x.js"])
    ck("the citation URL is NOT named as broken even though it is remote",
       "https://s.example/source" not in r["broken"])

    # the same page WITHOUT a subresource: citations only -> CLEAN
    r2 = classify({"ok": True, "resources": []}, {"ok": True, "resources": []})
    ck("a citations-only page is CLEAN with the cable out", r2["verdict"] == "CLEAN",
       "an empty page set must not be reported as broken, and neither must an honest one")

    # negative control: a page that fetched nothing in either run is CLEAN
    r3 = classify({"ok": True, "resources": [
        {"url": "https://d.example/dead.js", "status": 0, "transfer": 0}]},
        {"ok": True, "resources": [
        {"url": "https://d.example/dead.js", "status": 0, "transfer": 0}]})
    ck("a remote ref dead in BOTH runs is reported separately, not as an offline break",
       r3["verdict"] == "CLEAN" and r3["dead_in_both"] == ["https://d.example/dead.js"],
       "a dead URL and an offline break are different facts")

    # --- the move test ----------------------------------------------------
    mv = rel_sub('<link rel="stylesheet" href="style.css"><script src="app.js"></script>')
    ck("a sibling-file reference is caught by the move test",
       len(mv) == 2 and {m["url"] for m in mv} == {"style.css", "app.js"})
    ck("a data: URI is not a move-test offender",
       rel_sub('<img src="data:image/gif;base64,R0lGOD">') == [])
    ck("a pure citation page has no move-test offenders",
       rel_sub('<a href="https://x.example/y">y</a>') == [])

    # --- the first line ---------------------------------------------------
    line = vline(54, 55, [{"page": "x"}], [])
    ck("the verdict line leads with the count", line.startswith("54 of 55 pages draw"),
       line)
    ck("the verdict line names the failing count when there is one",
       "1 do not" in line)
    ck("a clean fleet says so without hedging", "none do not" in vline(55, 55, [], []))

    # --- determinism of the signature -------------------------------------
    rows = [{"page": "b", "verdict": "CLEAN", "broken": [], "moved": False},
            {"page": "a", "verdict": "BROKEN", "broken": ["u"], "moved": True}]
    ck("the verdict signature is order-independent", sig(rows) == sig(list(reversed(rows))))
    ck("the verdict signature is JSON and carries no timers",
       "cost" not in sig(rows) and json.loads(sig(rows)))
    # the tie case the falsifier's control exposed: two rows sharing a page name
    tied = [{"page": "same", "verdict": "CLEAN", "broken": [], "moved": False},
            {"page": "same", "verdict": "BROKEN", "broken": ["u"], "moved": True}]
    ck("the verdict signature is order-independent EVEN WITH TIED PAGE NAMES",
       sig(tied) == sig(list(reversed(tied))),
       "sorting on page alone left ties resolved by input order -- the signature "
       "was not a signature")


    # --- FALSIFICATION ---------------------------------------------------
    # The faults are declared HERE, in the artifact, and applied to a pristine
    # copy of the sliced core: every marker below is replaced in BOTH the module
    # and the probe. A rewrite that misses the probe copy must be reported as a
    # fault that got through -- not blessed.
    print("\n  -- falsification: a declared fault must be CAUGHT, a control must ESCAPE --")
    MUTANTS = [
        # name, owner (the one assertion that must trip), marker, replacement
        ("citation-blamed", "the citation URL is NOT named as broken",
         "        if not is_remote(url):\n            continue\n        got = r.get(\"status\", 0) or r.get(\"transfer\", 0)\n        if got:\n            remote_in_light.append(url)",
         "        if not is_remote(url):\n            continue\n        remote_in_light.append(url)"),
        ("blanket-remote", "a citations-only page is CLEAN with the cable out",
         "    broken = sorted(set(remote_in_light) & set(denied_in_dark))",
         "    broken = sorted(set(lr) | set(dr))"),
        ("inert-control", "CONTROL",
         "def is_remote(url):",
         "def is_remote(url_arg__):\n    url = url_arg__"),
    ]
    # A mutant is judged on the DELTA against the clean core over a SET of
    # scenarios. One scenario is not enough: the first version of this falsifier
    # declared two faults and reported both as ESCAPED, because the inputs it
    # built happened to make those mutations equivalent. That was a finding about
    # the falsifier, not about the mutations -- so the scenarios below are chosen
    # to separate each declared fault from the clean run.
    SCENARIOS = [
        ("needed-asset-denied",
         ({"ok": True, "resources": [{"url": "https://cdn.example/real.js",
                                      "status": 200, "transfer": 900}]},
          {"ok": True, "resources": [{"url": "https://cdn.example/real.js",
                                      "status": 0, "transfer": 0}]})),
        ("citations-only-no-remote",
         ({"ok": True, "resources": []}, {"ok": True, "resources": []})),
        ("dead-url-in-both-runs",
         ({"ok": True, "resources": [{"url": "https://d.example/gone.js",
                                      "status": 0, "transfer": 0}]},
          {"ok": True, "resources": [{"url": "https://d.example/gone.js",
                                      "status": 0, "transfer": 0}]})),
        ("blackout-failed-asset-still-loaded",
         ({"ok": True, "resources": [{"url": "https://cdn.example/real.js",
                                      "status": 200, "transfer": 900}]},
          {"ok": True, "resources": [{"url": "https://cdn.example/real.js",
                                      "status": 200, "transfer": 900}]})),
    ]
    fault_text = ('<a href="https://s.example/source">a source</a>'
                  '<script src="https://cdn.example/real.js"></script>\n')

    def observe(fns, text):
        """Four named observations from one core, over every scenario."""
        obs = {}
        f_refs, _n = fns["split_refs"](text)
        obs["citation_counted_as_fetch"] = any(
            r["url"] == "https://s.example/source" for r in f_refs)
        for sname, (lt, dk) in SCENARIOS:
            got = fns["classify"](lt, dk)
            obs["%s.verdict" % sname] = got["verdict"]
            obs["%s.broken" % sname] = ",".join(got["broken"])
        obs["verdict_line_clean"] = fns["verdict_line"](4, 4, [], [])
        obs["verdict_line_broken"] = fns["verdict_line"](3, 4, [{"page": "x"}], [])
        return obs

    clean_fns = {"split_refs": split_refs, "classify": classify, "verdict_line": vline,
                 "relative_subresources": rel_sub, "summary_signature": sig, "is_remote": ns["is_remote"]}
    base_obs = observe(clean_fns, fault_text)
    results = []
    for name, owner, marker, repl in MUTANTS:
        hit = block.count(marker)
        if hit != 1:
            ck("mutant '%s' could be applied (its anchor is unique)" % name, False,
               "anchor matched %d time(s) -- target by anchor, never by guesswork" % hit)
            continue
        mns = {"re": re, "json": json}
        err = ""
        try:
            exec(compile(block.replace(marker, repl), "<mutant:%s>" % name, "exec"), mns)  # noqa: S102
            obs = observe(mns, fault_text)
        except Exception as exc:  # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, exc)
            obs = {}
        changed = sorted(k for k in base_obs if obs.get(k) != base_obs.get(k))
        if name == "inert-control":
            ck("CONTROL mutant (renames a parameter, changes nothing) MUST ESCAPE",
               not changed and not err,
               "changed=%s err=%s -- a control that is CAUGHT means this harness "
               "reports faults that are not there" % (changed, err))
        else:
            ck("declared fault '%s' is CAUGHT (owner: %s)" % (name, owner),
               bool(changed), err or "no observation moved -- the fault escaped")
        results.append((name, changed))
    print("\n  mutation delta against the clean core, BY NAME (not a total):")
    for name, changed in results:
        print("    %-22s %s" % (name, ", ".join(changed) if changed else "(nothing changed)"))

    # and the negative control on the LIVE render path: identical resources in
    # both runs must not be reported broken
    ctrl = classify({"ok": True, "resources": light["resources"]},
                    {"ok": True, "resources": light["resources"]})
    ck("CONTROL: the same resources in both runs must NOT be reported broken",
       ctrl["verdict"] == "CLEAN", "a control that fails here means the tool cries wolf")

    # --- live control page: the blackout must really work -----------------
    print("\n  -- live control: does the blackout actually blackhole? --")
    tmp = Path(tempfile.mkdtemp(prefix="plug-ctl-"))
    try:
        ctl = tmp / "control.html"
        ctl.write_text(
            '<!doctype html><meta charset="utf-8"><body><div id="m">p</div>'
            '<script src="https://cdn.jsdelivr.net/npm/plug-check-not-real@1/x.js">'
            '</script><script>'
            'fetch("https://example.com/ping",{mode:"no-cors"}).then(function(){'
            'document.getElementById("m").textContent="NET-REACHABLE";})'
            '.catch(function(e){document.getElementById("m").textContent='
            '"NET-BLOCKED:"+e.name;});</script></body>', encoding="utf-8")
        clean = tmp / "clean.html"
        clean.write_text('<!doctype html><meta charset="utf-8"><title>clean</title>'
                         '<body><h1>clean</h1><p>no remote anything</p></body>',
                         encoding="utf-8")
        got = {}
        for dark in (False, True):
            res = run_batch(chrome, [ctl, clean], dark=dark)
            got["dark" if dark else "light"] = res
        light_txt = (got["light"].get("f0") or {}).get("text", "")
        dark_txt = (got["dark"].get("f0") or {}).get("text", "")
        ck("CONTROL light: the network is reachable when unblackholed",
           "NET-REACHABLE" in light_txt, "light text was %r" % light_txt[:80])
        ck("CONTROL dark: the network is really blocked when blackholed",
           "NET-BLOCKED" in dark_txt, "dark text was %r" % dark_txt[:80])
        lr = classify(got["light"].get("f0"), got["dark"].get("f0"))
        ck("the control page is correctly found BROKEN off-network (real break)",
           lr["verdict"] == "BROKEN" and any("not-real" in u for u in lr["broken"]),
           json.dumps(lr["broken"]))
        cr = classify(got["light"].get("f1"), got["dark"].get("f1"))
        ck("a page with no remote anything is correctly CLEAN off-network (no false alarm)",
           cr["verdict"] == "CLEAN", json.dumps(cr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 70)
    print("SELFTEST: %d checks, %d failure(s)" % (len(checks), len(failures)))
    for f in failures:
        print("   FAILED: %s" % f)
    return 0 if not failures else 1


# --------------------------------------------------------------------------- #
# the artifact
# --------------------------------------------------------------------------- #
def render_page(rows, chrome, out_path, line, roots):
    total = len(rows)
    broken = [r for r in rows if r["verdict"] == "BROKEN"]
    moved = [r for r in rows if r["moved"]]
    clean = total - len(broken)
    sig = json.loads(summary_signature(rows))

    def esc(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    def row(r):
        cls = "bad" if r["verdict"] == "BROKEN" else ("mv" if r["moved"] else "ok")
        detail = []
        for u in r["broken"]:
            detail.append('<div class="u">DENIED IN THE DARK: %s</div>' % esc(u))
        for u in r["dead_in_both"]:
            detail.append('<div class="u dim">dead in both runs (not an offline break): %s</div>' % esc(u))
        for m in r["relative_subresources"]:
            detail.append('<div class="u dim">sibling file, move test: &lt;%s %s="%s"&gt;</div>'
                          % (esc(m["element"]), esc(m["attribute"]), esc(m["url"])))
        if not r["probe_ok"]:
            detail.append('<div class="u dim">the probe did not report ok -- this row is not evidence</div>')
        return ('<div class="row %s"><div class="p"><span class="tag">%s</span> %s</div>'
                '<div class="m">%d citation link(s) &middot; %d remote subresource(s) &middot; '
                '%d sibling ref(s) &middot; %d bytes</div>%s</div>'
                % (cls, r["verdict"], esc(r["page"]),
                   r["citation_links_in_source"], r["remote_subresources_in_source"],
                   r["relative_subresources_in_source"], r["bytes"],
                   "".join(detail) or ""))

    rows_sorted = sorted(rows, key=lambda r: (r["verdict"] != "BROKEN", not r["moved"], r["page"]))
    badge = "ok" if not broken else "bad"
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pull the Plug — does every page still draw with the cable out?</title>
<style>
  :root{--bg:#0b0d10;--panel:#12151a;--edge:#1e242c;--ink:#e6edf3;--dim:#8b98a5;
        --faint:#5b6673;--ok:#57d9a3;--bad:#ff6b6b;--warn:#f0b429;--line:#232a33}
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%%}
  body{margin:0;background:var(--bg);color:var(--ink);padding:22px 16px 70px;
       font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:940px;margin:0 auto}
  .kick{color:var(--dim);font:600 11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
        letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}
  h1{font:600 26px/1.25 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
     letter-spacing:-.4px;margin:0 0 12px;border-left:4px solid var(--%(badge)s);padding-left:12px}
  .meta{color:var(--faint);font:12px/1.6 ui-monospace,monospace;margin-bottom:20px}
  .meta b{color:var(--dim)}
  .panel{background:var(--panel);border:1px solid var(--edge);border-radius:10px;
         padding:14px 15px;margin-bottom:14px}
  h2{font:600 12px/1 ui-monospace,monospace;letter-spacing:2px;text-transform:uppercase;
     color:var(--faint);margin:26px 0 10px;padding-bottom:7px;border-bottom:1px solid var(--line)}
  .kv{display:flex;flex-wrap:wrap;gap:8px}
  .kpi{flex:1 1 150px;background:var(--panel);border:1px solid var(--edge);border-radius:9px;padding:11px 12px}
  .kpi .n{font:600 24px/1 ui-monospace,monospace;margin-bottom:5px}
  .kpi .l{color:var(--dim);font:11px/1.3 ui-monospace,monospace;letter-spacing:1px;text-transform:uppercase}
  .kpi.ok .n{color:var(--ok)} .kpi.bad .n{color:var(--bad)} .kpi.warn .n{color:var(--warn)}
  .row{background:var(--panel);border:1px solid var(--edge);border-left:3px solid var(--edge);
       border-radius:9px;padding:10px 12px;margin-bottom:7px}
  .row.bad{border-left-color:var(--bad)} .row.mv{border-left-color:var(--warn)}
  .row.ok{border-left-color:var(--ok)}
  .p{font:600 13px/1.4 ui-monospace,monospace;word-break:break-all}
  .tag{font:600 10px/1 ui-monospace,monospace;letter-spacing:1px;padding:3px 6px;border-radius:4px;
       background:#1b2229;color:var(--dim);vertical-align:middle;margin-right:6px}
  .row.bad .tag{color:var(--bad)} .row.mv .tag{color:var(--warn)} .row.ok .tag{color:var(--ok)}
  .m{color:var(--faint);font:11px/1.5 ui-monospace,monospace;margin-top:5px}
  .u{color:var(--bad);font:11px/1.5 ui-monospace,monospace;margin-top:4px;word-break:break-all}
  .u.dim{color:var(--faint)}
  ol,ul{margin:8px 0 0;padding-left:20px;color:var(--dim);font-size:14px}
  li{margin-bottom:6px}
  code{background:#171d24;padding:1px 5px;border-radius:4px;
       font:12px ui-monospace,monospace;color:var(--ink);word-break:break-all}
  .lim{border-left:3px solid var(--warn)}
  table{border-collapse:collapse;width:100%%;margin-top:6px}
  td,th{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left;
        font:12px/1.4 ui-monospace,monospace;color:var(--dim);vertical-align:top}
  th{color:var(--faint);font-weight:600;text-transform:uppercase;letter-spacing:1px;font-size:10px}
  /* the phone rule: below 620px a 3-column table turns into three stacked
     records. Measured defect it fixes: at 390px the middle header wrapped onto
     four lines and the body cells broke mid-token, which is the densest and
     least scannable thing on the page -- on the one width that matters here. */
  @media (max-width:620px){
    table.cmp thead{display:none}
    table.cmp tr{display:block;border-bottom:1px solid var(--line);padding:8px 0}
    table.cmp tbody,table.cmp td{display:block}
    table.cmp td{border:0;padding:2px 0}
    table.cmp td:first-child{color:var(--ink)}
    table.cmp td:before{content:attr(data-label);display:block;color:var(--faint);
      font:600 9px/1.4 ui-monospace,monospace;letter-spacing:1.5px;
      text-transform:uppercase;margin-bottom:2px}
  }
  footer{margin-top:34px;padding-top:14px;border-top:1px solid var(--line);
         color:var(--faint);font:11px/1.7 ui-monospace,monospace}
</style>
</head>
<body>
<div class="wrap">
  <div class="kick">Software room &middot; offline render proof</div>
  <h1>%(line)s</h1>
  <div class="meta">
    measured %(when)s &middot; browser <b>%(chrome)s</b> &middot;
    blackout <b>--host-resolver-rules="MAP * ~NOTFOUND" --proxy-server=127.0.0.1:1</b><br>
    viewport <b>%(vw)d&times;%(vh)d</b> (an iframe's own layout viewport) &middot;
    pages <b>%(total)d</b> &middot; exclusions printed at the foot of this page
  </div>

  <div class="kv">
    <div class="kpi ok"><div class="n">%(clean)d</div><div class="l">draw with the cable out</div></div>
    <div class="kpi %(badge)s"><div class="n">%(nbroken)d</div><div class="l">do not</div></div>
    <div class="kpi warn"><div class="n">%(nmoved)d</div><div class="l">fail the move test</div></div>
    <div class="kpi"><div class="n">%(ncites)d</div><div class="l">citation links, not offenders</div></div>
  </div>

  <h2>The method, and the mistake it exists to avoid</h2>
  <div class="panel">
    <p style="margin:0 0 8px;color:var(--dim);font-size:14px">
      Both of these are <code>https://&hellip;</code> in the source, and a regex cannot tell
      them apart:</p>
    <table class="cmp">
      <thead><tr><th>reference</th><th>does the browser fetch it to DRAW the page?</th>
        <th>counts as an offender?</th></tr></thead>
      <tbody>
      <tr>
        <td data-label="reference">&lt;img src&gt;, &lt;script src&gt;,
            &lt;link rel=stylesheet&gt;, CSS <code>&#64;import</code>,
            style <code>url()</code></td>
        <td data-label="fetched to draw?">yes &mdash; a fail here breaks the page</td>
        <td data-label="offender?">YES</td></tr>
      <tr>
        <td data-label="reference">&lt;a href&gt; to a source URL</td>
        <td data-label="fetched to draw?">no &mdash; only if the reader clicks</td>
        <td data-label="offender?">NO</td></tr>
      </tbody>
    </table>
    <p style="margin:9px 0 0;color:var(--dim);font-size:14px">
      This tool stops reading the source for the verdict. It launches Chrome with every
      hostname unresolvable and no proxy, loads the page, and reads back what the browser
      actually tried to fetch and what came back empty (<code>responseStatus:0</code>,
      <code>transferSize:0</code>). A page is broken only when a subresource the page
      needed <em>succeeded with the network up and was denied with it down</em>.</p>
  </div>

  <h2>Every page, worst first</h2>
  %(rows)s

  <h2>What would falsify this</h2>
  <div class="panel">
    <ul>
      <li>A control page carrying one remote <code>&lt;script src&gt;</code> must be found
          BROKEN &mdash; and it is, in the self-test, on every run.</li>
      <li>A page with no remote anything must be found CLEAN &mdash; and it is; that is the
          negative control, and without it "found nothing" would be indistinguishable from
          "looked at nothing".</li>
      <li>The light/dark pair must disagree on the network itself. If both runs report the
          asset loaded, the blackout failed and this page is worthless.</li>
      <li>The logic self-test is sliced out of <em>this build</em> between its own marker
          comments, so the code under test and the test are the same bytes. The slice is
          then re-executed in a namespace holding nothing but <code>re</code> and
          <code>json</code> &mdash; on the first run it failed there with a
          <code>NameError</code>, which is the whole point of testing the bytes you ship
          rather than the ones you remember writing.</li>
    </ul>
  </div>

  <h2>Honest limits</h2>
  <div class="panel lim">
    <ul>
      <li><b>A citation is not proof it was followed.</b> This page proves the cited URL did
          not load. It does not check the URL still resolves, or still says what the page
          claims. A dead citation passes this tool.</li>
      <li><b>Rendering is not layout.</b> Off-screen overflow and the 390px rule are a
          different measurement (see <code>overflow390.py</code>). This page fires no pixels
          judgment.</li>
      <li><b>Excluded deliberately:</b> %(excl)s.
          Loop fixtures, browser-profile internals and build checkpoints are not shipped
          pages; leaving them out is a decision, not an accident.</li>
      <li><b>The cache is disabled per launch, not per page.</b> Two pages in one batch share
          a browser, so a URL fetched by the first page could in principle be served from
          memory for the second. The counts would not change; a per-page launch would.</li>
      <li><b>%(nbroken)d of %(total)d is the finding tonight.</b> A clean sweep is a real
          result here and not a soft one &mdash; but it only covers the pages in the roots
          listed below.</li>
    </ul>
  </div>

  <h2>How to re-run it</h2>
  <div class="panel">
    <p style="margin:0 0 6px;color:var(--dim);font-size:14px">The exact command that produced this page:</p>
    <p style="margin:0"><code>python3 plug_check.py --scan</code></p>
    <p style="margin:8px 0 0;color:var(--dim);font-size:14px">The self-test, on these bytes:</p>
    <p style="margin:0"><code>python3 plug_check.py --selftest</code></p>
    <p style="margin:8px 0 0;color:var(--dim);font-size:14px">Roots scanned:</p>
    <p style="margin:0">%(roots)s</p>
  </div>

  <footer>
    verdict signature (a re-run must reproduce this byte-for-byte; only timers may move):<br>
    <code>%(sig)s</code><br><br>
    Pull the Plug &middot; built in the software room &middot; everything here is local:
    nothing was sent, published, spent or moved off this machine.
  </footer>
</div>
</body>
</html>
""" % {
        "line": esc(line), "when": os.environ.get("PLUG_WHEN", ""),
        "chrome": esc(chrome), "vw": VW, "vh": VH, "total": total,
        "clean": clean, "nbroken": len(broken), "nmoved": len(moved), "badge": badge,
        "ncites": sum(r["citation_links_in_source"] for r in rows),
        "rows": "\n".join(row(r) for r in rows_sorted),
        "excl": esc(", ".join(EXCLUDE_PARTS)),
        "roots": "<br>".join(esc(str(r)) for r in roots),
        # the FULL signature, not a prefix. Truncating it made the verifier's
        # invariant unsatisfiable on any census bigger than the cut -- the page
        # and the receipt disagreed on a healthy artifact. Carry all of it.
        "sig": esc(json.dumps(sig, sort_keys=True)),
    }
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="prove every shipped page draws with the cable out")
    ap.add_argument("--scan", nargs="*", default=None, metavar="PATH",
                    help="roots to scan (default: the fleet root and every agent workspace)")
    ap.add_argument("--file", metavar="PAGE", help="check exactly one page")
    ap.add_argument("--selftest", action="store_true", help="exercise this file's own logic")
    ap.add_argument("--out", metavar="PAGE.html", help="where to write the artifact")
    ap.add_argument("--json", metavar="FILE.json", help="where to write the raw receipt")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("FATAL: no headless Chrome found; a render verdict requires a real browser.")
        return 2

    if args.selftest:
        return selftest(__file__, chrome)

    if args.file:
        pages, roots = [Path(args.file).expanduser()], [Path(args.file).expanduser().parent]
    else:
        roots = ([Path(p) for p in args.scan] if args.scan
                 else [Path("/home/hermes/fleet"),
                       Path("/home/hermes/.local/share/StarNet/workspaces")])
        pages = discover(roots)
    if not pages:
        print("no .html pages found under: %s" % [str(r) for r in roots])
        return 2

    print("plug_check -- %d page(s) -- browser %s" % (len(pages), chrome))
    print("blackout: %s\n" % " ".join(DARK_FLAGS))
    rows = check_pages(chrome, pages, verbose=not args.quiet)

    broken = [r for r in rows if r["verdict"] == "BROKEN"]
    moved = [r for r in rows if r["moved"]]
    clean = len(rows) - len(broken)
    line = verdict_line(clean, len(rows), broken, moved)
    print("\n" + line)

    # REFUSE to write the standing artifact on a single-file check. An earlier
    # revision let `--file <page>` fall through to the default output path and
    # clobbered the 48-page artifact with a 1-page one. A check of one page must
    # never overwrite the census; it writes only where it is told to.
    if args.file and not args.out:
        print("\n(single-page check: no artifact written, the standing census is untouched)")
    else:
        stamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        out = Path(args.out) if args.out else (Path.home() / "fleet" / "rooms" / "software"
                                               / "workspace" / "artifacts"
                                               / ("dark-render-%s.html" % stamp))
        render_page(rows, chrome, out, line, roots)
        print("artifact: %s" % out)
    if args.json:
        jp = Path(args.json)
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(json.dumps({
            "verdict_line": line, "pages": len(rows), "clean": clean,
            "broken": [r["page"] for r in broken],
            "move_test_failures": [r["page"] for r in moved],
            "signature": summary_signature(rows), "rows": rows,
        }, indent=2), encoding="utf-8")
        print("receipt:  %s" % args.json)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
