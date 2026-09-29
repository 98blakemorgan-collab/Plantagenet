#!/usr/bin/env python3
"""Repair TLM_nov_2026_final.qlab5 so QLab can open it (it crashed on load).

tools/apply_lx_sound_edits.py wrote two things QLab cannot decode:

  1. 58 AudioLevelKnobs.initialLevel and 4 FadeValueEntry.endValue values were stored as
     references to a number object. QLab stores these inline and decodes them as plain
     numbers, so it throws on the reference and the workspace crashes as it opens.
     They are put back inline, with the same values.
  2. The Q26 fade (FADE TO -21 dB Q22, formerly FADE OUT Q24) had its target ID moved to
     Q22 but its cueTarget still pointed at the Q24 groan cue. It now points at Q22.

No level, time, name or cue changes. The number objects left unreferenced by (1) stay
in the archive (unreferenced objects are ignored when QLab reads it).
Records the new checksum in BUILD_METADATA.json and the assembler. Runs only once.
"""
import hashlib
import json
import os
import plistlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(ROOT, "package", "TLM_nov_2026_final")
QLAB = os.path.join(SHOW, "TLM_nov_2026_final.qlab5")
QLAB_IN = "97f1e0cfd574bc1839165e23407fac5d3847985f9ff87cb30de4f85a6c6f6774"
INLINE = {("AudioLevelKnobs", "initialLevel"), ("FadeValueEntry", "endValue")}
U = plistlib.UID


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    assert sha(QLAB) == QLAB_IN, "not the workspace this repair was written for"
    raw = plistlib.load(open(QLAB, "rb"))
    wo = raw["$objects"]
    root = wo[raw["$top"]["root"].data]
    rk = {wo[k.data]: v for k, v in zip(root["NS.keys"], root["NS.objects"])}
    blob = wo[rk["cueLists"].data]
    arc = plistlib.loads(blob["NS.data"])
    o = arc["$objects"]

    def R(x):
        return o[x.data] if isinstance(x, U) else x

    def S(x):
        v = R(x)
        return v["NS.string"] if isinstance(v, dict) and "NS.string" in v else v

    n_inline = 0
    for x in o:
        if isinstance(x, dict) and "$class" in x:
            cls = o[x["$class"].data]["$classname"]
            for k, v in list(x.items()):
                if (cls, k) in INLINE and isinstance(v, U):
                    assert isinstance(o[v.data], float), (cls, k, o[v.data])
                    x[k] = o[v.data]
                    n_inline += 1
    assert n_inline == 62, n_inline

    cues = {i: x for i, x in enumerate(o) if isinstance(x, dict) and "uniqueID" in x and "$class" in x}
    by_id = {S(c["uniqueID"]): i for i, c in cues.items()}
    fixed = []
    for i, c in cues.items():
        t = S(c.get("cueTargetUniqueID")) if "cueTargetUniqueID" in c else "$null"
        if t in by_id and c["cueTarget"].data != by_id[t]:
            c["cueTarget"] = U(by_id[t])
            fixed.append(S(c["name"]))
    assert fixed == ["FADE TO -21 dB Q22 SFX Wind/rain + ship creaks"], fixed

    blob["NS.data"] = plistlib.dumps(arc, fmt=plistlib.FMT_BINARY, sort_keys=False)
    open(QLAB, "wb").write(plistlib.dumps(raw, fmt=plistlib.FMT_BINARY, sort_keys=False))
    new = sha(QLAB)

    meta_p = os.path.join(SHOW, "BUILD_METADATA.json")
    meta = json.load(open(meta_p))
    meta["sha256"]["qlab"] = new
    meta.setdefault("final_names", []).append(
        "QLab load crash fixed (tools/fix_qlab_decode.py): 62 level/fade values stored inline again as QLab "
        "writes them; the Q26 fade's cueTarget now points at Q22 to match its target ID")
    json.dump(meta, open(meta_p, "w"), indent=2, ensure_ascii=False)
    open(meta_p, "a").write("\n")
    asm_p = os.path.join(ROOT, "package", "ASSEMBLE_TLM_nov_2026_final.command")
    asm = open(asm_p, newline="").read()
    assert asm.count('QLAB_SHA="%s"' % QLAB_IN) == 1
    open(asm_p, "w", newline="").write(asm.replace('QLAB_SHA="%s"' % QLAB_IN, 'QLAB_SHA="%s"' % new))
    print("%d values inline again; cueTarget fixed: %s" % (n_inline, fixed[0]))
    print("show QLab SHA-256 %s" % new)


if __name__ == "__main__":
    main()
