#!/usr/bin/env python3
"""Check that the venue base BASE_SHOW_2026.mtr matches the R13.1 Mantra show file.

The show file is built on the venue base, so these must be identical in both:
custom fixtures, patch, network, rig view, recent colours, live scene, the P1
venue looks (memories 0-9) and the internal venue memories 100-109. Also checks
each file's [ZZ_FileEnd] Size footer.

Usage: python3 tools/check_mantra_base.py [base.mtr] [show.mtr]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_DIR = os.path.join(ROOT, "package", "TLM_R13_REBUILT_Show_Files")
BASE = os.path.join(SHOW_DIR, "BASE_SHOW_2026.mtr")
SHOW = os.path.join(SHOW_DIR, "TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr")

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


def main(base=BASE, show=SHOW):
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
    if problems:
        print("\n".join(problems))
        print("MISMATCH: %d problem(s) in %d sections checked" % (len(problems), checked))
        return 1
    print("OK: %s matches %s (%d sections: patch, fixtures, network, rig view, P1, memories 100-109)"
          % (os.path.basename(base), os.path.basename(show), checked))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
