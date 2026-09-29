#!/usr/bin/env python3
"""Give the two QLab workspaces their final names inside the file, to match the file names.

  TLM_nov_2026_final.qlab5                 workspaceName TLM_Show_R13_1 -> TLM_nov_2026_final
  Plantagenet_Players_Base_2026_r1.qlab5   workspaceName BASE_SHOW_2026 -> Plantagenet_Players_Base_2026_r1,
                                           and the two cue texts that name the base file

Only strings change; every cue, setting, target and OSC message is untouched (checked after writing).
Records the new show checksum in BUILD_METADATA.json and the assembler; the base checksum is written by
tools/build_base_package.py. Runs only once (it checks the old names are there).
"""
import hashlib
import json
import os
import plistlib
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(ROOT, "package", "TLM_nov_2026_final")
BASE = os.path.join(ROOT, "base", "Plantagenet_Players_Base_2026_r1")
JOBS = [(os.path.join(SHOW, "TLM_nov_2026_final.qlab5"), "TLM_Show_R13_1", "TLM_nov_2026_final", False),
        (os.path.join(BASE, "Plantagenet_Players_Base_2026_r1.qlab5"), "BASE_SHOW_2026", "Plantagenet_Players_Base_2026_r1",
         True)]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rename(path, old, new, inner_too):
    raw = plistlib.load(open(path, "rb"))
    objs = raw["$objects"]
    root = objs[raw["$top"]["root"].data]
    keys = {objs[k.data]: v for k, v in zip(root["NS.keys"], root["NS.objects"])}
    wn = keys["workspaceName"].data
    assert objs[wn] == old, (path, objs[wn])
    objs[wn] = new
    blob = objs[keys["cueLists"].data]
    inner = plistlib.loads(blob["NS.data"])
    before = [o for o in inner["$objects"]]
    n = 0
    if inner_too:
        for i, o in enumerate(inner["$objects"]):
            if isinstance(o, str) and old in o:
                inner["$objects"][i] = o.replace(old, new)
                n += 1
        blob["NS.data"] = plistlib.dumps(inner, fmt=plistlib.FMT_BINARY, sort_keys=False)
    after = inner["$objects"]
    changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    assert len(before) == len(after) and all(isinstance(before[i], str) for i in changed)
    open(path, "wb").write(plistlib.dumps(raw, fmt=plistlib.FMT_BINARY, sort_keys=False))
    return n


def main():
    old_show = sha(JOBS[0][0])
    for path, old, new, inner in JOBS:
        n = rename(path, old, new, inner)
        print("%s: workspaceName -> %s%s" % (os.path.basename(path), new, (", %d cue texts" % n) if n else ""))
    new_show = sha(JOBS[0][0])
    meta_p = os.path.join(SHOW, "BUILD_METADATA.json")
    meta = json.load(open(meta_p))
    meta["sha256"]["qlab"] = new_show
    meta.setdefault("final_names", []).append("QLab workspaceName set to TLM_nov_2026_final (strings only)")
    json.dump(meta, open(meta_p, "w"), indent=2, ensure_ascii=False)
    open(meta_p, "a").write("\n")
    asm_p = os.path.join(ROOT, "package", "ASSEMBLE_TLM_nov_2026_final.command")
    asm = open(asm_p, newline="").read()
    assert asm.count('QLAB_SHA="%s"' % old_show) == 1
    open(asm_p, "w", newline="").write(asm.replace('QLAB_SHA="%s"' % old_show, 'QLAB_SHA="%s"' % new_show))
    print("show QLab SHA-256 %s" % new_show)


if __name__ == "__main__":
    main()
