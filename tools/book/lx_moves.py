"""Part B3 Rig Move Guide, and the stand-alone Lighting Changes summary.

Both are built from the same rig data as Part B and the layout plan (B2): the as-installed positions
(make_printouts.INSTALLED, from the venue photos) and the show positions (make_printouts.HANG). A fixture moves
when the two differ. The C42s on the FOH bar and the three PixBars on the pelmet front are fixed and never move.
"""
import os
import re

from core import (PartDoc, title_block, stats, box, table, H1, H2, P, bullets, steps, checklist, notes_area,
                  picture, swatch_strip, swatch_legend, REV, DATE, mm)
import make_printouts as mp
import part_b
import show as S_

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PHOTOS = os.path.join(ROOT, "production", "assets", "venue_photos")
FOCUS = {n: (t, pos, addr, role) for n, t, pos, addr, role in part_b.FOCUS}
TYPE = {"C42": "Lightsky C42", "ZM": "Tour Pro Zoom", "COB": "TourCOB PAR", "PIX": "PixBar", "HAZE": "Hazer",
        "PIN": "Pinspot"}

# Where each moved fixture goes, in words, and how it is hung there
WHERE = {19: ("LX2", "between the COB PARs, just stage-right of centre", "hook clamp + bond; 13°, barn doors"),
         20: ("LX2", "between the COB PARs, just stage-left of centre", "hook clamp + bond; 13°, barn doors"),
         21: ("SR boom", "top of the boom, about 2.8 m", "boom arm + bond; aims across to SL at head height"),
         22: ("SL boom", "top of the boom, about 2.8 m", "boom arm + bond; aims across to SR at head height"),
         29: ("SR boom", "boom arm about 1.2 m (mid)", "boom arm + bond; knee to hip across the stage"),
         30: ("SR boom", "boom arm about 0.4 m (shin)", "boom arm + bond; shins and feet across the stage"),
         31: ("SL boom", "boom arm about 1.2 m (mid)", "boom arm + bond; knee to hip across the stage"),
         32: ("SL boom", "boom arm about 0.4 m (shin)", "boom arm + bond; shins and feet across the stage")}

PHOTO_CAPTIONS = [
    ("14_FOH_bar_C42_1-12_numbered.jpg", "FOH bar from the stage: C42 #12 … #1 (#1 at the stage-right end). FIXED."),
    ("06_Pelmet_front_PixBars_and_FOH_bar.jpg", "Pelmet front, in front of the main curtain: 3 PixBars (FIXED) and speakers."),
    ("05_LX1_left_end.jpg", "LX1 left end: 2 Zooms."),
    ("07_LX1_left_group.jpg", "LX1 left group: COB, 3 Zooms, COB."),
    ("09_LX1_middle_group.jpg", "LX1 middle group: COB, 3 Zooms, COB; projector beside it."),
    ("10_LX1_right_end.jpg", "LX1 right end: 2 Zooms."),
    ("11_LX2_left.jpg", "LX2 left: COB PARs and PixBars."),
    ("12_LX2_middle.jpg", "LX2 middle: COB PARs and PixBars."),
    ("13_LX2_back_right_and_projector.jpg", "LX2 back right: COB PARs, PixBars, the wall COB; projector at LX1 beyond."),
    ("08_Stage_to_house_FOH_bar.jpg", "The house from the stage: FOH bar over the seating."),
]


def _norm(pos):
    return re.sub(r" \d+$", "", pos or "")


def moves():
    """[(n, type, from, to)] for every fixture whose show position differs from where it hangs now."""
    out = []
    for n in sorted(FOCUS):
        here, there = _norm(mp.INSTALLED.get(n)), _norm(mp.HANG.get(n))
        if here and there and here != there:
            out.append((n, FOCUS[n][0], here, there))
    return out


STAYS = [("FOH bar", "Lightsky C42 #1–12", "FIXED — cannot be moved. Focus only; jobs go by position (Part B §1)."),
         ("Pelmet front", "3 × PixBar", "FIXED — cannot be moved. Tabs / apron wash; tilt off the front rows."),
         ("LX1", "Zoom #13–18", "Stay on LX1. Slide along the bar to even the spacing once #19–22 and the COBs are off."),
         ("LX1", "Projector", "Stays at the centre of LX1; throws upstage onto the back wall."),
         ("LX2", "COB #23–28 · 3 × PixBar", "Stay: backlight and effect row."),
         ("LX2 wall bracket", "COB #39", "Stays where it is (confirm it is #39)."),
         ("Floor, upstage", "Hazer #40", "Placed on the floor for the show (no rigging).")]


def photo_grid(d, width=82 * mm):
    from reportlab.platypus import Table, TableStyle
    cells = []
    for f, cap in PHOTO_CAPTIONS:
        path = os.path.join(PHOTOS, f)
        if os.path.exists(path):
            cells.append([picture(path, width, width * 0.62), P(cap, "small")])
    rows = [cells[i:i + 2] for i in range(0, len(cells), 2)]
    for r in rows:
        if len(r) < 2:
            r.append("")
    if rows:
        t = Table(rows, colWidths=[85 * mm, 85 * mm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        d.add(t)


# --------------------------------------------------------------------------
# Part B3 — Rig Move Guide
# --------------------------------------------------------------------------

def build_moves(path):
    mv = moves()
    booms = sorted({to for _n, _t, _f, to in mv if "boom" in to})
    d = PartDoc(path, "B3", "Rig Move Guide",
                "The best order to move the installed rig into the show positions: what stays, what moves, the kit, "
                "the order of work, safety, and the test and focus afterwards.")
    d.add(title_block("PART B3 · %s · %s" % (REV, DATE), "Rig Move Guide",
                      "From the rig as installed (venue photos) to the show rig in B2 — in one ladder pass"))
    d.add(stats([(str(len(mv)), "fixtures to move"), (str(len(booms)), "floor booms to build"),
                 ("15", "fixed fixtures: 12 C42 + 3 PixBars"), ("0", "address or patch changes")]))
    d.add(box("rule", "THREE RULES",
              ["**Nothing on the FOH bar or the pelmet front moves.** The 12 Lightsky C42s and the 3 PixBars in front of "
               "the main curtain are fixed.",
               "**Move by fixture number, not by position.** Each number carries its job in the show file. If the rig ID "
               "test shows the four COBs on LX1 are not #29–32, move #29–32 to the booms wherever they hang, and put any "
               "LX1 COB with another number where the plan (B2) puts that number.",
               "**Never change an address or a mode.** A fixture keeps its DMX address wherever it hangs; the labels, "
               "link map and rig ID test all go by number."]))

    d.add(H1("1 What moves"))
    rows = []
    for i, (n, t, here, there) in enumerate(mv, 1):
        to, spot, how = WHERE.get(n, (there, "", ""))
        rows.append(["M%d" % i, "**#%d**" % n, TYPE.get(t, t), here, "**%s** — %s" % (to, spot), how,
                     FOCUS[n][3], "☐"])
    d.add(table(["", "#", "Type", "From", "To", "Hang with / aim", "Job after the move", "✓"], rows,
                [8 * mm, 9 * mm, 20 * mm, 12 * mm, 38 * mm, 34 * mm, 41 * mm, 8 * mm]))
    d.add(box("verify", "CONFIRM FIRST", "The four LX1 COB PARs are assumed to be #29–32 (the photos show four COBs on LX1 "
              "and the patch has four boom COBs). Run the rig ID test (docs/BASE_SHOW_2026_Rig_ID_Test.pdf, T23–T32) "
              "before anything comes down and write the real numbers on this sheet."))
    d.add(H2("What stays"))
    d.add(table(["Where", "Fixtures", "Note"], [list(r) for r in STAYS], [30 * mm, 44 * mm, 96 * mm], bold_first=True))

    d.add(H1("2 Kit"))
    d.add(checklist([
        "2 floor booms (about 3 m pole) with weighted bases — confirm with the venue (R-26)",
        "6 boom arms / half-couplers (3 per boom)",
        "8 safety bonds (one per moved fixture) + spares",
        "The 8 hook clamps come off LX1 with the fixtures: 2 go back up on LX2 (#19, #20)",
        "Spanners for the clamps, torch, gloves, tie line or bucket for lowering",
        "Ladder or tower with a second person footing it",
        "DMX cables: LX2 → SR boom, SR → SL boom (run along the back wall), SL boom → hazer; one per boom fixture",
        "DMX female–female barrels to bridge the gaps left on LX1; one terminator for the end of the line",
        "Power: one 10 A feed to each boom (Part C §5), IEC/powerCON leads to each boom fixture",
        "Cable mats or ramps for the wing crossings, black gaffer, white tape for the boom bases",
        "Printed base labels (docs/BASE_SHOW_2026_Mantra_Labels.pdf) and this sheet on a clipboard",
    ], cols=1))

    d.add(H1("3 Order of work — the best way"))
    d.add(P("Floor work first, then **one** height pass along LX1 and LX2, then cable, test and focus. Every fixture that "
            "comes down from LX1 goes straight to its new place, so nothing sits on the stage floor and the ladder is "
            "set up once per position."))
    d.add(H2("Stage 0 · Before (the day before, or first thing)"))
    d.add(steps([
        "Export the desk to USB (Home › Tools › Export Show) — the restore point.",
        "Run the rig ID test on the installed rig: I1–I4 type sweeps, then T1–T40. Tick where each fixture really hangs; "
        "write the numbers of the four LX1 COBs and the three pelmet PixBars on this sheet.",
        "Stick the base labels on every fixture that will move (number on the body, facing the ladder).",
        "Agree the boom positions in each wing: clear of the wing doors, props tables, quick-change space and water "
        "stations, and out of the proposed wet zone (B2).",
    ]))
    d.add(H2("Stage 1 · Build the booms (floor level, no height)"))
    d.add(steps([
        "Stand each boom in its agreed spot; weight or screw down the base; mark the base with white tape.",
        "Fit the three arms: top ~2.8 m (Zoom), mid ~1.2 m (COB), shin ~0.4 m (COB).",
        "Run the 10 A power feed to each boom and the DMX to the SR boom, then SR → SL along the back wall. Mat or ramp "
        "every crossing; keep exits and the wet zone clear.",
    ]))
    d.add(H2("Stage 2 · LX1 — one pass, stage right to stage left"))
    d.add(steps([
        "Power off LX1 (or at least unplug each fixture's power before its data). LED fixtures cool quickly but the heat "
        "sinks stay hot — gloves.",
        "At each ladder position take down only the fixtures on the move list, in the order you reach them: Zooms "
        "#19–22 and the four COBs.",
        "For each one: check its label, unplug power, unplug DMX in and out, and **join the in and out cables with a barrel** "
        "so the fixtures further along LX1 still get data. Unclip the safety bond, loosen the clamp, lower it on a line "
        "or hand it down.",
        "Hand it straight to its new position: the booms take #21, #22 and the four COBs; #19 and #20 go to LX2 with "
        "their clamps.",
        "Leave Zooms #13–18 and the projector alone for now.",
    ]))
    d.add(H2("Stage 3 · LX2 — hang #19 and #20"))
    d.add(steps([
        "Hang #19 just stage-right of centre and #20 just stage-left of centre, between the COB PARs (B2 plan order "
        "23, 26, 19, 24, 27, 20, 25, 28). Clamp, bond, then cable into the LX2 DMX chain and power.",
        "Do not move the LX2 COBs, the three LX2 PixBars or COB #39 on its wall bracket.",
    ]))
    d.add(H2("Stage 4 · Dress the booms"))
    d.add(steps([
        "SR boom: #21 Zoom top, #29 COB mid, #30 COB shin. SL boom: #22 Zoom top, #31 COB mid, #32 COB shin.",
        "Tighten each arm, fit the safety bond, point each unit roughly across the stage.",
        "DMX: in to the top fixture, down the boom, out to the next boom; SL boom out to the hazer #40; terminate the "
        "hazer (last on universe 1). Power each fixture from the boom feed.",
    ]))
    d.add(H2("Stage 5 · Tidy LX1"))
    d.add(steps([
        "Slide Zooms #13–18 along LX1 so they are evenly spread across the stage (B2), keeping the projector clear. "
        "Re-bond each one; tidy the DMX and power runs, removing barrels where a cable now reaches.",
        "Power LX1 back up.",
    ]))
    d.add(H2("Stage 6 · Test"))
    d.add(steps([
        "Run the rig ID test again: I1–I4, then T1–T40. Every fixture lit alone, in its show position, right type.",
        "Anything dark: check power, then the DMX chain from the last working fixture (fault table in the rig ID test).",
    ]))
    d.add(H2("Stage 7 · Focus"))
    d.add(steps([
        "Dark stage, a walker, and BG-02 / BG-18 on the projector for washout checks.",
        "FOH C42s (fixed — focus only): face pairs #1+#4, #5+#8, #9+#12, then the specials on their marks (Part B §7).",
        "Pelmet PixBars (fixed): tilt onto the tabs and apron, not into the front rows.",
        "LX1 wash #13–18, LX2 backlight #23–28, V3/V4 #19–20 on their marks, then the booms at head, knee and shin height.",
        "Save the desk (T S) and export to USB. Tick the Part B fixture schedule.",
    ]))
    d.add(box("rec", "ALLOW", "About half a day with two people: booms and power 45 min · LX1/LX2 moves 1–1.5 h · cabling "
              "45 min · test 20 min · focus 1–2 h. An estimate — adjust at the site walk."))

    d.add(H1("4 Safety"))
    d.add(bullets([
        "Two people for all work at height; the ladder or tower footed; nobody under the work; tools on a lanyard.",
        "Every fixture has a safety bond before it is let go — on LX2 and on the booms as well.",
        "Boom bases weighted or fixed and taped white; nothing hung above head height on a boom without a bond.",
        "Cables matted across wing routes; exits, fire doors and the wet zone kept clear (R-23, R-26).",
        "Hazer off during the move; detector isolation only under the agreed procedure (R-13).",
        "Bar loads: LX2 gains two Zooms, LX1 loses six fixtures — confirm LX2 with the venue (R-24).",
    ]))

    d.add(H1("5 Rig photos — as installed"))
    photo_grid(d)
    d.add(notes_area("Move notes (real COB/PixBar numbers, boom positions, problems)", 8))
    return d.build()


# --------------------------------------------------------------------------
# Lighting Changes — everything changed in the lighting, in one document
# --------------------------------------------------------------------------

def _cue_swatches(nums):
    cells = []
    for n in nums:
        c = S_.CUE.get(n)
        if not c:
            continue
        for x in c["lx"]:
            name, summ, _fx = S_.position_summary(x["p"], x["m"], x["c"])
            cells.append([name, swatch_strip(summ)])
    return cells


def build_changes(path):
    mv = moves()
    d = PartDoc(path, "", "Lighting Changes", divider=False)
    d.add(title_block("%s · %s" % (REV, DATE), "Lighting Changes",
                      "Every change to the lighting since the R13.1 package: the show file, the fixed FOH bar, the rig "
                      "and the paperwork"))
    d.add(stats([("5", "programming fixes"), ("12", "C42 jobs set by position"), (str(len(mv)), "fixtures to move"),
                 ("15", "fixtures fixed in place")]))

    d.add(H1("1 Show programming fixes (Mantra show file)"))
    d.add(P("Made with tools/apply_lx_sound_edits.py. Each change is also made at the cue's P8 backup position."))
    d.add(table(["Change", "Cues", "Before", "After"], [
        ["**Flash hits are white**", "Q21, Q23, Q25, Q35, Q57b + look M09",
         "Full white plus saturated colour — red/gold backlight, green sides, pink/teal PixBars: a tinted hit",
         "White on every colour fixture (faces stay cool white)"],
        ["**One storm palette**", "Q20 – Q25b",
         "Backlight changed colour every cue (gold, pink, green, red, teal…); each flash returned to a different colour",
         "M08 STORM colours throughout, levels unchanged; every flash returns to the state it left"],
        ["**Low blue storm tail**", "Q26", "Hot-pink backlight at 100 %, gold sides", "Deep-blue backlight 45 %, sides 30 %"],
        ["**House backlight**", "Q1, Q2, Q3, Q38, Q65", "Orange → red → pink in front of the audience",
         "The M02 HOUSE blue throughout"],
        ["**Shell is the brightest**", "Q36, Q52 – Q56", "Backlight 88–90 % against the 85 % shell special",
         "Side 16 % and back 18 % (the M12 VOICE SHELL levels)"]],
        [34 * mm, 30 * mm, 56 * mm, 50 * mm]))
    d.add(H2("As programmed now"))
    d.add(swatch_legend())
    d.add(P("The white flash hits show as white cells with a thin outline.", "muted"))
    d.add(table(["Cue on the desk", "Layers"], _cue_swatches(["1", "20", "21", "22", "25", "26", "35", "36", "52", "57b"]),
                [60 * mm, 110 * mm]))

    d.add(H1("2 The FOH C42s are fixed — jobs by position"))
    d.add(P("The 12 Lightsky C42s cannot be moved. They hang in number order, **#1 at the stage-right end**. The old jobs "
            "put every face light on the house-left half, so each job moved to the unit that suits it, and the show "
            "programming moved with it (tools/apply_fixed_foh_jobs.py; the venue base is untouched)."))
    old_of = {1: 1, 2: 8, 3: 11, 4: 2, 5: 3, 6: 7, 7: 12, 8: 4, 9: 5, 10: 10, 11: 9, 12: 6}
    d.add(table(["Desk #", "FOH position", "Job now", "Was on desk #"],
                [["**#%d**" % n, "%d from the SR end" % n, FOCUS[n][3], ("#%d" % old_of[n]) if old_of[n] != n else "same"]
                 for n in range(1, 13)], [18 * mm, 32 * mm, 88 * mm, 32 * mm]))

    d.add(H1("3 The rig — as installed and for the show"))
    d.add(table(["Position", "Installed now (venue photos)", "Plan"], [list(r) for r in part_b.INSTALLED],
                [36 * mm, 58 * mm, 76 * mm], bold_first=True))
    d.add(P("**Fixed — never move:** C42 #1–12 on the FOH bar and the 3 PixBars on the pelmet front. **Moves:** "
            + ", ".join("#%d %s → %s" % (n, here, to) for n, _t, here, to in mv)
            + ". The order of work is in Part B3, Rig Move Guide."))

    d.add(H1("4 Files and paperwork"))
    d.add(table(["File", "What changed"], [
        [S_.MTR_NAME, "Section 1 fixes; C42 programming moved with the new jobs (show memories 10–70 only)"],
        ["BASE_SHOW_2026.mtr / .qlab5", "Unchanged — still match the show file's patch, P1 looks and memories 100–109"],
        ["B2 Stage Lighting Layout Plan", "FOH bar in fixed order with job tags; pelmet PixBars fixed; projector at LX1; "
         "as-installed → plan table"],
        ["B3 Rig Move Guide", "New: the moves, kit, order of work, safety, test and focus"],
        ["Part B, A, C, D, K", "Fixed FOH jobs, installed rig, specials and focus notes"],
        ["Base labels, link map, rig ID test", "Positions as installed; C42s by FOH position 1–12"],
        ["Mantra labels, cue sheets", "Rebuilt from the new show file and fixture names"]],
        [58 * mm, 112 * mm]))

    d.add(H1("5 Still to check"))
    d.add(checklist([
        "Rig ID test: the real numbers of the four LX1 COBs, the three pelmet PixBars and the wall COB",
        "C42 order #1 (SR end) to #12 confirmed on the bar",
        "Focus every C42 job from its fixed position; tape the V2 Flanders mark where #7 lands cleanly",
        "Pelmet PixBars: no glare into the front rows",
        "Cue-to-cue: white flashes, storm colours, the shell levels and the house backlight from the house",
    ]))
    d.build()
    return path
