#!/usr/bin/env python3
"""Build the zoom adjustment sheet for the Tour Pro Zooms (#13-22).

Read from the show files, so the numbers match what the desk will do:
  - BASE_SHOW_2026.mtr and TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr
      Zoom channel layout, patch addresses, the ZOOM value every memory stores
  - BASE_SHOW_2026.qlab5   the QLab test cue that brings each Zoom up alone

Usage:  python3 tools/make_zoom_sheet.py            (needs reportlab)
Output: package/TLM_R13_REBUILT_Show_Files/docs/TLM_R13_1_Zoom_Adjustment.pdf
        (also copied to production/TLM_Show_R13_1/03_Lighting_Mantra)
"""
import collections
import os
import re
import shutil

import make_base_printouts as bp
import make_printouts as mp
from make_printouts import P, esc, mm, colors, landscape, A4, Spacer, Table, TableStyle, KeepTogether

ZOOMS = range(13, 23)
MODEL = "ZOOM 12 CHANNEL"
FILES = [("base", os.path.join(mp.SHOW, "BASE_SHOW_2026.mtr")), ("show", mp.MTR)]
NOTES = {19: "voice special V3 Theodore: book says 13°", 20: "voice special V4 Marina: book says 13°"}


def sections(path):
    t = open(path, encoding="latin-1").read()
    secs = re.split(r"^\[([^\]]+)\]\s*$", t, flags=re.M)
    return {secs[i]: secs[i + 1] for i in range(1, len(secs), 2)}


def channel_layout(d):
    """[(channel, attribute name, home value)] of the Zoom fixture type."""
    cf = dict(l.split("=", 1) for l in d["CustomFixtures"].splitlines() if "=" in l)
    cfn = next(k.split("_")[0] for k, v in cf.items() if k.endswith("_Model") and v == MODEL)
    atts = {k.split("_")[1] for k in cf if re.match(cfn + r"_Att\d+_", k)}
    rows = [(int(cf["%s_%s_ChanNum" % (cfn, a)]), cf["%s_%s_Name" % (cfn, a)], cf["%s_%s_HomeVal" % (cfn, a)])
            for a in atts]
    return sorted(rows)


def stored_zoom(d):
    """fixture -> Counter of the ZOOM values stored in the file's memories and cues."""
    out = collections.defaultdict(collections.Counter)
    for name, body in d.items():
        if name.startswith("Memory"):
            for m in re.finditer(r"^Channel(\d+)_attr_val_ZOOM=(\d+)", body, re.M):
                out[int(m.group(1))][int(m.group(2))] += 1
    return out


def summary(counter):
    if not counter:
        return "not stored"
    return " / ".join("%d (×%d)" % (v, n) for v, n in sorted(counter.items()))


def build():
    st = mp.styles(7.6)
    data = {k: sections(p) for k, p in FILES}
    layout = channel_layout(data["show"])
    zoom_ch = next(c for c, name, _ in layout if name == "ZOOM")
    stored = {k: stored_zoom(d) for k, d in data.items()}
    total = {k: sum(sum(c.values()) for f, c in s.items() if f in ZOOMS) for k, s in stored.items()}
    mems, patch = bp.load_mtr()
    tests = {}
    for c in bp.load_qlab()[2]:
        if c["num"].startswith("T"):
            for p, m, _, _ in c["fires"]:
                lit = mems[bp.idx(p, m)]["lit"]
                if len(lit) == 1:
                    tests[next(iter(lit))] = c["num"]

    path = os.path.join(mp.OUT, "TLM_R13_1_Zoom_Adjustment.pdf")
    doc = mp.Doc(path, "TLM R13.1 Zoom Adjustment", "%s · zoom sheet · %s · %s" % (mp.SHOWNAME, mp.REV, mp.DATE),
                 landscape(A4))
    story = [P("Adjusting zoom — Tour Pro Zoom #13–22", st["title"]),
             P("Read from BASE_SHOW_2026.mtr, %s and BASE_SHOW_2026.qlab5." % os.path.basename(mp.MTR), st["sub"]),
             Spacer(0, 3 * mm)]

    warn = Table([[P("<b>WHY A ZOOM CHANGE WON'T STICK</b> &nbsp; Every memory stores a ZOOM value for #13–22 "
                     "(%d entries in the show file, %d in the base), all set to snap. The Mantra is latest-takes-"
                     "precedence, so the next memory QLab fires puts zoom straight back to the stored value. "
                     "Turning the encoder is fine for finding the right value, but to keep it the value has to be "
                     "written into the memories (step 2)." % (total["show"], total["base"]), st["note"])]],
                 colWidths=[277 * mm])
    warn.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.2, mp.INK), ("BACKGROUND", (0, 0), (-1, -1), mp.TINT),
                              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story += [warn, Spacer(0, 3 * mm)]

    steps = [
        ["<b>1 Find the value</b><br/>(focus session)",
         "Load BASE_SHOW_2026.mtr on the desk and BASE_SHOW_2026.qlab5 in QLab. GO the fixture's test cue (table "
         "below) so it is the only light on. On the Mantra select that fixture, open its attributes and turn "
         "ZOOM (look under the beam attributes — the exact Mantra Lite button names are not confirmed here). "
         "Zoom snaps, range 0–255. Check the fixture manual for which end is narrow, or just watch the beam. "
         "Write the number in the table. Barn doors and aim are set by hand at the fixture."],
        ["<b>2 Make it stick</b>",
         "<b>A · recommended:</b> send the numbers (e.g. “#13–18 = 120, #19–20 = 40”). They get written into "
         "every memory of both .mtr files, checksums and checks updated; then re-import the show file on the "
         "desk (Home › Tools › Import Show).<br/><b>B · on the desk:</b> set the zoom and update every memory "
         "that uses that fixture, on every page. Slow and easy to miss one — run the whole show after."],
        ["<b>3 Check</b>",
         "With the show file loaded, fire a few scenes from QLab that use the Zooms (LX1 wash #13–18, side "
         "#21–22, voice specials #19–20 at Q55/Q56) and confirm the beam stays where you set it."],
    ]
    t = Table([[P(a, st["b"]), P(b, st["b"])] for a, b in steps], colWidths=[34 * mm, 243 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, mp.RULE),
                           ("LINEABOVE", (0, 0), (-1, 0), 0.8, mp.INK),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    story += [t, Spacer(0, 4 * mm)]

    rows = []
    for n in ZOOMS:
        pt = patch[n]
        rows.append(["<b>%d</b>" % n, "<b>%s</b>" % esc(mp.FIXTURES[n - 1][1]), mp.HANG[n], bp.fader(n),
                     "U%d : %d" % (pt["u"], pt["a"]), "<b>U%d : %d</b>" % (pt["u"], pt["a"] + zoom_ch - 1),
                     tests.get(n, "—"), summary(stored["show"].get(n)), summary(stored["base"].get(n)),
                     esc(NOTES.get(n, "")), "", "☐"])
    table = mp.make_table(["#", "Label", "Hung", "Fader", "DMX start", "ZOOM ch %d" % zoom_ch, "QLab test",
                           "Stored now: show (× entries)", "Stored now: base", "Note", "NEW VALUE", "Beam OK"],
                          rows, [9 * mm, 21 * mm, 17 * mm, 20 * mm, 19 * mm, 20 * mm, 15 * mm, 34 * mm, 26 * mm,
                                 44 * mm, 36 * mm, 16 * mm], st)
    table.setStyle(TableStyle([("ROWBACKGROUNDS", (10, 1), (10, -1), [colors.white]),
                               ("BOX", (10, 1), (10, -1), 1.2, mp.INK),
                               ("TOPPADDING", (0, 1), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 1), (-1, -1), 4.5)]))
    story += [KeepTogether([P("Fixtures and where zoom lives — fill in NEW VALUE at the focus session", st["h"]),
                            Spacer(0, 1 * mm), table])]

    story += [Spacer(0, 3 * mm),
              P("<b>Zoom 12-channel layout</b> (from the desk file): " + " · ".join(
                  "%d %s%s" % (c, name.title(), " (home %s)" % home if home != "0" else "")
                  for c, name, home in layout) +
                ". Keep Control, Strobe, Other, Default, Auto speed and Reset at 0.", st["note"])]
    doc.build(story)
    shutil.copy(path, os.path.join(bp.PROD, os.path.basename(path)))
    return path


if __name__ == "__main__":
    print(os.path.relpath(build(), mp.ROOT))
