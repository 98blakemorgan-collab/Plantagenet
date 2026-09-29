#!/usr/bin/env python3
"""Triple check of the whole R13.1 show build.

Pass 1  Files       every control file present, parses, matches its SHA-256 in BUILD_METADATA.json and the
                    assembler, Mantra size footers, the QLab archive intact and round-trips byte for byte.
Pass 2  The show    QLab and Mantra checked against each other: every OSC message (what QLab sends, not just
                    the cue name), every memory and cue it targets, releases, flash returns, fades, levels,
                    media, the patch, the fixed-FOH jobs, the review edits, no strobe; the venue base.
Pass 3  Paperwork   the book, printouts, base docs and cue list rebuilt in a scratch copy of the repo and
                    compared with the committed files; fixture names, jobs and moves agree; no stale text; every
                    file described in the File Guide.

Usage: python3 tools/verify_show.py [--quick]     (--quick skips the rebuild in pass 3)
Writes production/TLM_nov_2026_final/TLM_nov_2026_final_Build_Check.txt and .json. Exit code 1 if anything fails.
"""
import csv
import hashlib
import io
import json
import math
import os
import plistlib
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PKG = os.path.join(ROOT, "package")
SHOW = os.path.join(PKG, "TLM_nov_2026_final")
BASE_DIR = os.path.join(ROOT, "base", "Plantagenet_Players_Base_2026_r1")
F = {"qlab": os.path.join(SHOW, "TLM_nov_2026_final.qlab5"),
     "mantra": os.path.join(SHOW, "TLM_nov_2026_final.mtr"),
     "mantra_base": os.path.join(BASE_DIR, "Plantagenet_Players_Base_2026_r1.mtr"),
     "qlab_base": os.path.join(BASE_DIR, "Plantagenet_Players_Base_2026_r1.qlab5")}
ASSEMBLER = os.path.join(PKG, "ASSEMBLE_TLM_nov_2026_final.command")
REPORT = os.path.join(ROOT, "production", "TLM_nov_2026_final", "TLM_nov_2026_final_Build_Check")
U = plistlib.UID

RESULTS = []          # (pass, id, status, title, detail)


def check(pas, cid, title):
    def deco(fn):
        def run():
            try:
                status, detail = fn()
            except Exception as e:           # a check that crashes is a failure, with the reason
                status, detail = "FAIL", "check crashed: %s: %s" % (type(e).__name__, e)
            RESULTS.append((pas, cid, status, title, detail))
            return status
        run.cid = cid
        CHECKS.append(run)
        return run
    return deco


CHECKS = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ok(detail=""):
    return "OK", detail


def fail(problems, limit=12):
    extra = "" if len(problems) <= limit else " … and %d more" % (len(problems) - limit)
    return "FAIL", "; ".join(problems[:limit]) + extra


def verdict(problems, good):
    return fail(problems) if problems else ok(good)


# --------------------------------------------------------------------------
# Readers
# --------------------------------------------------------------------------

def mtr_sections(path):
    t = open(path, encoding="latin-1").read()
    parts = re.split(r"^\[([^\]]+)\]\n", t, flags=re.M)
    return dict(zip(parts[1::2], parts[2::2])), t


def kv(body):
    return dict(l.split("=", 1) for l in body.splitlines() if "=" in l)


def unarchive(data):
    objs = data["$objects"]

    def res(x, stack=()):
        if isinstance(x, U):
            if x.data in stack:
                return None
            stack = stack + (x.data,)
            x = objs[x.data]
        if isinstance(x, dict):
            if "NS.keys" in x:
                return {str(res(k, stack)): res(v, stack) for k, v in zip(x["NS.keys"], x["NS.objects"])}
            if "NS.objects" in x:
                return [res(v, stack) for v in x["NS.objects"]]
            if "NS.string" in x:
                return x["NS.string"]
            if "NS.data" in x:
                return x["NS.data"]
            return {k: res(v, stack) for k, v in x.items() if k != "$class"}
        if isinstance(x, list):
            return [res(v, stack) for v in x]
        if x == "$null":
            return None
        return x
    return res(data["$top"]["root"])


def load_ws(path):
    raw = plistlib.load(open(path, "rb"))
    ws = unarchive(raw)
    lists = unarchive(plistlib.loads(ws["cueLists"]))
    return raw, ws, lists


def walk(cues, parent=None, out=None):
    """Flatten a cue tree in firing order: [(cue, parent group)]."""
    out = [] if out is None else out
    for c in cues or []:
        out.append((c, parent))
        walk(c.get("cues"), c, out)
    return out


SEC = {k: mtr_sections(v) for k, v in F.items() if k.startswith("mantra")}
RAW_Q, WS, LISTS = load_ws(F["qlab"])
MAIN = LISTS["cues"][0]
FLAT = walk(MAIN["cues"])
OSC = re.compile(r"^/PlayMemory/Page=(\d+)/Memory=(\d+)/Cue=(\d+)/Level=(\d+)/Fade=(\d+)$")
PAGE_ID = {1: {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 9: 8, 10: 9}, 2: {1: 10, 2: 11, 3: 12, 4: 13, 5: 14, 6: 15, 9: 18, 10: 19},
           3: {k: 19 + k for k in range(1, 7)}, 4: {k: 29 + k for k in range(1, 11)}, 5: {k: 39 + k for k in range(1, 7)},
           6: {k: 49 + k for k in range(1, 11)}, 7: {k: 59 + k for k in range(1, 8)}, 8: {1: 70}}


def file_of(c):
    ft = c.get("fileTarget")
    return ft.get("relativePath") if isinstance(ft, dict) else None


def is_osc(c):
    return "oscString" in c and c.get("oscString") is not None


def groups():
    return [c for c in MAIN["cues"]]


# --------------------------------------------------------------------------
# Pass 1 — files
# --------------------------------------------------------------------------

EXPECTED = ["ASSEMBLE_TLM_nov_2026_final.command", "READ_ME_FIRST.txt", "TLM_nov_2026_final_REVIEW_NOTES.txt", "SOURCE_ZIPS.csv",
            "TLM_nov_2026_final/00_START_HERE.txt", "TLM_nov_2026_final/BUILD_METADATA.json",
            "TLM_nov_2026_final/TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv",
            "TLM_nov_2026_final/TLM_nov_2026_final_SFX_RETARGET_MAP.csv", "TLM_nov_2026_final/TLM_nov_2026_final_MANTRA_SECTION_MAP.csv",
            "TLM_nov_2026_final/TLM_nov_2026_final_MANTRA_SECTION_MAP.txt", "TLM_nov_2026_final/TLM_nov_2026_final_MEDIA_MANIFEST.csv",
            "TLM_nov_2026_final/TLM_nov_2026_final.qlab5", "TLM_nov_2026_final/TLM_nov_2026_final.mtr"]


@check(1, "1.1", "Every package file is present, with no stray files")
def c_files():
    probs = ["missing %s" % f for f in EXPECTED if not os.path.exists(os.path.join(PKG, f))]
    for dp, dn, fs in os.walk(PKG):
        for f in fs + dn:
            if f in (".DS_Store", "__pycache__") or f.startswith("._"):
                probs.append("stray %s" % os.path.relpath(os.path.join(dp, f), PKG))
    n = sum(len(fs) for _, _, fs in os.walk(PKG))
    return verdict(probs, "%d files in package/, all %d control files present" % (n, len(EXPECTED)))


@check(1, "1.2", "Control-file SHA-256 = BUILD_METADATA.json + assembler (show) = BASE_METADATA.json (base)")
def c_hashes():
    meta = json.load(open(os.path.join(SHOW, "BUILD_METADATA.json")))["sha256"]
    bmeta_p = os.path.join(BASE_DIR, "BASE_METADATA.json")
    bmeta = json.load(open(bmeta_p))["sha256"] if os.path.exists(bmeta_p) else {}
    asm = open(ASSEMBLER).read()
    avar = {"qlab": "QLAB_SHA", "mantra": "MTR_SHA"}
    probs = []
    for k, p in F.items():
        h = sha(p)
        where = meta if k in avar else bmeta
        if where.get(k) != h:
            probs.append("%s: %s %s… ≠ file %s…" % (k, "BUILD_METADATA" if k in avar else "BASE_METADATA",
                                                    str(where.get(k))[:10], h[:10]))
        if k in avar:
            m = re.search(r'^%s="([0-9a-f]{64})"' % avar[k], asm, flags=re.M)
            if not m or m.group(1) != h:
                probs.append("%s: assembler %s… ≠ file %s…" % (k, m.group(1)[:10] if m else "none", h[:10]))
    for k in ("mantra_base", "qlab_base"):
        if k in meta:
            probs.append("BUILD_METADATA.json still lists the base (%s): the base is a separate package" % k)
    if re.search(r"^(BASE_SHA|QBASE_SHA)=", asm, flags=re.M):
        probs.append("the show assembler still checks base files")
    return verdict(probs, "4 files, 3 places each: " + ", ".join("%s %s…" % (k, sha(p)[:12]) for k, p in F.items()))


@check(1, "1.3", "Mantra [ZZ_FileEnd] Size footers match the file sizes")
def c_footers():
    probs = []
    for k in ("mantra", "mantra_base"):
        size = int(kv(SEC[k][0]["ZZ_FileEnd"])["Size"])
        if size != os.path.getsize(F[k]):
            probs.append("%s: footer %d, file %d" % (k, size, os.path.getsize(F[k])))
    return verdict(probs, "show %d bytes, base %d bytes" % (os.path.getsize(F["mantra"]), os.path.getsize(F["mantra_base"])))


@check(1, "1.4", "Mantra files are well formed (sections, cue keys in order, memory headers)")
def c_mtr_form():
    probs = []
    for k in ("mantra", "mantra_base"):
        secs, text = SEC[k]
        if not text.startswith("[CustomFixtures]"):
            probs.append("%s: does not start with [CustomFixtures]" % k)
        for name, body in secs.items():
            lines = [l for l in body.split("\n") if l]
            if re.fullmatch(r"Memory\d+(-Cue\d+)?", name) and lines != sorted(lines):
                probs.append("%s [%s] keys out of order" % (k, name))
            bad = [l for l in lines if "=" not in l]
            if bad:
                probs.append("%s [%s] line without '=': %r" % (k, name, bad[0][:40]))
        for name in secs:
            m = re.fullmatch(r"Memory(\d+)", name)
            if m:
                n = int(kv(secs[name]).get("NumScenes", "1"))
                have = [s for s in secs if re.fullmatch(r"Memory%s-Cue\d+" % m.group(1), s)]
                if len(have) != n:
                    probs.append("%s Memory%s: NumScenes %d, %d cue sections" % (k, m.group(1), n, len(have)))
    return verdict(probs, "%d + %d sections" % (len(SEC["mantra"][0]), len(SEC["mantra_base"][0])))


@check(1, "1.5", "QLab workspaces are intact (references, value encoding, cue targets, round trip, totalCues)")
def c_qlab_form():
    probs = []
    for k in ("qlab", "qlab_base"):
        data = open(F[k], "rb").read()
        raw = plistlib.loads(data)
        if plistlib.dumps(raw, fmt=plistlib.FMT_BINARY, sort_keys=False) != data:
            probs.append("%s: does not round-trip byte for byte" % k)
        wo = raw["$objects"]
        root = wo[raw["$top"]["root"].data]
        rk = {wo[x.data]: v for x, v in zip(root["NS.keys"], root["NS.objects"])}
        inner = plistlib.loads(wo[rk["cueLists"].data]["NS.data"])
        for arc, label in ((raw, "outer"), (inner, "cue lists")):
            n = len(arc["$objects"])

            def scan(x):
                if isinstance(x, U):
                    if x.data >= n:
                        probs.append("%s %s: reference %d out of range" % (k, label, x.data))
                elif isinstance(x, dict):
                    for v in x.values():
                        scan(v)
                elif isinstance(x, list):
                    for v in x:
                        scan(v)
            scan(arc["$objects"])
        # QLab decodes each property one way: a number it writes inline (levels, fade endValues)
        # crashes it when stored as a reference, so every property must use a single encoding
        io = inner["$objects"]
        enc = {}
        for x in io:
            if isinstance(x, dict) and "$class" in x:
                cls = io[x["$class"].data].get("$classname")
                for key, v in x.items():
                    enc.setdefault((cls, key), set()).add(isinstance(v, U))
        for (cls, key), kinds in sorted(enc.items()):
            if len(kinds) > 1:
                probs.append("%s: %s.%s stored both inline and as a reference" % (k, cls, key))
        # a cue's target object must be the cue its target ID names
        R = lambda x: io[x.data] if isinstance(x, U) else x
        S = lambda x: R(x)["NS.string"] if isinstance(R(x), dict) and "NS.string" in R(x) else R(x)
        cues = {i: x for i, x in enumerate(io) if isinstance(x, dict) and "uniqueID" in x and "$class" in x}
        by_id = {S(c["uniqueID"]): i for i, c in cues.items()}
        for c in cues.values():
            t = S(c["cueTargetUniqueID"]) if "cueTargetUniqueID" in c else "$null"
            if t != "$null" and (t not in by_id or c.get("cueTarget") != U(by_id[t])):
                probs.append("%s: %s targets %s but its cueTarget is another cue" % (k, S(c["name"]), t))
        _r, ws, lists = load_ws(F[k])
        count = len(walk(lists["cues"][0]["cues"]))
        if ws.get("totalCues") not in (None, count) and k == "qlab":
            probs.append("%s: totalCues %s, %d cues in the list" % (k, ws.get("totalCues"), count))
    _r, wsb, lb = load_ws(F["qlab_base"])
    return verdict(probs, "show %d cues (totalCues %s), base %d cues" % (len(FLAT), WS.get("totalCues"),
                                                                        len(walk(lb["cues"][0]["cues"]))))


@check(1, "1.6", "CSV and JSON files parse with the expected rows")
def c_tables():
    probs = []
    man = list(csv.DictReader(open(os.path.join(SHOW, "TLM_nov_2026_final_MEDIA_MANIFEST.csv"), newline="")))
    paths = [r["Relative Media Path"] for r in man]
    if len(paths) != 80 or len(set(paths)) != 80:
        probs.append("manifest: %d rows, %d unique (expect 80)" % (len(paths), len(set(paths))))
    smap = list(csv.DictReader(open(os.path.join(SHOW, "TLM_nov_2026_final_MANTRA_SECTION_MAP.csv"), newline="")))
    if len(smap) != 153:
        probs.append("section map: %d rows (expect 153)" % len(smap))
    for f in ("TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv", "TLM_nov_2026_final_SFX_RETARGET_MAP.csv"):
        rows = list(csv.reader(open(os.path.join(SHOW, f), newline="")))
        widths = {len(r) for r in rows if r}
        if len(widths) != 1:
            probs.append("%s: rows of different widths %s" % (f, sorted(widths)))
    json.load(open(os.path.join(SHOW, "BUILD_METADATA.json")))
    list(csv.DictReader(open(os.path.join(PKG, "SOURCE_ZIPS.csv"), newline="")))
    return verdict(probs, "manifest 80, section map 153, fix list and SFX map rectangular, metadata JSON valid")


@check(1, "1.7", "Scripts compile (Python) and parse (bash)")
def c_scripts():
    probs = []
    n = 0
    scratch = tempfile.mkdtemp(prefix="tlm_pyc_")
    for dp, _dn, fs in os.walk(HERE):
        for f in fs:
            if f.endswith(".py"):
                n += 1
                try:
                    py_compile.compile(os.path.join(dp, f), doraise=True, cfile=os.path.join(scratch, f + "c"))
                except py_compile.PyCompileError as e:
                    probs.append(str(e)[:120])
    for sh in (ASSEMBLER, os.path.join(HERE, "build_package.sh")):
        r = subprocess.run(["bash", "-n", sh], capture_output=True, text=True)
        if r.returncode:
            probs.append("%s: %s" % (os.path.basename(sh), r.stderr.strip()[:120]))
    return verdict(probs, "%d Python files compile; assembler and build_package.sh parse" % n)


# --------------------------------------------------------------------------
# Pass 2 — the show
# --------------------------------------------------------------------------

def osc_cues():
    out = []
    for c, parent in FLAT:
        if is_osc(c):
            out.append((c, parent))
    return out


@check(2, "2.1", "Cue numbers are unique; emergency cues E1–E3 present")
def c_numbers():
    nums = [c.get("number") for c, _ in FLAT if c.get("number")]
    dup = sorted({n for n in nums if nums.count(n) > 1})
    probs = ["duplicate cue number %s" % d for d in dup]
    for e in ("E1", "E2", "E3"):
        if e not in nums:
            probs.append("missing %s" % e)
    return verdict(probs, "%d numbered cues, none repeated" % len(nums))


@check(2, "2.2", "Every OSC message: what QLab sends = the cue name, on the MANTRA patch")
def c_osc_payload():
    patches = {p["data"]["uniqueID"]: p["data"].get("name") for p in WS["settings"]["Network"]["networkPatches"]}
    probs = []
    n = 0
    for c, parent in osc_cues():
        n += 1
        s = c["oscString"]
        name = c.get("name", "")
        if not OSC.match(s):
            probs.append("%s: unexpected OSC %r" % (parent.get("number") if parent else "?", s))
        if s not in name:
            probs.append("Q%s: name %r ≠ payload %r" % (parent.get("number") if parent else "?", name[:50], s))
        if patches.get(c.get("networkPatchID")) != "MANTRA":
            probs.append("Q%s: network patch %s" % (parent.get("number") if parent else "?", c.get("networkPatchID")))
    return verdict(probs, "%d OSC cues checked, all on the MANTRA patch" % n)


@check(2, "2.3", "Every OSC target exists in the Mantra show file")
def c_osc_targets():
    secs = SEC["mantra"][0]
    probs = []
    for c, parent in osc_cues():
        p, m, cue, lvl, fade = map(int, OSC.match(c["oscString"]).groups())
        mid = PAGE_ID.get(p, {}).get(m)
        if mid is None or "Memory%d" % mid not in secs:
            probs.append("Q%s: P%d M%d is not a memory" % (parent.get("number"), p, m))
            continue
        n = int(kv(secs["Memory%d" % mid]).get("NumScenes", "1"))
        if not 1 <= cue <= n:
            probs.append("Q%s: P%d M%d cue %d (memory has %d)" % (parent.get("number"), p, m, cue, n))
        if lvl not in (0, 100):
            probs.append("Q%s: level %d" % (parent.get("number"), lvl))
        if not 0 <= fade <= 10000:
            probs.append("Q%s: fade %d ms" % (parent.get("number"), fade))
        if lvl and not kv(secs.get("Memory%d-Cue%d" % (mid, cue - 1), "")).get("Name"):
            probs.append("Q%s: P%d M%d cue %d has no name" % (parent.get("number"), p, m, cue))
    return verdict(probs, "every page/memory/cue exists; levels 0 or 100; fades 0–10 s")


@check(2, "2.4", "Section map names = the Mantra cue names (and the P8 backup copies)")
def c_section_map():
    secs = SEC["mantra"][0]
    probs = []
    rows = list(csv.DictReader(open(os.path.join(SHOW, "TLM_nov_2026_final_MANTRA_SECTION_MAP.csv"), newline="")))
    for r in rows:
        mid, k = int(r["Internal Memory ID"]), int(r["Cue In Section"]) - 1
        name = kv(secs.get("Memory%d-Cue%d" % (mid, k), "")).get("Name", "")
        b = kv(secs.get("Memory70-Cue%d" % (int(r["Backup Position"]) - 1), "")).get("Name", "").replace("BACKUP - ", "")
        if name != r["Cue Name"]:
            probs.append("pos %s: map %r ≠ desk %r" % (r["Backup Position"], r["Cue Name"], name))
        if b != r["Cue Name"]:
            probs.append("P8 pos %s: %r ≠ %r" % (r["Backup Position"], b, r["Cue Name"]))
    # the P8 backup copy carries the same levels and colours as the performance cue
    diffs = 0
    for r in rows:
        mid, k = int(r["Internal Memory ID"]), int(r["Cue In Section"]) - 1
        a = {x: y for x, y in kv(secs["Memory%d-Cue%d" % (mid, k)]).items() if x.startswith("Channel")}
        b = {x: y for x, y in kv(secs["Memory70-Cue%d" % (int(r["Backup Position"]) - 1)]).items() if x.startswith("Channel")}
        if a != b:
            diffs += 1
            if diffs <= 5:
                probs.append("P8 pos %s differs from P%s M%s cue %s" % (r["Backup Position"], r["Performance Page"],
                                                                        r["Playback Memory"], r["Cue In Section"]))
    return verdict(probs, "153 positions: names match, and every P8 backup cue equals its performance cue")


@check(2, "2.5", "Releases: each memory is released as the show leaves it; nothing stacks")
def c_releases():
    live, probs = {}, []
    for g in groups():
        num = g.get("number", "")
        if num.startswith("E") or num == "66":
            continue
        for c, _p in walk(g.get("cues")):
            if not is_osc(c):
                continue
            p, m, cue, lvl, _f = map(int, OSC.match(c["oscString"]).groups())
            if lvl == 0:
                if (p, m) not in live:
                    probs.append("Q%s releases P%d M%d, which is not up" % (num, p, m))
                live.pop((p, m), None)
            else:
                live[(p, m)] = cue
        scene = [k for k in live if k[0] in (2, 3, 4)]
        if len(scene) > 1:
            probs.append("after Q%s: %s up together" % (num, ", ".join("P%dM%d" % k for k in scene)))
        if num == "57b" and (5, 5) in live:
            probs.append("HAYWIRE still up after Q57b")
    end = [k for k in live if k[0] in (2, 3, 4)]
    return verdict(probs, "one scene/song memory up at a time through all %d show groups; ends on %s"
                   % (len(groups()), ", ".join("P%dM%d" % k for k in end)))


@check(2, "2.6", "Flash hits return by themselves (QLab pre-wait 0.1–1.5 s)")
def c_flashes():
    probs, n = [], 0
    for g in groups():
        oscs = [c for c, _ in walk(g.get("cues")) if is_osc(c) and not c["oscString"].endswith("Level=0/Fade=0") or False]
        fires = [c for c in oscs if "/Level=100/" in c["oscString"] and not c["oscString"].startswith("/PlayMemory/Page=5")]
        if len(fires) >= 2 and fires[0]["oscString"].endswith("/Fade=0"):
            n += 1
            pw = fires[1].get("preWait") or 0
            if not 0.1 <= pw <= 1.5:
                probs.append("Q%s: return pre-wait %.2f s" % (g.get("number"), pw))
    return verdict(probs, "%d flash cues, each with an automatic return" % n)


@check(2, "2.7", "Fades target a cue that is already running, with the level in their name")
def c_fades():
    by_id = {c.get("uniqueID"): (i, c) for i, (c, _p) in enumerate(FLAT)}
    probs, n = [], 0
    for i, (c, parent) in enumerate(FLAT):
        name = c.get("name") or ""
        if not name.startswith("FADE"):
            continue
        n += 1
        t = by_id.get(c.get("cueTargetUniqueID"))
        if not t:
            probs.append("%s (in Q%s): target missing" % (name[:40], parent.get("number") if parent else "?"))
            continue
        if t[0] > i:
            probs.append("%s: target comes later in the list" % name[:40])
        e = ((c.get("fade") or {}).get("entries") or {}).get("0", {})
        m = re.match(r"FADE TO (-?\d+) dB", name)
        if m:
            end = e.get("endValue", 0)
            db = 20 * math.log10(end) if end > 0 else -999
            if abs(db - int(m.group(1))) > 0.2:
                probs.append("%s: fades to %.1f dB" % (name[:40], db))
        elif name.startswith("FADE OUT") and "VIDEO" not in name:
            if e.get("endValue", 0) != 0 or not c.get("stopTargetWhenDone"):
                probs.append("%s: does not fade to silence and stop" % name[:40])
    return verdict(probs, "%d fade cues: targets exist and are already running; FADE TO levels match" % n)


@check(2, "2.8", "Audio: every file in the manifest, every manifest file used, levels ≤ 0 dB, songs at 0 dB")
def c_audio():
    man = {r["Relative Media Path"] for r in csv.DictReader(open(os.path.join(SHOW, "TLM_nov_2026_final_MEDIA_MANIFEST.csv"), newline=""))}
    used, probs, n = set(), [], 0
    for c, parent in FLAT:
        f = file_of(c)
        if not f:
            continue
        used.add(f)
        if f not in man:
            probs.append("Q%s uses %s (not in the manifest)" % (parent.get("number") if parent else "?", f))
        if f.startswith("media/audio/"):
            n += 1
            lv = (((c.get("levels") or {}).get("entries") or {}).get("0") or {}).get("initialLevel", 1.0)
            if lv > 1.0001:
                probs.append("%s above 0 dB" % os.path.basename(f))
            if "/01_Music_Songs/" in f and abs(lv - 1.0) > 1e-4:
                probs.append("%s not at 0 dB" % os.path.basename(f))
    for f in sorted(man - used):
        probs.append("manifest file never used: %s" % f)
    return verdict(probs, "%d media targets (%d audio cues) all in the 80-file manifest; all 80 used" % (len(used), n))


def wav_seconds(path):
    """Length of a WAV from its RIFF header (handles WAVE_FORMAT_EXTENSIBLE, which the wave module can't)."""
    import struct
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("%s is not a WAV" % os.path.basename(path))
    pos, rate, size = 12, None, None
    while pos + 8 <= len(data):
        cid, clen = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])[0]
        if cid == b"fmt ":
            rate = struct.unpack("<I", data[pos + 16:pos + 20])[0]        # bytes per second
        elif cid == b"data":
            size = clen
        pos += 8 + clen + (clen & 1)
    return size / rate


@check(2, "2.9", "Bundled placeholder sounds exist and are as long as their cues expect")
def c_bundled():
    probs, n = [], 0
    ends = {}
    for c, _p in FLAT:
        f = file_of(c)
        if f and c.get("endTime"):
            ends.setdefault(f, set()).add(round(float(c["endTime"]), 2))
    for dp, _dn, fs in os.walk(os.path.join(SHOW, "media")):
        for f in fs:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, SHOW)
            if not f.lower().endswith(".wav"):
                continue
            n += 1
            dur = wav_seconds(p)
            for e in ends.get(rel, ()):
                if e > dur + 0.05:
                    probs.append("%s is %.2f s, cue plays to %.2f s" % (f, dur, e))
            if rel not in ends:
                probs.append("%s is bundled but no cue uses it" % f)
    return verdict(probs, "%d bundled WAVs, each used and long enough" % n)


@check(2, "2.10", "No strobe, macro or reset values in the show; chases under 3 flashes a second")
def c_strobe():
    secs = SEC["mantra"][0]
    probs = []
    for name, body in secs.items():
        m = re.fullmatch(r"Memory(\d+)-Cue\d+", name)
        if not m or not 10 <= int(m.group(1)) < 100:
            continue
        for k, v in kv(body).items():
            if re.search(r"_attr_val_(STROBE|COLOR%20MACRO|CONTROL|RESET)$", k) and v != "0":
                probs.append("%s %s=%s" % (name, k, v))
    for name, body in secs.items():
        m = re.fullmatch(r"Memory(\d+)", name)
        if m and kv(body).get("IsChase") == "true":
            bpm = float(kv(body).get("ChaseBpm", "0"))
            if bpm / 60 > 3:
                probs.append("Memory%s chase at %.0f BPM (%.1f steps/s)" % (m.group(1), bpm, bpm / 60))
    return verdict(probs, "strobe, colour macro, control and reset are 0 in every show cue; chases ≤ 3 steps/s")


@check(2, "2.11", "Patch: 40 fixtures, types by number, no address overlaps")
def c_patch():
    probs = []
    for k in ("mantra", "mantra_base"):
        p = kv(SEC[k][0]["Patch"])
        n = int(p["NumPatchItems"])
        if n != 40:
            probs.append("%s: %d patch items" % (k, n))
        used = {}
        for i in range(n):
            ch = int(p["Item%d_Channel" % i]) + 1
            model = p["Item%d_Model" % i]
            a, b = int(p["Item%d_StartDmx" % i]), int(p["Item%d_EndDmx" % i])
            want = ("CX 42 NEW" if ch <= 12 else "ZOOM 12 CHANNEL" if ch <= 22 else "TOURCOB PAR" if ch <= 32 or ch == 39
                    else "PIXBAR 6CH" if ch <= 38 else "HAZER 2CH")
            if model != want:
                probs.append("%s #%d is %s (expect %s)" % (k, ch, model, want))
            for addr in range(a, b + 1):
                if addr in used:
                    probs.append("%s #%d overlaps #%d at U%d:%d" % (k, ch, used[addr], addr // 512 + 1, addr % 512 + 1))
                    break
                used[addr] = ch
    return verdict(probs, "show and base: 12 C42 · 10 Zoom · 11 COB · 6 PixBar · hazer, no overlaps")


@check(2, "2.12", "Fixed FOH C42 jobs: programming follows the positions")
def c_foh_jobs():
    secs = SEC["mantra"][0]

    def lit(mid, k):
        d = kv(secs["Memory%d-Cue%d" % (mid, k)])
        return {int(x.group(1)): int(v) for key, v in d.items()
                for x in [re.fullmatch(r"Channel(\d+)_Level", key)] if x and int(v) > 0 and int(x.group(1)) <= 12}
    probs = []
    faces = {1, 4, 5, 8, 9, 12}
    if set(lit(19, 0)) != faces:
        probs.append("SAFE LIGHT (P2 M10) C42s %s ≠ faces %s" % (sorted(lit(19, 0)), sorted(faces)))
    if set(lit(66, 0)) != faces:
        probs.append("M17 SAFE LIGHT C42s %s" % sorted(lit(66, 0)))
    specials = {"Q5 Spirit": (10, 4, 2), "Q6 Octavia": (10, 5, 11), "Q36 shell": (14, 6, 10), "Q53 Dame": (22, 3, 3),
                "Q54 Flanders": (22, 4, 7), "57c Ariel": (22, 9, 6)}
    for label, (mid, k, want) in specials.items():
        l = lit(mid, k)
        extra = {n: v for n, v in l.items() if n not in faces}
        if set(extra) != {want}:
            probs.append("%s: special C42 %s, expect #%d" % (label, sorted(extra), want))
    return verdict(probs, "faces #1, 4, 5, 8, 9, 12; Spirit #2, Octavia #11, Shell #10, Dame #3, Flanders #7, Ariel #6")


@check(2, "2.13", "Review edits still in place (white flashes, storm palette, house blue, shell levels)")
def c_review_edits():
    secs = SEC["mantra"][0]

    def col(mid, k, ch):
        return int(kv(secs["Memory%d-Cue%d" % (mid, k)]).get("Channel%d_Colour" % ch, "0")) & 0xFFFFFF

    def lvl(mid, k, ch):
        return int(kv(secs["Memory%d-Cue%d" % (mid, k)]).get("Channel%d_Level" % ch, "0")) * 100 // 65535
    probs = []
    for mid, k in ((12, 4), (12, 7), (12, 10), (14, 4), (22, 8), (58, 0)):
        for ch in (13, 21, 23, 33):
            if col(mid, k, ch) != 0xFFFFFF:
                probs.append("flash Memory%d cue %d #%d not white" % (mid, k, ch))
    for k in (3, 5, 6, 8, 9, 11):
        if col(12, k, 23) != col(57, 0, 23):
            probs.append("storm Memory12 cue %d backlight ≠ M08" % k)
    for mid, k in ((10, 0), (10, 1), (10, 2), (15, 0), (25, 1)):
        if col(mid, k, 23) != col(51, 0, 23):
            probs.append("house Memory%d cue %d backlight ≠ M02" % (mid, k))
    for k in (2, 3, 4, 5, 6):
        if lvl(22, k, 23) > 20:
            probs.append("shell Memory22 cue %d backlight %d %%" % (k, lvl(22, k, 23)))
    return verdict(probs, "all four lighting fixes found in the show file")


@check(2, "2.14", "Venue base matches the show file (patch, fixtures, network, rig view, P1, 100–109)")
def c_base():
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_mantra_base.py")], capture_output=True, text=True)
    out = r.stdout.strip().replace("\n", " · ")
    return ("OK" if r.returncode == 0 else "FAIL"), out[:400]


@check(2, "2.15", "The base is a separate package: complete on its own, and nothing of it in the show package")
def c_base_package():
    if not os.path.isdir(BASE_DIR):
        return "FAIL", "base/Plantagenet_Players_Base_2026_r1 is missing (run tools/build_base_package.py)"
    probs = []
    for f in ("Plantagenet_Players_Base_2026_r1.mtr", "Plantagenet_Players_Base_2026_r1.qlab5", "BASE_METADATA.json", "00_READ_ME_FIRST.txt",
              "docs/Plantagenet_Players_Base_2026_r1_Guide.pdf", "docs/Plantagenet_Players_Base_2026_r1_Link_Map.pdf", "docs/Plantagenet_Players_Base_2026_r1_Mantra_Labels.pdf",
              "docs/Plantagenet_Players_Base_2026_r1_Rig_ID_Test.pdf", "docs/Plantagenet_Players_Base_2026_r1_Preview.pdf"):
        if not os.path.exists(os.path.join(BASE_DIR, f)):
            probs.append("missing base/%s" % f)
    for dp, _dn, fs in os.walk(PKG):
        for f in fs:
            if f.startswith(("Plantagenet_Players_Base_2026_r1", "BASE_SHOW_2026")) or (f.endswith((".mtr", ".qlab5"))
                                                            and f not in (os.path.basename(F["mantra"]),
                                                                          os.path.basename(F["qlab"]))):
                probs.append("base file in the show package: %s" % os.path.relpath(os.path.join(dp, f), PKG))
    zp = os.path.join(ROOT, "dist", "Plantagenet_Players_Base_2026_r1.zip")
    if os.path.exists(zp):
        import zipfile
        names = zipfile.ZipFile(zp).namelist()
        for f in ("Plantagenet_Players_Base_2026_r1.mtr", "Plantagenet_Players_Base_2026_r1.qlab5", "00_READ_ME_FIRST.txt", "docs/Plantagenet_Players_Base_2026_r1_Guide.pdf"):
            if "Plantagenet_Players_Base_2026_r1/" + f not in names:
                probs.append("the base zip has no %s" % f)
        if any(n.endswith(os.path.basename(F["mantra"])) for n in names):
            probs.append("the base zip contains the show file")
    return verdict(probs, "base/Plantagenet_Players_Base_2026_r1 complete (files, docs, guide, preview, checksums); "
                          "nothing of it in the show package")


# --------------------------------------------------------------------------
# Pass 3 — paperwork
# --------------------------------------------------------------------------

REBUILD = [["tools/book/build.py"], ["tools/make_base_printouts.py"], ["tools/make_zoom_sheet.py"]]


def pdf_text(path):
    import pymupdf
    d = pymupdf.open(path)
    return [re.sub(r"\s+", " ", p.get_text()).strip() for p in d]


@check(3, "3.1", "Rebuilding the book, printouts and base docs reproduces the committed files")
def c_rebuild():
    if QUICK:
        return "SKIP", "skipped (--quick)"
    tmp = tempfile.mkdtemp(prefix="tlm_verify_")
    try:
        dst = os.path.join(tmp, "repo")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", "private"))
        for cmd in REBUILD:
            r = subprocess.run([sys.executable] + [os.path.join(dst, c) for c in cmd], cwd=dst, capture_output=True,
                               text=True)
            if r.returncode:
                return "FAIL", "%s failed: %s" % (cmd[0], (r.stderr or r.stdout).strip()[-300:])
        probs, n = [], 0
        for area in ("production", "package"):
            for dp, _dn, fs in os.walk(os.path.join(ROOT, area)):
                for f in fs:
                    a = os.path.join(dp, f)
                    rel = os.path.relpath(a, ROOT)
                    b = os.path.join(dst, rel)
                    if "/media/" in rel or rel.endswith((".jpg", ".png", ".mov", ".mp4", ".mp3", ".wav")):
                        continue
                    if "Previz" in rel or "Preview" in rel or "Build_Check" in rel or "BUILD_CHECK" in rel or "File_Guide" in rel:
                        continue            # built by their own tools
                    if not os.path.exists(b):
                        continue
                    n += 1
                    if f.endswith(".pdf"):
                        ta, tb = pdf_text(a), pdf_text(b)
                        if ta != tb:
                            k = next((i for i, (x, y) in enumerate(zip(ta, tb)) if x != y), min(len(ta), len(tb)))
                            probs.append("%s: page %d differs%s" % (rel, k + 1, "" if len(ta) == len(tb)
                                                                     else " (%d vs %d pages)" % (len(ta), len(tb))))
                    elif open(a, "rb").read() != open(b, "rb").read():
                        probs.append("%s differs" % rel)
                # files the build makes that are not committed
            for dp, _dn, fs in os.walk(os.path.join(dst, area)):
                for f in fs:
                    rel = os.path.relpath(os.path.join(dp, f), dst)
                    if not os.path.exists(os.path.join(ROOT, rel)) and "private" not in rel:
                        probs.append("build makes %s, not committed" % rel)
        return verdict(probs, "%d committed outputs compared (PDFs by text, others byte for byte): all current" % n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@check(3, "3.2", "Fixture names, jobs, specials and hang positions agree across the paperwork")
def c_names():
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(HERE, "book"))
    import make_printouts as mp
    import part_b
    import lx_moves
    probs = []
    focus = {n: r for n, _t, _p, _a, r in part_b.FOCUS}
    names = {n: mp.FIXTURES[n - 1][1] for n in range(1, 13)}
    want = {1: "FACE", 2: "SPIRIT", 3: "DAME", 4: "FACE", 5: "FACE", 6: "ARIEL", 7: "FLANDERS", 8: "FACE", 9: "FACE",
            10: "SHELL", 11: "OCTAVIA", 12: "FACE"}
    for n, w in want.items():
        if not names[n].startswith(w):
            probs.append("labels #%d %s (expect %s)" % (n, names[n], w))
        if w != "FACE" and w.title() not in focus[n] and w.lower() not in focus[n].lower():
            probs.append("Part B #%d focus %r does not name %s" % (n, focus[n], w.title()))
        if w == "FACE" and not focus[n].startswith("Face"):
            probs.append("Part B #%d focus %r is not a face light" % (n, focus[n]))
    sp = {s[0]: s[2] for s in part_b.SPECIALS}
    for code, n in (("SP1", 6), ("SP2", 2), ("SP3", 11), ("SP4", 10), ("V1", 3), ("V2", 7)):
        if not sp[code].startswith("#%d " % n):
            probs.append("Part B specials %s = %s (expect #%d)" % (code, sp[code], n))
    mv = lx_moves.moves()
    if sorted(n for n, *_ in mv) != [19, 20, 21, 22, 29, 30, 31, 32]:
        probs.append("moves %s" % [n for n, *_ in mv])
    if any(n <= 12 or 33 <= n <= 38 for n, *_ in mv):
        probs.append("a fixed fixture is on the move list")
    return verdict(probs, "labels, Part B focus/specials and the 8 moves agree; C42s and pelmet PixBars never move")


STALE = [(r"#1–6 faces|FOH #1–6|C42 #1–6\)", "old face numbering"),
         (r'"SP1", "Ariel", "#7|"SP2", "Spirit", "#8|"SP3", "Octavia", "#9|#11–12 C42|#9–12 \(Octavia', "old special numbering"),
         (r"five storm layers", "old Q27 storm text"),
         (r"decide whether the 3 pelmet PixBars|move them here, or keep", "pelmet PixBars are fixed"),
         (r"5dca0842f16f9c12|95cf3c690c2cef57|9301c0f9375e4483", "a superseded file hash"),
         (r"hung under the mid-stage beam", "projector is at LX1")]


@check(3, "3.3", "No stale statements left in the book sources or package notes")
def c_stale():
    probs = []
    places = [os.path.join(HERE, "book")] + [PKG]
    for base in places:
        for dp, _dn, fs in os.walk(base):
            for f in fs:
                if not f.endswith((".py", ".txt", ".csv")) or "__pycache__" in dp:
                    continue
                p = os.path.join(dp, f)
                text = open(p, encoding="utf-8", errors="replace").read()
                for pat, why in STALE:
                    for m in re.finditer(pat, text):
                        line = text.count("\n", 0, m.start()) + 1
                        rel = os.path.relpath(p, ROOT)
                        if rel.endswith("TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv") or "sha256_before" in text[max(0, m.start() - 80):m.start()]:
                            continue
                        if rel.endswith("TLM_nov_2026_final_REVIEW_NOTES.txt") and why == "a superseded file hash":
                            continue
                        probs.append("%s:%d %s" % (rel, line, why))
    return verdict(probs, "none of %d stale patterns found" % len(STALE))


@check(3, "3.4", "Every file the read-me files and README point to exists")
def c_refs():
    probs = []
    texts = {"README.md": os.path.join(ROOT, "README.md"), "READ_ME_FIRST.txt": os.path.join(PKG, "READ_ME_FIRST.txt"),
             "00_START_HERE.txt": os.path.join(SHOW, "00_START_HERE.txt")}
    names = set()
    for dp, _dn, fs in os.walk(ROOT):
        if "/.git" in dp:
            continue
        names.update(fs)
    for label, p in texts.items():
        for m in re.finditer(r"[A-Za-z0-9_\-]+\.(?:py|sh|command|qlab5|mtr|csv|json|pdf|txt)\b", open(p).read()):
            f = m.group(0)
            if f not in names and not f.startswith(("TLM_nov_2026_final_Package", "ASSEMBLY_REPORT", "TLM_R13_1.zip",
                                                    "TLM_nov_2026_final_Build_Check", "TLM_nov_2026_final.zip",
                                                    "Plantagenet_Players_Base_2026_r1.zip", "INSTALL_REPORT")):
                probs.append("%s mentions %s — not found" % (label, f))
    return verdict(sorted(set(probs)), "all file names in README, READ_ME_FIRST and 00_START_HERE exist")


@check(3, "3.5", "Every file in the package, base and production folders is described in the File Guide")
def c_guide():
    sys.path.insert(0, os.path.join(HERE, "book"))
    import file_guide
    missing = file_guide.undocumented()
    total = sum(len(file_guide.files_of(a)) for _t, a in file_guide.AREAS)
    return verdict(["not in the File Guide: %s" % m for m in missing], "all %d files described" % total)


# --------------------------------------------------------------------------

QUICK = "--quick" in sys.argv


def main():
    for run in CHECKS:
        run()
    lines = ["THE LITTLE MERMAID - R13.1 BUILD CHECK", "=" * 38, ""]
    names = {1: "PASS 1 - FILES", 2: "PASS 2 - THE SHOW (QLab <-> Mantra <-> media)", 3: "PASS 3 - PAPERWORK"}
    for p in (1, 2, 3):
        lines.append(names[p])
        for pas, cid, status, title, detail in RESULTS:
            if pas == p:
                lines.append("  [%-4s] %s %s" % (status, cid, title))
                if detail:
                    lines.append("         %s" % detail)
        lines.append("")
    fails = [r for r in RESULTS if r[2] == "FAIL"]
    lines.append("RESULT: %s — %d checks, %d OK, %d failed, %d skipped" % (
        "FAIL" if fails else "PASS", len(RESULTS), sum(r[2] == "OK" for r in RESULTS), len(fails),
        sum(r[2] == "SKIP" for r in RESULTS)))
    text = "\n".join(lines) + "\n"
    print(text)
    if not QUICK:
        open(REPORT + ".txt", "w").write(text)
        json.dump([dict(zip(("pass", "id", "status", "title", "detail"), r)) for r in RESULTS],
                  open(REPORT + ".json", "w"), indent=1, ensure_ascii=False)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
