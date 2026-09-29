#!/usr/bin/env python3
"""Build the separate venue base package: base/Plantagenet_Players_Base_2026_r1 and dist/Plantagenet_Players_Base_2026_r1.zip.

The venue base is the Plantagenet Hall rig on its own: Plantagenet_Players_Base_2026_r1.mtr (patch, fixtures, network, rig view,
venue looks, no show cues), the QLab base Plantagenet_Players_Base_2026_r1.qlab5 that fires it, the base printouts, the base lighting
previz and a guide to all of it. It is kept out of the show package (package/TLM_nov_2026_final): this folder is
its only home, and dist/Plantagenet_Players_Base_2026_r1.zip is its own download.

Usage: python3 tools/build_base_package.py
(Build the base printouts and previz first: python3 tools/make_base_printouts.py; python3 tools/lighting_previz.py --base)
"""
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "book"))
import make_printouts as mp  # noqa: E402
import make_base_printouts as bp  # noqa: E402
from core import (PartDoc, title_block, stats, box, table, H1, H2, P, bullets, steps, notes_area, REV, DATE,  # noqa: E402
                  mm)

SHOW = mp.SHOW
NAME = "Plantagenet_Players_Base_2026_r1"
OUT = os.path.join(ROOT, "base", NAME)
DOCS = os.path.join(OUT, "docs")
ZIP = os.path.join(ROOT, "dist", NAME + ".zip")
PREVIZ = os.path.join(ROOT, "production", "TLM_nov_2026_final", "03_Lighting_Mantra", "Plantagenet_Players_Base_2026_r1_Previz.pdf")
TYPES = {"CX 42 NEW": "Lightsky C42", "ZOOM 12 CHANNEL": "Tour Pro Zoom", "TOURCOB PAR": "TourCOB PAR",
         "PIXBAR 6CH": "PixBar", "HAZER 2CH": "Hazer"}
MODE = {"CX 42 NEW": "11 ch", "ZOOM 12 CHANNEL": "12 ch", "TOURCOB PAR": "6 ch", "PIXBAR 6CH": "6 ch", "HAZER 2CH": "2 ch"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ranges(ns):
    return bp.ranges(ns) if ns else "—"


# --------------------------------------------------------------------------
# The guide
# --------------------------------------------------------------------------

FILES = [("00_READ_ME_FIRST.txt", "What this folder is and the first steps", "Everyone"),
         ("Plantagenet_Players_Base_2026_r1.mtr", "The venue base for the LSC Mantra Lite: patch, fixture library, network, rig view, venue "
          "looks P1 and memories 100–109. No show cues.", "LX — import on the desk"),
         ("Plantagenet_Players_Base_2026_r1.qlab5", "QLab 5 workspace that fires the venue base: venue looks V1–V10, rig ID sweeps I1–I5, "
          "rig test T1–T41, emergency E1–E3", "LX / QLab op — rig check"),
         ("BASE_METADATA.json", "SHA-256 of the two base files and where they came from", "Checking a copy"),
         ("docs/Plantagenet_Players_Base_2026_r1_Guide.pdf", "This guide", "Everyone"),
         ("docs/Plantagenet_Players_Base_2026_r1_Link_Map.pdf", "Which QLab base cue fires which Mantra page/memory, and every fixture's "
          "fader, address and test cue", "LX"),
         ("docs/Plantagenet_Players_Base_2026_r1_Mantra_Labels.pdf", "Desk fader and playback labels for the base (venue names only)", "LX — print"),
         ("docs/Plantagenet_Players_Base_2026_r1_Rig_ID_Test.pdf", "Rig ID test: find every fixture, check type, position, address and mode; "
          "fault table and sign-off", "LX — rig day"),
         ("docs/Plantagenet_Players_Base_2026_r1_Previz.pdf", "The base lighting drawn on photos of the stage: the whole rig, every "
          "venue look, the rig ID sweeps and each fixture on its own", "Everyone")]


def build_guide(path, mems, patch, qlab):
    wsname, net, cues = qlab
    d = PartDoc(path, "", "Venue Base Guide", divider=False, header_left="PLANTAGENET HALL · VENUE BASE")
    d.add(title_block("Plantagenet_Players_Base_2026_r1 · %s" % DATE, "Venue Base Guide",
                      "The Plantagenet Hall lighting rig on its own: the Mantra base, the QLab base that tests it, the "
                      "printouts and how to use them"))
    looks = [i for i in range(10) if i in mems and mems[i]["name"]]
    inner = [i for i in range(100, 110) if i in mems and mems[i]["name"]]
    d.add(stats([(str(len(patch)), "fixtures patched"), (str(len(looks)), "venue looks (P1)"),
                 (str(len(inner)), "venue memories 100–109"), (str(len(cues)), "QLab base cues")]))
    d.add(box("rule", "WHAT THE BASE IS",
              ["**Plantagenet_Players_Base_2026_r1.mtr** is the venue's own Mantra show file: the patch, the five custom fixture types, "
               "the network, the rig view, the venue looks on Page 1 and the internal memories 100–109. It has none of the "
               "Little Mermaid cues. The R13.1 show file is built on it, and the two are checked to be identical in all "
               "of those parts (tools/check_mantra_base.py).",
               "**Plantagenet_Players_Base_2026_r1.qlab5** is a QLab 5 workspace that fires the base: each venue look, every fixture of one "
               "type at once (rig ID), one fixture at a time (rig test) and three emergency cues. Use it for the rig day "
               "and to put the venue back after the show."]))
    d.add(box("verify", "ONLY WITH THE BASE ON THE DESK", "Run Plantagenet_Players_Base_2026_r1.qlab5 only when Plantagenet_Players_Base_2026_r1.mtr is loaded "
              "on the Mantra. With the show file loaded, its P2–P5 test cues would fire show memories instead."))

    d.add(H1("1 Files in this folder"))
    d.add(table(["File", "What it is", "Use"], [[f, w, u] for f, w, u in FILES], [66 * mm, 72 * mm, 32 * mm]))

    d.add(H1("2 The rig as installed"))
    d.add(P("From the venue photos (29 Sep 2026) and the base patch. **The 12 Lightsky C42s are fixed on the FOH bar** in "
            "number order, #1 at the stage-right end, and **the 3 PixBars on the pelmet front are fixed**. Which COB PARs "
            "and PixBars hang where is assumed until the rig ID test."))
    rows = []
    for n in sorted(patch):
        pt = patch[n]
        rows.append(["**%d**" % n, TYPES.get(pt["model"], pt["model"]), mp.INSTALLED.get(n, ""),
                     "U%d : %d–%d" % (pt["u"], pt["a"], pt["b"]), MODE.get(pt["model"], ""), bp.fader(n), "T%d" % n])
    d.add(table(["#", "Fixture", "Hangs now", "DMX", "Mode", "Fader", "Test"], rows,
                [10 * mm, 30 * mm, 30 * mm, 30 * mm, 14 * mm, 30 * mm, 12 * mm]))
    d.add(box("verify", "POWER AND DATA", ["FOH C42s run from the venue dimmers: set those dimmer channels to **NON-DIM** "
              "(hard power) before switching on; never dim an LED fixture.",
              "Universe 1 on the desk XLR (stage rig and hazer); universe 2 over Ethernet to the node 2.0.0.10 for the FOH "
              "bar. Desk 2.0.0.1 / 255.0.0.0, DHCP off; Art-Net and sACN are both on — turn off the one the node doesn't use."]))

    d.add(H1("3 Venue looks and memories"))
    lrows = []
    for i in looks + inner:
        m = mems[i]
        lit = sorted(m["lit"])
        by = {}
        for n in lit:
            by.setdefault(TYPES.get(patch[n]["model"], "?") if n in patch else "?", []).append(n)
        what = " · ".join("%s #%s" % (t, ranges(ns)) for t, ns in by.items()) or "nothing (blackout)"
        desk = ("P1 M%d" % (i + 1)) if i < 10 else ("memory %d" % i)
        qcue = next((c["num"] for c in cues if any(bp.idx(p, mm_) == i for p, mm_, _, _ in c["fires"])), "—")
        lrows.append(["**%s**" % m["name"], desk, qcue, what])
    d.add(table(["Look", "Desk", "QLab base", "What is lit"], lrows, [34 * mm, 22 * mm, 18 * mm, 96 * mm]))
    d.add(P("Memories 100–109 are internal venue memories (rows by type, the three stage areas, blackout); they are not on "
            "a playback page."))

    d.add(H1("4 The QLab base cues"))
    groups = {}
    for c in cues:
        k = re.match(r"[A-Z]+", c["num"] or "")
        groups.setdefault(k.group(0) if k else "", []).append(c)
    purpose = {"V": "Venue looks P1, one at a time — each GO releases the other P1 looks",
               "I": "Rig ID: every fixture of one type at full (I1 C42, I2 Zoom, I3 COB, I4 PixBar); I5 clears",
               "T": "Rig test: one fixture per GO (T1–T40, P2 M1 – P5 M10 test memories), each releasing the one before; "
                    "T41 ends",
               "E": "E1 stop all (QLab panic) · E2 all Mantra memories off · E3 stage work"}
    qrows = [[g, "%s – %s" % (cs[0]["num"], cs[-1]["num"]), str(len(cs)), purpose.get(g, "")]
             for g, cs in groups.items() if g in purpose]
    d.add(table(["Group", "Cues", "Count", "What it does"], qrows, [16 * mm, 26 * mm, 14 * mm, 114 * mm]))

    d.add(H1("5 How to"))
    d.add(H2("Load the venue base on the Mantra"))
    d.add(steps(["Put a FAT32 USB stick in the Mantra. Home › Tools › Export Show — keep that export as the restore point.",
                 "Copy Plantagenet_Players_Base_2026_r1.mtr onto the stick. Home › Tools › Import Show › Plantagenet_Players_Base_2026_r1.mtr.",
                 "Check the five custom fixture types: CX 42 NEW, ZOOM 12 CHANNEL, TOURCOB PAR, PIXBAR 6CH, HAZER 2CH.",
                 "Tools › Setup › Network: 2.0.0.1, 255.0.0.0; turn off Art-Net or sACN (whichever the node doesn't use).",
                 "Tools › Setup › Remote Triggers › Add › OSC · Play Memory · port 8000 (for QLab). Save (T S)."]))
    d.add(H2("Run the rig check from QLab"))
    d.add(steps(["Open Plantagenet_Players_Base_2026_r1.qlab5 on the show Mac. Workspace Settings › Network: MANTRA → wired Ethernet.",
                 "GO I1–I4: count each type against the rig ID test sheet (12 C42 · 10 Zoom · 11 COB · 6 PixBar); I5 clears.",
                 "GO T1–T40: one fixture at a time. Tick lit alone, where it hangs, right type; write the real numbers of "
                 "the LX1/LX2 COBs and the pelmet PixBars.",
                 "Faults: the fault table on the rig ID test (address, mode, cable, terminator). E2 turns everything off."]))
    d.add(H2("Go to the show, and put the venue back afterwards"))
    d.add(steps(["For the show: Home › Tools › Import Show › TLM_nov_2026_final.mtr (in the show "
                 "folder) and open TLM_nov_2026_final.qlab5 — not this QLab base.",
                 "After the last show: Import Plantagenet_Players_Base_2026_r1.mtr, check V1 STAGE WORK from the QLab base or the desk, save "
                 "and export to USB. The venue is back to its own rig and looks."]))

    d.add(H1("6 Lighting previz"))
    d.add(P("docs/Plantagenet_Players_Base_2026_r1_Previz.pdf draws the base on photos of the stage: the whole rig (tabs open and "
            "closed), every venue look, the rig ID sweeps and each fixture on its own, as installed. The same pictures are "
            "on the interactive Venue Base Previz page."))

    d.add(H1("7 Checksums"))
    d.add(table(["File", "SHA-256"], [[f, sha(os.path.join(OUT, f))] for f in ("Plantagenet_Players_Base_2026_r1.mtr", "Plantagenet_Players_Base_2026_r1.qlab5")],
                [44 * mm, 126 * mm]))
    d.add(notes_area("Rig day notes", 6))
    d.build()
    return path


READ_ME = """PLANTAGENET HALL - VENUE BASE  (Plantagenet_Players_Base_2026_r1, {date})
=======================================================

The venue's lighting rig on its own, separate from The Little Mermaid show.

  Plantagenet_Players_Base_2026_r1.mtr     Mantra venue base: patch, fixtures, network, rig
                         view, venue looks P1 and memories 100-109.
                         No show cues. Import it to put the desk back to
                         the venue, or to run the rig check.
  Plantagenet_Players_Base_2026_r1.qlab5   QLab base that fires it: V1-V10 venue looks,
                         I1-I5 rig ID (one type at a time), T1-T41 rig test
                         (one fixture per GO), E1-E3 emergency.
                         Only use it with Plantagenet_Players_Base_2026_r1.mtr on the desk.
  BASE_METADATA.json     checksums of the two files
  docs/                  Venue Base Guide (start here), link map, desk
                         labels, rig ID test, base lighting previz

FIRST
  1. Read docs/Plantagenet_Players_Base_2026_r1_Guide.pdf.
  2. Mantra: export the current show to USB, then Home > Tools > Import
     Show > Plantagenet_Players_Base_2026_r1.mtr.
  3. QLab: open Plantagenet_Players_Base_2026_r1.qlab5, Workspace Settings > Network >
     MANTRA -> wired Ethernet. Mantra remote trigger: OSC, Play Memory,
     port 8000.
  4. Rig day: print docs/Plantagenet_Players_Base_2026_r1_Rig_ID_Test.pdf and run I1-I4,
     then T1-T40.

The 12 Lightsky C42s (FOH bar) and the 3 PixBars on the pelmet front are
fixed and cannot be moved. FOH dimmer channels feeding the C42s: NON-DIM.

Checksums (SHA-256)
  Plantagenet_Players_Base_2026_r1.mtr    {mtr}
  Plantagenet_Players_Base_2026_r1.qlab5  {qlab}

This base is separate from the show package (TLM_nov_2026_final.zip) and is
not included in it. The show file is built on this base: its patch,
fixtures, network, rig view, venue looks and memories 100-109 are checked
to be identical (tools/check_mantra_base.py).
"""


def main():
    if not os.path.exists(PREVIZ):
        raise SystemExit("Build the base previz first: python3 tools/lighting_previz.py --base")
    for f in ("%s.mtr" % NAME, "%s.qlab5" % NAME) + tuple("docs/%s_%s.pdf" % (NAME, d) for d in
                                                              ("Link_Map", "Mantra_Labels", "Rig_ID_Test")):
        if not os.path.exists(os.path.join(OUT, f)):
            raise SystemExit("missing %s (base printouts: python3 tools/make_base_printouts.py)" % f)
    os.makedirs(DOCS, exist_ok=True)
    shutil.copy2(PREVIZ, os.path.join(DOCS, os.path.basename(PREVIZ)))
    mems, patch = bp.load_mtr()
    qlab = bp.load_qlab()
    build_guide(os.path.join(DOCS, "Plantagenet_Players_Base_2026_r1_Guide.pdf"), mems, patch, qlab)
    hashes = {"mantra_base": sha(os.path.join(OUT, "Plantagenet_Players_Base_2026_r1.mtr")),
              "qlab_base": sha(os.path.join(OUT, "Plantagenet_Players_Base_2026_r1.qlab5"))}
    json.dump({"name": NAME, "date": DATE, "home": "base/%s (not in the show package)" % NAME, "sha256": hashes,
               "fixtures": len(patch), "qlab_base_cues": len(qlab[2])},
              open(os.path.join(OUT, "BASE_METADATA.json"), "w"), indent=2)
    open(os.path.join(OUT, "00_READ_ME_FIRST.txt"), "w").write(
        READ_ME.format(date=DATE, mtr=hashes["mantra_base"], qlab=hashes["qlab_base"]))
    os.makedirs(os.path.dirname(ZIP), exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _dn, fs in os.walk(OUT):
            for f in sorted(fs):
                p = os.path.join(dp, f)
                z.write(p, os.path.join(NAME, os.path.relpath(p, OUT)))
    print(os.path.relpath(OUT, ROOT))
    print(os.path.relpath(ZIP, ROOT))


if __name__ == "__main__":
    main()
