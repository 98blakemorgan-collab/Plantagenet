#!/usr/bin/env python3
"""Give the 12 fixed Lightsky C42s on the FOH bar jobs that suit where they hang.

The C42s cannot be moved. They hang on the FOH bar in desk-number order, #1 at the
stage-right (house-left) end to #12 at the stage-left end (venue photos; the venue
base STAGE RIGHT / CENTRE / STAGE LEFT looks use #1-4 / #5-8 / #9-12). With the old
jobs every face light came from the house-left half and every special from the
house-right half, so the jobs are reassigned by position:

  face DSR  #1 + #4    face DSC  #5 + #8    face DSL  #9 + #12   (a cross pair per zone)
  SP2 Spirit #2 · V1 Dame #3 · SP1 Ariel #6 · V2 Flanders #7 · SP4 Shell #10 · SP3 Octavia #11

In TLM_nov_2026_final.mtr every show memory (10-70) moves each
job's programming to its new desk number. Patch, fixtures, network, rig view, live
scene, the venue P1 looks (0-9) and memories 100-109 are not touched, so the file
still matches Plantagenet_Players_Base_2026_r1.mtr (tools/check_mantra_base.py).

Runs only on the file it was written for (SHA-256 checked) and records the new
hash in BUILD_METADATA.json and ASSEMBLE_TLM_nov_2026_final.command.
"""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(ROOT, "package", "TLM_nov_2026_final")
MTR = os.path.join(SHOW, "TLM_nov_2026_final.mtr")
META = os.path.join(SHOW, "BUILD_METADATA.json")
ASSEMBLER = os.path.join(ROOT, "package", "ASSEMBLE_TLM_nov_2026_final.command")
MTR_IN = "9301c0f9375e4483a6f0e819f23f2a2466e027e322dcf32a5a12f69522619a1b"

# new desk number -> the desk number whose job (and programming) it takes over
OLD_OF = {1: 1, 2: 8, 3: 11, 4: 2, 5: 3, 6: 7, 7: 12, 8: 4, 9: 5, 10: 10, 11: 9, 12: 6}
NEW_OF = {old: new for new, old in OLD_OF.items()}
SHOW_MEMORIES = range(10, 100)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def renumber(body):
    lines = body.split("\n")
    assert lines[-2:] == ["", ""] or lines[-1] == "", repr(body[-20:])
    keep_tail = []
    while lines and lines[-1] == "":
        keep_tail.append(lines.pop())
    assert lines == sorted(lines), "section not in key order"

    def ren(line):
        m = re.match(r"Channel(\d+)_", line)
        if m and int(m.group(1)) in NEW_OF:
            return "Channel%d_%s" % (NEW_OF[int(m.group(1))], line[m.end():])
        return line
    return "\n".join(sorted(ren(l) for l in lines) + keep_tail)


def main():
    assert sorted(OLD_OF) == sorted(OLD_OF.values()) == list(range(1, 13))
    assert sha(MTR) == MTR_IN, "Mantra file is not the one these edits were written for"
    text = open(MTR, encoding="latin-1").read()
    parts = re.split(r"^\[([^\]]+)\]\n", text, flags=re.M)
    names, bodies = parts[1::2], parts[2::2]
    changed = 0
    for i, name in enumerate(names):
        m = re.fullmatch(r"Memory(\d+)(-Cue\d+)?", name)
        if not m or int(m.group(1)) not in SHOW_MEMORIES or not m.group(2):
            continue
        new = renumber(bodies[i])
        if new != bodies[i]:
            bodies[i] = new
            changed += 1
    out = "".join("[%s]\n%s" % (n, b) for n, b in zip(names, bodies))
    size = len(out.encode("latin-1"))
    out = re.sub(r"(\[ZZ_FileEnd\]\nSize=)\d+", r"\g<1>%d" % size, out)
    assert len(out.encode("latin-1")) == size
    open(MTR, "w", encoding="latin-1", newline="").write(out)

    new_sha = sha(MTR)
    meta = json.load(open(META))
    meta["sha256_before_fixed_foh_jobs"] = {"mantra": MTR_IN}
    meta["sha256"]["mantra"] = new_sha
    meta["r13_1_fixed_foh_jobs"] = [
        "C42 #1-12 are fixed on the FOH bar in number order (#1 stage-right end); jobs reassigned by position: "
        "faces DSR #1+#4, DSC #5+#8, DSL #9+#12; SP2 Spirit #2, V1 Dame #3, SP1 Ariel #6, V2 Flanders #7, "
        "SP4 Shell #10, SP3 Octavia #11",
        "Mantra show memories 10-70: each job's programming moved to its new desk number (%d cue sections); "
        "patch, fixtures, network, rig view, live scene, P1 and memories 100-109 unchanged" % changed,
    ]
    json.dump(meta, open(META, "w"), indent=2, ensure_ascii=False)
    open(META, "a").write("\n")
    asm = open(ASSEMBLER, newline="").read()
    assert asm.count('MTR_SHA="%s"' % MTR_IN) == 1
    open(ASSEMBLER, "w", newline="").write(asm.replace('MTR_SHA="%s"' % MTR_IN, 'MTR_SHA="%s"' % new_sha))
    print("%d cue sections renumbered; new SHA-256 %s" % (changed, new_sha))


if __name__ == "__main__":
    main()
