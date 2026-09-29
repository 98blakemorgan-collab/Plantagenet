#!/usr/bin/env python3
"""Check that the venue base Plantagenet_Players_Base_2026_r1.mtr matches the R13.1 Mantra show file,
and that the QLab base Plantagenet_Players_Base_2026_r1.qlab5 matches Plantagenet_Players_Base_2026_r1.mtr.

The show file is built on the venue base, so these must be identical in both:
custom fixtures, patch, network, rig view, recent colours, live scene, the P1
venue looks (memories 0-9) and the internal venue memories 100-109. Also checks
each file's [ZZ_FileEnd] Size footer.

The QLab base must fire every named P1-P5 memory of the base show, and nothing
that isn't in it.

Usage: python3 tools/check_mantra_base.py [base.mtr] [show.mtr] [base.qlab5]
"""
import os
import plistlib
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_DIR = os.path.join(ROOT, "package", "TLM_nov_2026_final")
BASE = os.path.join(ROOT, "base", "Plantagenet_Players_Base_2026_r1", "Plantagenet_Players_Base_2026_r1.mtr")
SHOW = os.path.join(SHOW_DIR, "TLM_nov_2026_final.mtr")
QLAB_BASE = os.path.join(ROOT, "base", "Plantagenet_Players_Base_2026_r1", "Plantagenet_Players_Base_2026_r1.qlab5")

SHARED = ["CustomFixtures", "Patch", "Network", "RigView", "RecentColours", "LiveScene"]
VENUE_MEMORIES = list(range(0, 10)) + list(range(100, 110))


def sections(path):
    secs, cur = {}, None
    with open(path, encoding="latin-1") as f:
        for line in f.read().split("\n"):
            m = re.match(r"^\[(.*)\]$", line)
            if m:
                cur = m.group(1)
                secs[cur] = []
            elif cur is not None:
                secs[cur].append(line)
    return secs


def qlab_targets(path):
    """(page, memory) of every /PlayMemory OSC message in a QLab 5 workspace."""
    ws = plistlib.load(open(path, "rb"))
    strings = [o for o in ws["$objects"] if isinstance(o, str)]
    for o in ws["$objects"]:
        if isinstance(o, dict) and isinstance(o.get("NS.data"), bytes) and o["NS.data"][:6] == b"bplist":
            inner = plistlib.loads(o["NS.data"])
            if isinstance(inner, dict) and "$objects" in inner:
                strings += [x for x in inner["$objects"] if isinstance(x, str)]
    return {(int(p), int(m)) for s in strings for p, m in re.findall(r"/PlayMemory/Page=(\d+)/Memory=(\d+)/", s)}


def check_qlab(base, qlab):
    secs = sections(base)
    named = set()
    for k, lines in secs.items():
        m = re.fullmatch(r"Memory(\d+)-Cue0", k)
        if m and int(m.group(1)) < 50 and any(l.startswith("Name=") and l != "Name=" for l in lines):
            i = int(m.group(1))
            named.add((i // 10 + 1, i % 10 + 1))
    fired = qlab_targets(qlab)
    problems = ["QLab base fires P%d M%d, which is not in %s" % (p, m, os.path.basename(base))
                for p, m in sorted(fired - named)]
    problems += ["QLab base never fires P%d M%d" % pm for pm in sorted(named - fired)]
    return problems, len(named)


def main(base=BASE, show=SHOW, qlab=QLAB_BASE):
    b, s = sections(base), sections(show)
    names = list(SHARED)
    for n in VENUE_MEMORIES:
        mem = "Memory%d" % n
        names += [mem] + sorted(k for k in set(b) | set(s) if k.startswith(mem + "-"))
    problems = []
    for name in names:
        if name not in b and name not in s:
            continue
        if b.get(name) != s.get(name):
            problems.append("differs: [%s]" % name)
    for path, secs in ((base, b), (show, s)):
        size = next((l.split("=", 1)[1] for l in secs.get("ZZ_FileEnd", []) if l.startswith("Size=")), None)
        if size != str(os.path.getsize(path)):
            problems.append("%s: [ZZ_FileEnd] Size=%s, file is %d bytes"
                            % (os.path.basename(path), size, os.path.getsize(path)))
    checked = sum(1 for n in names if n in b or n in s)
    qlab_problems, nmem = check_qlab(base, qlab)
    problems += qlab_problems
    if problems:
        print("\n".join(problems))
        print("MISMATCH: %d problem(s) in %d sections checked" % (len(problems), checked))
        return 1
    print("OK: %s matches %s (%d sections: patch, fixtures, network, rig view, P1, memories 100-109)"
          % (os.path.basename(base), os.path.basename(show), checked))
    print("OK: %s fires all %d P1-P5 memories of %s and nothing else"
          % (os.path.basename(qlab), nmem, os.path.basename(base)))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
