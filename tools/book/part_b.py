"""Part B — Lighting Design (R13.1 colour-forward design on the venue rig)."""
from core import *  # noqa: F401,F403
import show as S_


RIG = [("Lightsky 8800-C42", "12", "#1–12", "U2 · 11 ch · 101–232",
        "LED profile with shutters, 6 colours + CCT, 19° lens", "Face light and hard-edged specials. Best skin tones."),
       ("Tour Pro Zoom", "10", "#13–22", "U1 · 12 ch · 301–420",
        "RGBW COB zoom wash 13–45°, barn doors", "Colour top wash (LX1), voice-transfer pools, high side"),
       ("Tour Pro TourCOB PAR", "11", "#23–32, 39", "U1 · 6 ch · 421–486",
        "RGBW COB PAR, fixed beam", "Backlight and side light; the main colour energy of the show"),
       ("Tour Pro PixBar", "6", "#33–38", "U1 · 6 ch · 1–36",
        "Linear bar, whole-bar colour in this mode", "Effect row: storm, magic, jellyfish, song impacts"),
       ("Hazer", "1", "#40", "U1 · 2 ch · 487–488", "Output + fan", "Selective haze, P5 M4 (50 % / fan 50 %)")]

FAMILY = [("Underwater", "Deep blue → cyan → turquoise → purple → blue/green", "M03 · Q4–Q11, Q31"),
          ("Comedy", "Aqua → hot pink → yellow/gold → purple accents", "M04 · Q9, Q12–Q14"),
          ("Royal / palace", "Gold + royal/deep blue, magenta/gold musical lifts", "M05 · Q10, Q39–Q44"),
          ("Ship / storm", "Steel/deep blue + amber; storm through cyan/purple/ice-white impacts",
           "M06, M08, M09 · Q18–Q27"),
          ("Shore / dry land", "Amber → peach → pink → lavender → moonlight blue", "M07, M14 · Q28–Q30.5, Q59"),
          ("Magic / Spirit", "Purple → cyan → teal/green → white impact", "M10 · Q33–Q36, Q48, Q62"),
          ("Lair / Octavia", "Purple + acid green → red/magenta → cyan/purple", "M11 · Q50–Q58.5"),
          ("Jellyfish", "Hot pink + cyan + violet pulse", "M13 · Q45–Q49"),
          ("Wedding / finale", "Gold → aqua → magenta → blue → gold / multicolour", "M15, M16 · Q60–Q65")]

SONG_LANG = {"S1": "Aqua / hot pink / gold / deep blue / magenta / lime / white impacts",
             "S2": "Deep blue / purple / gold / magenta with warm-white highlights",
             "S3": "Blue / teal / violet / pink / cyan with a warmer emotional lift",
             "S4": "Steel/deep blue and amber, then teal/cyan and bright chorus accents",
             "S5": "Amber / pink / violet / cyan / gold with a larger final chorus",
             "S6": "Fastest colour changes: lime, cyan, magenta, gold, red and white impacts",
             "S7": "Hot pink / cyan / violet pulse language",
             "S8": "Purple / acid green / red / cyan for strong villain contrast",
             "S9": "Concert style: cyan / magenta / gold / blue / lime / hot pink",
             "S10": "Deep blue / amber / cyan / red / gold / bright white finale"}

SPECIALS = [("SP1", "Ariel", "#7 C42 (FOH)", "DSC mark; solo, duet, transformation, restore (57c)"),
            ("SP2", "Spirit", "#8 C42 (FOH)", "DS audience-left mark; every Spirit entrance"),
            ("SP3", "Octavia", "#9 C42 (LX1)", "US audience-right; entrances, lair, wedding interruption"),
            ("SP4", "Shell", "#10 C42 (LX1, shuttered tight)", "Plinth mark; brightest point in Scene Eight"),
            ("V1", "Dame", "#11 C42 (LX1)", "Voice-transfer mark 1 (Q53)"),
            ("V2", "Flanders", "#12 C42 (LX1)", "Voice-transfer mark 2 (Q54)"),
            ("V3", "Theodore", "#19 Zoom 13° + barn doors (LX2)", "Voice-transfer mark 3 (Q55)"),
            ("V4", "Marina", "#20 Zoom 13° + barn doors (LX2)", "Voice-transfer mark 4 (Q56)")]

FOCUS = [(1, "C42", "FOH", "U2:101", "Face zone 1 — DSR (from house left)"),
         (2, "C42", "FOH", "U2:112", "Face zone 1 — DSR (from house right)"),
         (3, "C42", "FOH", "U2:123", "Face zone 2 — DSC (from house left)"),
         (4, "C42", "FOH", "U2:134", "Face zone 2 — DSC (from house right)"),
         (5, "C42", "FOH", "U2:145", "Face zone 3 — DSL (from house left)"),
         (6, "C42", "FOH", "U2:156", "Face zone 3 — DSL (from house right)"),
         (7, "C42", "FOH", "U2:167", "SP1 Ariel — DSC mark, shuttered tight"),
         (8, "C42", "FOH", "U2:178", "SP2 Spirit — DS audience-left mark"),
         (9, "C42", "LX1", "U2:189", "SP3 Octavia — US audience-right mark"),
         (10, "C42", "LX1", "U2:200", "SP4 Shell — plinth mark, shuttered to the shell"),
         (11, "C42", "LX1", "U2:211", "V1 Dame — voice-transfer mark 1"),
         (12, "C42", "LX1", "U2:222", "V2 Flanders — voice-transfer mark 2")] + \
    [(13 + i, "ZM", "LX1", "U1:%d" % (301 + 12 * i), "Top/front colour wash — " + a)
     for i, a in enumerate(["DSR", "DSC", "DSL", "CSR", "CSC", "CSL"])] + \
    [(19, "ZM", "LX2", "U1:373", "V3 Theodore — 13°, barn doors, steep top light"),
     (20, "ZM", "LX2", "U1:385", "V4 Marina — 13°, barn doors, steep top light"),
     (21, "ZM", "SR boom", "U1:397", "High side — top of boom (~2.8 m), across to SL, head height"),
     (22, "ZM", "SL boom", "U1:409", "High side — top of boom (~2.8 m), across to SR, head height")] + \
    [(23 + i, "COB", "LX2", "U1:%d" % (421 + 6 * i), "Backlight — " + a)
     for i, a in enumerate(["DSR", "DSC", "DSL", "CSR", "CSC", "CSL"])] + \
    [(29, "COB", "SR boom", "U1:457", "Mid side — boom arm ~1.2 m, knee to hip"),
     (30, "COB", "SR boom", "U1:463", "Low side (shin) — boom arm ~0.4 m"),
     (31, "COB", "SL boom", "U1:469", "Mid side — boom arm ~1.2 m, knee to hip"),
     (32, "COB", "SL boom", "U1:475", "Low side (shin) — boom arm ~0.4 m")] + \
    [(33 + i, "PIX", "LX2", "U1:%d" % (1 + 6 * i), "Effect row, tilted downstage off the screen (R-25)")
     for i in range(6)] + \
    [(39, "COB", "LX2", "U1:481", "Extra backlight — centre (confirm it exists, R13.1 fix list)"),
     (40, "HAZE", "Floor, US", "U1:487", "Atmosphere — P5 M4 HAZE (50 %, fan 50 %)"),
     (41, "PIN", "FOH SR end", "U1:37", "Mirror ball (optional, not patched)"),
     (42, "PIN", "FOH SL end", "U1:38", "Mirror ball (optional, not patched)")]


def look_table():
    rows, strips = [], []
    for L in S_.LOOKS:
        s = L["summary"]
        rows.append(["**%s**" % L["name"], "P%d M%d" % (L["page"], L["mem"]), swatch_strip(s),
                     describe(s) + (" · specials %d%%" % s["SPC"][0] if s["SPC"][0] else "")])
    return table(["Look", "Desk", "Layers", "As programmed (level · colour)"], rows,
                 [30 * mm, 14 * mm, 57 * mm, 69 * mm])


def song_table():
    rows, tints = [], []
    for so in S_.SONGS:
        summs = [S_.position_summary(4, sec["m"], sec["c"])[1] for sec in so["sections"]]
        t = section_strip(summs, 64 * mm)
        rows.append(["**%s** %s" % (so["num"], so["title"]), "P4 M%d · %d cues" % (so["mem"], len(so["sections"])),
                     SONG_LANG[so["num"]], t])
    return table(["Song", "Desk", "Colour language", "Sections as programmed (one strip per section)"],
                 rows, [34 * mm, 20 * mm, 50 * mm, 66 * mm])


def build(path):
    d = PartDoc(path, "B", "Lighting Design",
                "The colour-forward design on the venue's installed 39-fixture rig: rig, layers, "
                "specials, the look library and song colour as programmed, fixture schedule and focus plan.")
    d.add(title_block("PART B · %s · %s" % (REV, DATE), "Lighting Design",
                      "Readable faces in neutral FOH light, with the energy coming "
                      "from changing LX1 colour, side-light contrast, LX2 backlight and animated PixBars."))
    d.add(stats([("39", "lighting fixtures + hazer, 4 types"), ("153", "programmed cue positions"),
                 ("17", "looks M01–M17 (P6–P7)"), ("10", "song memories (P4)"), ("0", "strobe values stored")]))
    d.add(box("rule", "THE DESIGN IN BRIEF",
              ["**Strong LX1 colour, side light, LX2 backlight and PixBar movement** over neutral faces, fast colour "
               "snaps on musical impacts, slower crossfades for emotional and dialogue moments, and every song has "
               "its own colour-driven memory.",
               "The show is split across pages: **P2 Act One, P3 Act Two, P4 songs, P5 FX/chases, P6–P7 look "
               "library, P8 full 153-step backup**. QLab fires every cue, including automatic flash returns and "
               "memory releases (Part D)."]))
    d.add(H1("1 The installed rig"))
    d.add(table(["Fixture", "Qty", "Mantra #", "DMX", "What it is", "Job in the show"],
                [list(r) for r in RIG], [30 * mm, 9 * mm, 17 * mm, 26 * mm, 42 * mm, 46 * mm], bold_first=True))
    d.add(P("Positions: 8 × C42 on the FOH truss (#1–8), LX1 downstage bar (C42 #9–12, "
            "Zoom #13–18), LX2 upstage bar (Zoom #19–20, COB #23–28, 39, PixBar #33–38), a floor boom in each "
            "wing (SR #21, 29, 30 · SL #22, 31, 32) and the hazer upstage on the floor (#40). The projector hangs "
            "centre stage towards the back and throws upstage (R-11)."))
    d.add(box("rule", "DESIGN RULE", "FOH #1–6 keep faces readable in every look. The flashier colour movement "
              "comes from the LX1 Zooms, side booms, LX2 backlight and PixBars. Never aim high-intensity "
              "backlight or PixBars at the projection screen (R-25)."))

    d.add(H1("2 Design layers"))
    d.add(table(["Layer", "How it is set", "What it does"], [
        ["Face (FOH C42 #1–6)", "Near-white: cool white under water, warm white on land (about 30–100 %)",
         "Every scene with dialogue stays readable"],
        ["Colour top (LX1 Zoom #13–18)", "Saturated scene colour: cyan, hot pink, gold, blue, violet",
         "Sets the scene colour; snaps on musical impacts"],
        ["Side (booms #21–22, 29–32)", "Contrasting colour to the top wash (lime, violet, magenta, teal)",
         "Body light and colour contrast for dance, off the screen"],
        ["Backlight (LX2 COB #23–28, 39)", "Highest levels in the rig (60–100 %), strong saturated colour",
         "Depth, haze beams, the storm and lair energy"],
        ["Effects (PixBar #33–38)", "Two-colour splits in storm, magic, jellyfish and every song",
         "Movement and impact without strobe"],
        ["Specials (C42 #7–12, Zoom #19–20)", "Hard pools on marks, added per cue",
         "Character entrances, shell, voice transfer"]],
        [44 * mm, 70 * mm, 56 * mm], bold_first=True))
    d.add(H2("Colour language by scene family"))
    d.add(table(["Scene family", "Colour language", "Looks · cues"], [list(r) for r in FAMILY],
                [34 * mm, 84 * mm, 52 * mm], bold_first=True))
    d.add(box("verify", "NO STROBE", "No strobe is programmed: Strobe, Control, Reset, Auto speed, Other, Default "
              "and Colour macro are 0 in every cue. Lightning and magic are single white hits (Q21, Q23, Q25, "
              "Q35, Q57b) that QLab returns automatically after 0.2–0.3 s. Never more than 3 flashes a second "
              "(R-04); the HAYWIRE chase runs at 2 steps a second."))

    d.add(H1("3 Specials"))
    d.add(table(["Special", "Character", "Fixture", "Use"], [list(r) for r in SPECIALS],
                [16 * mm, 22 * mm, 52 * mm, 80 * mm], bold_first=True))

    d.add(H1("4 Look library M01–M17 — as programmed"))
    d.add(P("The looks live on **Page 6 (M01–M10)** and **Page 7 (M11–M17)** for rebuilding and rehearsal. "
            "Performances run the scene memories on P2/P3 and the song memories on P4, which were built from "
            "these looks. Values below are read from the R13.1 show file."))
    d.add(swatch_legend(), look_table())
    d.add(box("verify", "CHECK IN THE VENUE", "Some backlight choices are deliberately bold (for example "
              "the coral-red backlight under M03 UNDERWATER and the teal backlight in M08 STORM). Look at every "
              "look from the house with performers at the focus session, and record any change in Manual "
              "Appendix B before saving the desk."))

    d.add(H1("5 Songs — Page 4"))
    d.add(P("Each song has its own memory on Page 4. QLab starts the track and the first section together; "
            "every later section is one GO on the music (Part E §4)."))
    d.add(swatch_legend(), song_table())

    d.add(H1("6 FX and chases — Page 5"))
    fx = []
    for m, label, use in [(1, "WARM CHASE", "Rehearsal / optional party energy"),
                          (2, "COOL CHASE", "Rehearsal / optional underwater movement"),
                          (3, "PARTY CHASE", "Optional finale / bows"),
                          (4, "HAZE", "Hazer #40 at 50 %, fan 50 % — run on its fader, 20–40 s before the look"),
                          (5, "HAYWIRE", "Q57 on, Q57b off — fired by QLab (V1, SP4, V2, V3, V4 at 85 %)"),
                          (6, "JELLY PULSE", "Bump for extra Q47 repeats")]:
        mm_ = S_.mem(5, m)
        spec = ("%d steps @ %s BPM" % (mm_["steps"], mm_["bpm"])) if mm_.get("chase") else "single look"
        fx.append(["P5 M%d" % m, "**%s**" % label, spec, use])
    d.add(table(["Desk", "Memory", "Programming", "Use"], fx, [16 * mm, 30 * mm, 36 * mm, 88 * mm]))

    d.add(H1("7 Fixture schedule and focus plan"))
    d.add(P("One row per fixture. Tick when focused; note the final colour/level. Addresses are the venue "
            "patch (Part C)."))
    d.add(table(["#", "Type", "Position", "DMX", "Focus / role", "✓"],
                [[str(n), t, p, a, r, "☐"] for n, t, p, a, r in FOCUS],
                [9 * mm, 12 * mm, 20 * mm, 17 * mm, 104 * mm, 8 * mm]))
    d.add(H2("Focus notes"))
    d.add(bullets([
        "FOH C42s: cross-light each zone from both sides; shutter off the screen, the proscenium and the front "
        "row. Fit the 26° or 36° lenses if the pools don't overlap.",
        "Specials: shutter each C42 tight to its glow-tape mark. The shell special (#10) is the brightest thing "
        "on stage in Scene Eight.",
        "LX1 Zooms: overlap by a third; barn doors cut the top edge so nothing reaches the screen.",
        "LX2: COB PARs down-and-forward to head height at the DS edge; PixBars tilted downstage, never onto the "
        "screen (R-25). The show runs the backlight hard, so check screen washout with BG-02 and BG-18 running.",
        "Side booms: Zoom high at head height across the stage; COB mid and low for bodies and dance.",
        "Voice transfer: Zooms #19–20 at 13° with barn doors match Dame and Flanders (#11–12); match the four "
        "levels by eye."]))
    d.add(notes_area("Designer / focus notes", 8))
    return d.build()
