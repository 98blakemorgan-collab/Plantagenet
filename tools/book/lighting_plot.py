"""Stage lighting layout plan (A3 landscape): plan view of the rig, fixture schedule, elevations and marks.

Drawn from the fixture and focus data in Part B. Positions along each bar are proposals and the drawing is not to scale:
confirm dimensions and positions at the site walk.
"""
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from core import NAVY, TEAL, CORAL, REV, DATE, colors
import part_b

W, H = landscape(A3)
INK = colors.black
MUTED = colors.HexColor("#555555")
GRID = colors.HexColor("#dfe5ec")
FLOOR = colors.HexColor("#f4f6f9")
WET = colors.HexColor("#d9ecfb")
TYPE = {"C42": (NAVY, "Lightsky 8800-C42 LED profile"), "ZM": (TEAL, "Tour Pro Zoom RGBW wash"),
        "COB": (CORAL, "TourCOB RGBW PAR"), "PIX": (colors.HexColor("#7a4bb0"), "PixBar linear bar"),
        "HAZE": (colors.HexColor("#6f7f8f"), "Hazer"), "PIN": (colors.HexColor("#9aa5b1"), "Pinspot (optional)")}
FOCUS = {n: (t, pos, addr, role) for n, t, pos, addr, role in part_b.FOCUS}
# Short job tag under each fixed FOH C42
JOB = {1: "F-DSR", 2: "SP2", 3: "V1", 4: "F-DSR", 5: "F-DSC", 6: "SP1", 7: "V2", 8: "F-DSC", 9: "F-DSL",
       10: "SP4", 11: "SP3", 12: "F-DSL"}

# plan geometry (paper mm; audience at the bottom, upstage at the top; stage right = audience left = page left)
SX0, SX1 = 55, 255          # stage floor (wing to wing)
PX0, PX1 = 72, 238          # proscenium opening
Y_FOH, Y_EDGE, Y_PROS, Y_TABS = 46, 70, 84, 88
Y_LX1, Y_LX2, Y_PIX = 100, 190, 198
Y_SCREEN, Y_BACK = 236, 240
RED = colors.HexColor("#8e1b2c")
CX = (SX0 + SX1) / 2


def P(x, y):
    return x * mm, y * mm


def text(c, x, y, s, size=6, font="Helvetica", color=INK, anchor="c"):
    if color not in (MUTED, colors.white) and color != colors.HexColor("#c8c8c8"):
        color = INK  # all text in black; colour stays on symbols and lines
    c.setFont(font, size)
    c.setFillColor(color)
    f = {"c": c.drawCentredString, "l": c.drawString, "r": c.drawRightString}[anchor]
    f(x * mm, y * mm, s)


def symbol(c, t, x, y, scale=1.0):
    col = TYPE[t][0]
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    if t == "C42":
        c.setFillColor(col)
        c.rect((x - 2.2 * scale) * mm, (y - 3.4 * scale) * mm, 4.4 * scale * mm, 5.2 * scale * mm, fill=1, stroke=0)
        c.rect((x - 1.4 * scale) * mm, (y + 1.8 * scale) * mm, 2.8 * scale * mm, 1.6 * scale * mm, fill=1, stroke=0)
    elif t == "ZM":
        c.setFillColor(colors.white)
        c.circle(x * mm, y * mm, 3.1 * scale * mm, fill=1, stroke=1)
        c.setFillColor(col)
        c.circle(x * mm, y * mm, 1.7 * scale * mm, fill=1, stroke=0)
    elif t == "COB":
        c.setFillColor(col)
        c.circle(x * mm, y * mm, 2.7 * scale * mm, fill=1, stroke=0)
    elif t == "PIX":
        c.setFillColor(col)
        c.roundRect((x - 7 * scale) * mm, (y - 1.2 * scale) * mm, 14 * scale * mm, 2.4 * scale * mm, 0.6 * mm, fill=1, stroke=0)
    elif t == "HAZE":
        c.setFillColor(col)
        c.rect((x - 3.5 * scale) * mm, (y - 2.5 * scale) * mm, 7 * scale * mm, 5 * scale * mm, fill=1, stroke=0)
        text(c, x, y - 1.1 * scale, "HZ", 4.5 * scale, "Helvetica-Bold", colors.white)
    elif t == "PIN":
        c.setFillColor(colors.white)
        c.setDash(1, 1)
        c.circle(x * mm, y * mm, 2.2 * scale * mm, fill=1, stroke=1)
        c.setDash()


def unit(c, n, x, y, label_above=True):
    t, pos, addr, role = FOCUS[n]
    symbol(c, t, x, y)
    dy = 4.4 if label_above else -6.2
    text(c, x, y + dy, "#%d" % n, 6, "Helvetica-Bold")
    text(c, x, y + dy + (-2.4 if label_above else -2.4), "", 4)
    text(c, x, y + (-6.4 if label_above else 4.6), addr, 4.3, color=MUTED)


def bar(c, y, x0, x1, name, sub):
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.line(*P(x0, y), *P(x1, y))
    for xe in (x0, x1):
        c.line(*P(xe, y - 1.2), *P(xe, y + 1.2))
    text(c, x0 - 2, y + 0.6, name, 7, "Helvetica-Bold", anchor="r")
    text(c, x0 - 2, y - 2.4, sub, 4.8, color=MUTED, anchor="r")


def spread(ns, x0, x1):
    step = (x1 - x0) / (len(ns) - 1)
    return [(n, x0 + i * step) for i, n in enumerate(ns)]


def mark(c, x, y, label, sub, col=CORAL):
    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.line(*P(x - 2, y - 2), *P(x + 2, y + 2))
    c.line(*P(x - 2, y + 2), *P(x + 2, y - 2))
    text(c, x, y + 3, label, 5.6, "Helvetica-Bold", col)
    text(c, x, y - 5, sub, 4.4, color=MUTED)


def zone(c, x0, y0, x1, y1, label):
    c.setStrokeColor(colors.HexColor("#b9c4d0"))
    c.setLineWidth(0.4)
    c.setDash(2, 2)
    c.rect(x0 * mm, y0 * mm, (x1 - x0) * mm, (y1 - y0) * mm, fill=0, stroke=1)
    c.setDash()
    text(c, x0 + 1.5, y1 - 3.5, label, 4.6, color=colors.HexColor("#8795a6"), anchor="l")


def plan(c):
    # house, floor and wings
    c.setFillColor(FLOOR)
    c.rect(SX0 * mm, Y_PROS * mm, (SX1 - SX0) * mm, (Y_BACK - Y_PROS) * mm, fill=1, stroke=0)
    c.rect(PX0 * mm, Y_EDGE * mm, (PX1 - PX0) * mm, (Y_PROS - Y_EDGE) * mm, fill=1, stroke=0)   # apron
    c.setStrokeColor(GRID)
    c.setLineWidth(0.25)
    for gx in range(SX0 + 10, SX1, 10):
        c.line(*P(gx, Y_PROS), *P(gx, Y_BACK))
    for gy in range(Y_PROS + 10, Y_BACK, 10):
        c.line(*P(SX0, gy), *P(SX1, gy))
    # proscenium wall with doors, apron edge
    c.setFillColor(INK)
    for x0, x1 in ((SX0 - 22, PX0), (PX1, SX1 + 22)):
        c.rect(x0 * mm, (Y_PROS - 1.5) * mm, (x1 - x0) * mm, 3 * mm, fill=1, stroke=0)
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    c.line(*P(PX0, Y_EDGE), *P(PX1, Y_EDGE))
    c.line(*P(PX0, Y_EDGE), *P(PX0, Y_PROS))
    c.line(*P(PX1, Y_EDGE), *P(PX1, Y_PROS))
    c.setLineWidth(0.6)
    c.line(*P(SX0, Y_PROS), *P(SX0, Y_BACK))
    c.line(*P(SX1, Y_PROS), *P(SX1, Y_BACK))
    c.setLineWidth(1.4)
    c.line(*P(SX0, Y_BACK), *P(SX1, Y_BACK))
    text(c, CX, Y_EDGE - 4, "APRON / STAGE EDGE", 5.5, "Helvetica-Bold", MUTED)
    text(c, PX0 + 3, Y_PROS - 5.5, "apron", 4.6, color=MUTED, anchor="l")
    for dx, lab in ((SX0 - 10, "prosc. door"), (SX1 + 10, "prosc. door")):
        c.setStrokeColor(colors.white)
        c.setLineWidth(1.6)
        c.line(*P(dx - 4, Y_PROS), *P(dx + 4, Y_PROS))
        text(c, dx, Y_PROS - 5, lab, 4.4, color=MUTED)
    # treads at the front corners (audience right is the larger flight)
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    for k in range(3):
        c.rect((PX1 - 22) * mm, (Y_EDGE - 4 - k * 3) * mm, 18 * mm, 3 * mm, fill=0, stroke=1)
    text(c, PX1 - 13, Y_EDGE - 15, "treads (aud. right)", 4.4, color=MUTED)
    for k in range(2):
        c.rect((PX0 + 3) * mm, (Y_EDGE - 4 - k * 3) * mm, 10 * mm, 3 * mm, fill=0, stroke=1)
    text(c, PX0 + 8, Y_EDGE - 12, "step", 4.4, color=MUTED)
    # house speakers on the walls either side
    for x in (SX0 - 18, SX1 + 18):
        c.setFillColor(INK)
        c.rect((x - 3) * mm, (Y_EDGE - 6) * mm, 6 * mm, 5 * mm, fill=1, stroke=0)
        text(c, x, Y_EDGE - 10, "wall speaker", 4.4, color=MUTED)
    # red pelmet + house tabs, black legs
    c.setStrokeColor(RED)
    c.setLineWidth(2.2)
    c.line(*P(PX0, Y_PROS + 1.8), *P(PX1, Y_PROS + 1.8))
    c.setLineWidth(1.2)
    c.setDash(3, 1.2)
    c.line(*P(PX0 + 1, Y_TABS), *P(PX1 - 1, Y_TABS))
    c.setDash()
    text(c, PX0 + 2, Y_TABS + 1.4, "3 PixBars on the pelmet front — FIXED, stay: tabs / apron wash", 4.4,
         color=MUTED, anchor="l")
    text(c, PX1 - 2, Y_TABS + 1.4, "RED PELMET + HOUSE TABS (Scenes Two, Four, Nine play in front)", 4.6, color=RED, anchor="r")
    c.setStrokeColor(INK)
    c.setLineWidth(2.4)
    for y in (150, 174, 226):
        c.line(*P(PX0 - 2, y), *P(PX0 + 10, y))
        c.line(*P(PX1 - 10, y), *P(PX1 + 2, y))
    text(c, PX0 + 12, 226.6, "black legs", 4.4, color=MUTED, anchor="l")
    text(c, SX0 - 12, (Y_PROS + Y_BACK) / 2 + 42, "SR WING", 6.5, "Helvetica-Bold", MUTED)
    text(c, SX1 + 12, (Y_PROS + Y_BACK) / 2 + 42, "SL WING", 6.5, "Helvetica-Bold", MUTED)
    text(c, SX0 - 12, (Y_PROS + Y_BACK) / 2 + 38, "(audience left)", 4.8, color=MUTED)
    text(c, SX1 + 12, (Y_PROS + Y_BACK) / 2 + 38, "(audience right)", 4.8, color=MUTED)
    text(c, SX0 - 12, 230, "wing door", 4.4, color=MUTED)
    text(c, SX1 + 12, 230, "wing door", 4.4, color=MUTED)

    # screen and projector
    c.setStrokeColor(colors.HexColor("#b9c2cc"))
    c.setLineWidth(3)
    c.line(*P(PX0 + 4, Y_SCREEN), *P(PX1 - 4, Y_SCREEN))
    text(c, CX, Y_BACK + 2.2, "PAINTED BACK WALL = PROJECTION SURFACE  ·  backdrops BG-01 – BG-26", 5.5, "Helvetica-Bold")
    px, py = CX, Y_LX1 + 6       # seen at LX1 centre in the venue photos, lens facing upstage
    c.setFillColor(INK)
    c.rect((px - 6) * mm, (py - 3) * mm, 12 * mm, 6 * mm, fill=1, stroke=0)
    text(c, px, py - 1, "PROJ", 5, "Helvetica-Bold", colors.white)
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.5)
    c.setDash(1.5, 1.5)
    c.line(*P(px - 5, py + 3), *P(PX0 + 6, Y_SCREEN - 1))
    c.line(*P(px + 5, py + 3), *P(PX1 - 6, Y_SCREEN - 1))
    c.setDash()
    text(c, px + 7, py + 3.4, "projector at LX1 centre (photos), bonded (R-22); throws upstage onto the wall", 4.4,
         color=MUTED, anchor="l")

    # zones and wet zone
    xs = [PX0 + 2, PX0 + 56, PX1 - 56, PX1 - 2]
    for (y0, y1, row) in ((Y_TABS + 20, 136, "DS"), (140, 180, "CS")):
        for i, side in enumerate(("R", "C", "L")):
            zone(c, xs[i] + 1, y0, xs[i + 1] - 1, y1, row + side)
    c.setFillColor(WET)
    c.setStrokeColor(colors.HexColor("#6aa9df"))
    c.setDash(1, 1.5)
    c.roundRect((PX0 + 6) * mm, 144 * mm, 42 * mm, 26 * mm, 3 * mm, fill=1, stroke=1)
    c.setDash()
    text(c, PX0 + 27, 164, "PROPOSED WET ZONE", 4.8, "Helvetica-Bold", colors.HexColor("#3a7fbf"))
    text(c, PX0 + 27, 160, "water pistols Q19.2 / Q58 (R-23)", 4.2, color=colors.HexColor("#3a7fbf"))
    text(c, PX0 + 27, 156.5, "confirm at the site walk", 4.2, color=colors.HexColor("#3a7fbf"))

    # performer marks
    mark(c, CX, 118, "SP1 Ariel", "#6 · DSC")
    mark(c, PX0 + 28, 118, "SP2 Spirit", "#2 · DS aud-left")
    mark(c, PX1 - 28, 172, "SP3 Octavia", "#11 · US aud-right")
    mark(c, CX, 164, "SP4 Shell", "#10 · plinth")
    for (x, y, lab, sub) in ((CX - 58, 136, "V1 Dame", "#3"), (CX - 30, 136, "V2 Flanders", "#7"),
                             (CX + 30, 150, "V3 Theodore", "#19"), (CX + 58, 150, "V4 Marina", "#20")):
        mark(c, x, y, lab, sub, colors.HexColor("#b0417a"))

    # FOH truss (over the house)
    bar(c, Y_FOH, SX0 + 5, SX1 - 5, "FOH BAR", "house ceiling · U2 · FIXED")
    for n, x in spread([41] + list(range(1, 13)) + [42], SX0 + 9, SX1 - 9):
        unit(c, n, x, Y_FOH)
        if n in JOB:
            text(c, x, Y_FOH - 9.2, JOB[n], 4.4, "Helvetica-Bold")
    text(c, CX, Y_FOH - 13.4, "THE 12 LIGHTSKY C42s CANNOT BE MOVED — hung in number order, #1 at the stage-right end. "
         "Jobs go by position: a cross pair per face zone, specials on the units nearest their marks.", 5.2,
         "Helvetica-Bold", RED)
    # LX1
    bar(c, Y_LX1, PX0, PX1, "LX1", "beam behind the pelmet")
    text(c, PX0 - 2, Y_LX1 - 5, "now: 10 Zooms, 4 COBs, proj. (moves: B3)", 4.4, color=MUTED, anchor="r")
    for n, x in spread([13, 16, 14, 17, 15, 18], PX0 + 5, PX1 - 5):
        unit(c, n, x, Y_LX1)
    # LX2 + PixBar row
    bar(c, Y_LX2, PX0, PX1, "LX2", "upstage beam")
    for n, x in spread([23, 26, 19, 24, 27, 20, 25, 28], PX0 + 5, PX1 - 5):
        unit(c, n, x, Y_LX2, label_above=False)
    # COB #39 stays on its wall bracket by LX2 (venue photo 9)
    unit(c, 39, PX1 + 8, Y_LX2, label_above=False)
    text(c, PX1 + 8, Y_LX2 - 9.6, "wall bracket", 4.2, color=MUTED)
    text(c, PX1 + 8, Y_LX2 - 12, "stays · side TBC", 4.2, color=MUTED)
    for x in (PX0 + 40, CX, PX1 - 40):
        symbol(c, "PIX", x, Y_PIX)
        text(c, x, Y_PIX + 2.6, "PixBar · # from rig ID test", 4.4, "Helvetica-Bold")
    text(c, CX, Y_PIX + 7.2, "3 PIXBARS on LX2, tilted downstage — never onto the back wall (R-25)", 4.6, color=MUTED)
    # the other three are fixed on the pelmet front, in front of the main curtain
    for x in (PX0 + 30, CX, PX1 - 30):
        symbol(c, "PIX", x, Y_PROS - 3.2)
        text(c, x, Y_PROS - 7.4, "PixBar · FIXED", 4.4, "Helvetica-Bold")

    # booms
    for side, x, ns in (("SR BOOM", SX0 - 12, (21, 29, 30)), ("SL BOOM", SX1 + 12, (22, 31, 32))):
        y = 140
        c.setFillColor(INK)
        c.circle(x * mm, y * mm, 1.6 * mm, fill=1, stroke=0)
        text(c, x, y + 26, side, 6.5, "Helvetica-Bold")
        text(c, x, y + 23, "weighted base (R-26)", 4.4, color=MUTED)
        for i, (n, h) in enumerate(zip(ns, ("top ~2.8 m", "mid ~1.2 m", "shin ~0.4 m"))):
            yy = y + 16 - i * 10 - 10
            ux = x
            symbol(c, FOCUS[n][0], ux, yy + 8, 0.9)
            text(c, ux + (6 if side.startswith("SR") else -6), yy + 8.6, "#%d" % n, 5.6, "Helvetica-Bold",
                 anchor="l" if side.startswith("SR") else "r")
            text(c, ux + (6 if side.startswith("SR") else -6), yy + 6.2, "%s · %s" % (h, FOCUS[n][2]), 4.2, color=MUTED,
                 anchor="l" if side.startswith("SR") else "r")

    # hazer
    symbol(c, "HAZE", PX0 + 14, 214)
    text(c, PX0 + 14, 218.5, "#40 HAZER · U1:487", 5, "Helvetica-Bold")
    text(c, PX0 + 14, 208, "US floor · P5 M4 · 50 % / fan 50 %", 4.3, color=MUTED)

    # house
    text(c, CX, 26.5, "AUDIENCE  (flat floor, loose chairs)", 11, "Helvetica-Bold", colors.HexColor("#c8c8c8"))
    text(c, CX, 21.5, "FOH bar hangs from the house ceiling · second ceiling rail further back (spare position, check load) · "
         "control at the back (QLab Mac, Mantra, StudioLive)", 5, color=MUTED)
    # north arrow style orientation
    text(c, 18, 250, "UPSTAGE ↑", 6, "Glyph", MUTED, anchor="l")
    text(c, 18, 22, "DOWNSTAGE / HOUSE ↓", 6, "Glyph", MUTED, anchor="l")


def panel(c):
    x0, x1 = 296, 410
    # title block
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.rect(x0 * mm, 250 * mm, (x1 - x0) * mm, 37 * mm, fill=0, stroke=1)
    text(c, x0 + 5, 279, "THE LITTLE MERMAID · PLANTAGENET HALL", 7, "Helvetica-Bold", INK, "l")
    text(c, x0 + 5, 269, "Stage Lighting Layout Plan", 15, "Helvetica-Bold", INK, "l")
    text(c, x0 + 5, 261, "Plan view · rig, specials, marks and fixture schedule", 6.5, color=MUTED, anchor="l")
    text(c, x0 + 5, 254, "%s · %s · NOT TO SCALE — indicative, verify on site" % (REV, DATE), 5.6, color=MUTED, anchor="l")

    # legend
    y = 243
    text(c, x0, y, "LEGEND", 7, "Helvetica-Bold", anchor="l")
    counts = {}
    for n, (t, *_r) in FOCUS.items():
        counts[t] = counts.get(t, 0) + 1
    y -= 6
    for t in ("C42", "ZM", "COB", "PIX", "HAZE", "PIN"):
        symbol(c, t, x0 + 6, y + 1, 0.9)
        text(c, x0 + 15, y, "%s  ×%d" % (TYPE[t][1], counts[t]), 5.8, anchor="l")
        y -= 6.2
    mark(c, x0 + 6, y + 2, "", "")
    text(c, x0 + 15, y, "Performer mark (special / voice)", 5.8, anchor="l")
    y -= 5
    text(c, x0, y, "#n = Mantra desk number = fixture ID · grey = universe:address", 5, color=MUTED, anchor="l")

    # schedule
    y -= 7
    text(c, x0, y, "FIXTURE SCHEDULE", 7, "Helvetica-Bold", anchor="l")
    y -= 5
    cols = [(x0, "#"), (x0 + 7, "Type"), (x0 + 17, "Position"), (x0 + 33, "DMX"), (x0 + 47, "Focus / job")]
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line((x0 - 1) * mm, (y + 3) * mm, x1 * mm, (y + 3) * mm)
    c.line((x0 - 1) * mm, (y - 1.4) * mm, x1 * mm, (y - 1.4) * mm)
    for cx, h in cols:
        text(c, cx, y, h, 5, "Helvetica-Bold", INK, "l")
    y -= 4.3
    for i, n in enumerate(sorted(FOCUS)):
        t, pos, addr, role = FOCUS[n]
        if i % 2:
            c.setFillColor(colors.HexColor("#f5f7fa"))
            c.rect((x0 - 1) * mm, (y - 1.2) * mm, (x1 - x0 + 1) * mm, 3.9 * mm, fill=1, stroke=0)
        role = role.replace(" (confirm it exists, R13.1 fix list)", " (confirm fitted)")
        if len(role) > 52:
            role = role[:51] + "…"
        vals = [str(n), t, pos, addr, role]
        for (cx, _h), v in zip(cols, vals):
            text(c, cx, y, v, 4.7, "Helvetica-Bold" if cx == x0 else "Helvetica", TYPE[t][0] if cx == x0 else INK, "l")
        y -= 3.9
    y -= 2
    text(c, x0, y, "Modes: C42 11 ch · Zoom 12 ch · COB 6 ch · PixBar 6 ch · hazer 2 ch. Keep strobe / macro / CCT at 0.", 4.6,
         color=MUTED, anchor="l")


def page2(c):
    text(c, 20, 280, "Stage Lighting Layout Plan — sections, booms and checks", 14, "Helvetica-Bold", INK, "l")
    text(c, 20, 273, "Side section and boom elevations are indicative. Record the measured trim heights and positions at the site walk.",
         6.5, color=MUTED, anchor="l")

    # side section
    gx0, gy0 = 25, 150
    text(c, gx0, 262, "SIDE SECTION (looking from SL)", 8, "Helvetica-Bold", anchor="l")
    c.setStrokeColor(INK)
    c.setLineWidth(1)
    c.line(*P(gx0, gy0), *P(gx0 + 90, gy0))            # house floor
    c.line(*P(gx0 + 90, gy0), *P(gx0 + 90, gy0 + 8))   # stage front
    c.line(*P(gx0 + 90, gy0 + 8), *P(gx0 + 240, gy0 + 8))  # stage floor
    text(c, gx0 + 45, gy0 - 5, "HOUSE", 6, "Helvetica-Bold", MUTED)
    text(c, gx0 + 165, gy0 + 3, "STAGE", 6, "Helvetica-Bold", MUTED)
    for x, h, lab, sub in ((gx0 + 60, 92, "FOH bar (ceiling)", "C42 #1–12 FIXED · faces + specials"),
                           (gx0 + 112, 84, "LX1 (behind pelmet)", "Zoom #13–18 · projector"),
                           (gx0 + 195, 88, "LX2", "COB #23–28 · Zoom #19–20 · 3 PixBars")):
        c.setLineWidth(1.4)
        c.circle(x * mm, (gy0 + h) * mm, 1.8 * mm, fill=0, stroke=1)
        c.setLineWidth(0.4)
        c.setDash(1, 1.5)
        c.line(*P(x, gy0 + h), *P(x, gy0))
        c.setDash()
        text(c, x, gy0 + h + 4, lab, 6.5, "Helvetica-Bold")
        text(c, x, gy0 + h - 5.5, sub, 4.8, color=MUTED)
        text(c, x + 2, gy0 + h / 2, "trim: ____ m", 5, color=MUTED, anchor="l")
    # beams
    c.setStrokeColor(TYPE["C42"][0])
    c.setLineWidth(0.5)
    c.line(*P(gx0 + 60, gy0 + 92), *P(gx0 + 110, gy0 + 22))
    c.setStrokeColor(TYPE["COB"][0])
    c.line(*P(gx0 + 195, gy0 + 88), *P(gx0 + 150, gy0 + 22))
    c.setStrokeColor(TYPE["ZM"][0])
    c.line(*P(gx0 + 112, gy0 + 84), *P(gx0 + 130, gy0 + 22))
    # pelmet and tabs in section
    c.setStrokeColor(RED)
    c.setLineWidth(1.6)
    c.line(*P(gx0 + 104, gy0 + 86), *P(gx0 + 104, gy0 + 72))
    c.setLineWidth(0.8)
    c.setDash(2, 1)
    c.line(*P(gx0 + 106, gy0 + 72), *P(gx0 + 106, gy0 + 8))
    c.setDash()
    text(c, gx0 + 102, gy0 + 66, "pelmet / tabs", 4.6, color=RED, anchor="r")
    text(c, gx0 + 100, gy0 + 30, "front / face", 5, color=TYPE["C42"][0])
    text(c, gx0 + 160, gy0 + 30, "back", 5, color=TYPE["COB"][0])
    text(c, gx0 + 131, gy0 + 40, "top", 5, color=TYPE["ZM"][0])
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.line(*P(gx0 + 232, gy0 + 8), *P(gx0 + 232, gy0 + 78))
    text(c, gx0 + 232, gy0 + 82, "back wall", 5.5, "Helvetica-Bold")
    c.setFillColor(INK)
    c.rect((gx0 + 122) * mm, (gy0 + 86) * mm, 8 * mm, 4 * mm, fill=1, stroke=0)
    text(c, gx0 + 132, gy0 + 87, "projector at LX1 → back wall", 5, color=MUTED, anchor="l")
    text(c, gx0 + 214, gy0 + 13, "#40 hazer", 5, color=MUTED)

    # boom elevations
    bx = 300
    text(c, bx, 262, "BOOM ELEVATIONS (from on stage)", 8, "Helvetica-Bold", anchor="l")
    for i, (name, ns) in enumerate((("SR boom", (21, 29, 30)), ("SL boom", (22, 31, 32)))):
        x = bx + 8 + i * 58
        c.setStrokeColor(INK)
        c.setLineWidth(1.6)
        c.line(*P(x, gy0 + 8), *P(x, gy0 + 100))
        c.setFillColor(INK)
        c.rect((x - 8) * mm, (gy0 + 6) * mm, 16 * mm, 3 * mm, fill=1, stroke=0)
        text(c, x, gy0 + 1, name + " · base weighted", 5.5, "Helvetica-Bold")
        for n, h, lab in zip(ns, (96, 48, 22), ("~2.8 m high side", "~1.2 m mid side", "~0.4 m shin")):
            t = FOCUS[n][0]
            symbol(c, t, x + 6, gy0 + h)
            text(c, x + 11, gy0 + h + 0.8, "#%d %s" % (n, "Zoom" if t == "ZM" else "COB"), 5.6, "Helvetica-Bold", anchor="l")
            text(c, x + 11, gy0 + h - 2.2, "%s · %s" % (lab, FOCUS[n][2]), 4.6, color=MUTED, anchor="l")

    # specials table
    ty = 128
    text(c, 20, ty, "SPECIALS AND MARKS", 8, "Helvetica-Bold", anchor="l")
    ty -= 6
    heads = [(20, "Special"), (36, "Character"), (62, "Fixture"), (112, "Mark / use")]
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(19 * mm, (ty + 3.5) * mm, 189 * mm, (ty + 3.5) * mm)
    c.line(19 * mm, (ty - 1.5) * mm, 189 * mm, (ty - 1.5) * mm)
    for x, h in heads:
        text(c, x, ty, h, 5.8, "Helvetica-Bold", INK, "l")
    ty -= 5
    for i, (sp, ch, fx, use) in enumerate(part_b.SPECIALS):
        if i % 2:
            c.setFillColor(colors.HexColor("#f5f7fa"))
            c.rect(19 * mm, (ty - 1.5) * mm, 170 * mm, 4.6 * mm, fill=1, stroke=0)
        for (x, _h), v in zip(heads, (sp, ch, fx, use)):
            text(c, x, ty, v, 5.6, "Helvetica-Bold" if x == 20 else "Helvetica", anchor="l")
        ty -= 4.6

    # data route and checks
    cx0 = 205
    text(c, cx0, 128, "DATA ROUTE", 8, "Helvetica-Bold", anchor="l")
    lines = ["U1 (desk XLR): LX1 → pelmet PixBars → LX2 → #39 → SR boom → SL boom → hazer · terminate",
             "U2 (Art-Net/sACN): desk → switch → node 2.0.0.10 → FOH bar C42 #1–12 · terminate",
             "Every fixture keeps its desk number and address wherever it hangs."]
    yy = 122
    for l in lines:
        text(c, cx0, yy, l, 5.8, anchor="l")
        yy -= 5
    text(c, cx0, yy - 3, "SITE-WALK CHECKS", 8, "Helvetica-Bold", anchor="l")
    yy -= 9
    checks = ["C42 #1–12 fixed: confirm the order (#1 SR end) and focus each job from where it hangs",
              "Rig ID test: which COB PARs and PixBars are on LX1, LX2, the pelmet (fixed) and the wall",
              "Bar loads and trims for FOH, LX1, LX2 (R-24)", "LX1 beam rated for the projector (it hangs there now); projector bonded (R-22)",
              "Boom bases weighted, clear of props tables and water stations (R-26)",
              "LX2 and PixBars tilted off the back wall; check washout with BG-02/BG-18 (R-25)",
              "Fixtures #38 PixBar and #39 TourCOB fitted and patched",
              "Wet zone agreed; towels and stage-dry checks (R-23)",
              "Hazer position vs detectors; isolation procedure agreed (R-13)",
              "Marks SP1–SP4 and V1–V4 taped after blocking"]
    for ch in checks:
        c.setStrokeColor(INK)
        c.setLineWidth(0.5)
        c.rect(cx0 * mm, (yy - 0.6) * mm, 2.8 * mm, 2.8 * mm, fill=0, stroke=1)
        text(c, cx0 + 5, yy, ch, 5.8, anchor="l")
        yy -= 5.2

    installed(c, 20, 78)

    c.setStrokeColor(GRID)
    c.rect(20 * mm, 12 * mm, 390 * mm, 22 * mm, fill=0, stroke=1)
    text(c, 23, 29, "NOTES / MEASUREMENTS", 6, "Helvetica-Bold", MUTED, "l")


def wrap(s, size, width_mm, font="Helvetica"):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if stringWidth(t, font, size) > width_mm * mm and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + [cur]


def installed(c, x0, y):
    """As-installed rig from the venue photos, and the plan for each position (part_b.INSTALLED)."""
    text(c, x0, y, "AS INSTALLED (venue photos) → PLAN", 8, "Helvetica-Bold", anchor="l")
    y -= 6
    cols = [(x0, 36, "Position"), (x0 + 37, 55, "Installed now"), (x0 + 93, 76, "Plan")]
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line((x0 - 1) * mm, (y + 3.5) * mm, (x0 + 170) * mm, (y + 3.5) * mm)
    c.line((x0 - 1) * mm, (y - 1.5) * mm, (x0 + 170) * mm, (y - 1.5) * mm)
    for x, _w, h in cols:
        text(c, x, y, h, 5.6, "Helvetica-Bold", INK, "l")
    y -= 4.8
    for i, row in enumerate(part_b.INSTALLED):
        cells = [wrap(v, 4.8, w - 1, "Helvetica-Bold" if k == 0 else "Helvetica") for k, (v, (_x, w, _h)) in
                 enumerate(zip(row, cols))]
        n = max(len(cl) for cl in cells)
        if i % 2:
            c.setFillColor(colors.HexColor("#f5f7fa"))
            c.rect((x0 - 1) * mm, (y - 1.4 - (n - 1) * 2.3) * mm, 171 * mm, (n * 2.3 + 1.6) * mm, fill=1, stroke=0)
        for k, ((x, _w, _h), cl) in enumerate(zip(cols, cells)):
            for j, line in enumerate(cl):
                col = RED if (i == 0 and k == 2) else INK
                text(c, x, y - j * 2.3, line, 4.8, "Helvetica-Bold" if k == 0 or (i == 0 and k == 2) else "Helvetica",
                     col, "l")
        y -= n * 2.3 + 1.9


def footer(c, page):
    text(c, 20, 6, "Stage Lighting Layout Plan · %s · The Little Mermaid · Plantagenet Hall" % REV, 5.5, color=MUTED, anchor="l")
    text(c, 410, 6, "sheet %d of 2" % page, 5.5, color=MUTED, anchor="r")


def build(path):
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Stage Lighting Layout Plan")
    c.setAuthor("The Little Mermaid production")
    plan(c)
    panel(c)
    footer(c, 1)
    c.showPage()
    page2(c)
    footer(c, 2)
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else "Lighting_Layout_Plan.pdf"))
