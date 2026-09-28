"""Part C — DMX Patch & Step-by-Step Guide."""
from core import *  # noqa: F401,F403
import show as S_
from part_b import FOCUS

LIB = {"C42": ("LIGHTSKY · CX 42 NEW", "11 ch"), "ZM": ("TOUR PR0 · ZOOM 12 CHANNEL", "12 ch"),
       "COB": ("TOUR PRO · TOURCOB PAR", "6 ch"), "PIX": ("TOUR PRO · PIXBAR 6CH", "6 ch"),
       "HAZE": ("GENERIC · HAZER 2CH", "2 ch"), "PIN": ("Generic dimmer (1 ch)", "1 ch")}
SPAN = {"C42": 11, "ZM": 12, "COB": 6, "PIX": 6, "HAZE": 2, "PIN": 1}
MAPS = {
    "Lightsky 8800-C42 · CX 42 NEW · 11 ch": [("1", "Red", "255"), ("2", "Amber", "0"), ("3", "Lime", "0"), ("4", "Green", "255"),
                                              ("5", "Blue", "255"), ("6", "UV", "0"), ("7", "CCT", "0"), ("8", "Colour macro", "0 · keep 0"),
                                              ("9", "Intensity", "0"), ("10", "Control", "0 · keep 0"), ("11", "Strobe", "0 · keep 0")],
    "Tour Pro Zoom · ZOOM 12 CHANNEL · 12 ch": [("1", "Intensity", "0"), ("2", "Red", "255"), ("3", "Green", "255"), ("4", "Blue", "255"),
                                                ("5", "White", "0"), ("6", "Control", "keep 0"), ("7", "Strobe", "keep 0"), ("8", "Zoom", "set in focus"),
                                                ("9", "Other", "keep 0"), ("10", "Default", "keep 0"), ("11", "Auto speed", "keep 0"), ("12", "Reset", "keep 0")],
    "Tour Pro TourCOB PAR · 6 ch": [("1", "Intensity", "0"), ("2", "Red", "255"), ("3", "Green", "255"), ("4", "Blue", "255"),
                                    ("5", "White", "0"), ("6", "Strobe", "keep 0")],
    "Tour Pro PixBar · PIXBAR 6CH · 6 ch": [("1", "Red", "255"), ("2", "Green", "255"), ("3", "Blue", "255"), ("4", "White", "0"),
                                            ("5", "Amber", "0"), ("6", "UV", "0")],
    "Hazer · HAZER 2CH · 2 ch": [("1", "Output", "0"), ("2", "Fan", "0")]}


def fader(n):
    return "Console" if n <= 24 else ("Wing 1" if n <= 36 else "Wing 2")


def build(path):
    d = PartDoc(path, "C", "DMX Patch & Step-by-Step Guide",
                "The venue patch (40 fixtures + optional pinspots), channel maps, Art-Net/sACN network, fader map, the "
                "patch procedure for the show file, rig sheets, power and troubleshooting.")
    d.add(title_block("PART C · %s · %s" % (REV, DATE), "DMX Patch & Step-by-Step Guide",
                      "Confirmed desk patch, channel maps, network, and the procedure from load to rig check"))
    d.add(stats([("40", "fixtures patched (base file)"), ("2", "optional pinspots #41–42"),
                 ("2", "universes (DMX + Art-Net/sACN)"), ("0", "re-addressing needed")]))
    d.add(box("rule", "WHERE THINGS LIVE", ["%s carries the venue base patch, custom fixtures and network. "
               "**HAZE is P5 M4**, P2 M3 is the ship/storm scene memory, and the optional pinspots go on **P5 M7** (free)." % S_.MTR_NAME]))
    d.add(box("rule", "THE ADDRESS TRAVELS WITH THE FIXTURE", "Every fixture keeps its desk number and DMX address wherever it "
              "hangs. Moving a C42 to the FOH truss means re-cabling it into the universe 2 line — not changing its address."))
    d.add(H2("Address map"))
    d.add(table(["Universe", "Range", "Fixtures", "Free"], [
        ["U1", "1–36", "PixBars #33–38 (6 ch)", ""], ["U1", "37–38", "Pinspots #41–42 (optional)", ""],
        ["U1", "39–300", "—", "262 free (future moving heads)"], ["U1", "301–420", "Tour Pro Zooms #13–22 (12 ch)", ""],
        ["U1", "421–486", "TourCOB PARs #23–32 and #39 (6 ch)", ""], ["U1", "487–488", "Hazer #40 (2 ch)", "489–512 free"],
        ["U2", "101–232", "Lightsky C42 #1–12 (11 ch)", "1–100 and 233–512 free"]], [20 * mm, 24 * mm, 76 * mm, 50 * mm]))

    d.add(H1("1 Master DMX patch"))
    rows = []
    for n, typ, pos, addr, role in FOCUS:
        u, a = addr.split(":")
        a = int(a)
        lib, mode = LIB[typ]
        rng = "%s:%d–%d" % (u, a, a + SPAN[typ] - 1) if SPAN[typ] > 1 else addr
        inten = {"C42": a + 8, "ZM": a, "COB": a, "PIX": "virtual", "HAZE": a, "PIN": a}[typ]
        rows.append([str(n), lib, mode, rng, str(inten), "A%03d" % a, pos, fader(n)])
    d.add(table(["#", "Desk library", "Mode", "Universe:address", "Intensity at", "Display", "Position", "Fader"], rows,
                [8 * mm, 46 * mm, 12 * mm, 26 * mm, 18 * mm, 14 * mm, 26 * mm, 20 * mm]))

    d.add(H1("2 Channel maps"))
    d.add(P("Each fixture must be in the matching DMX mode (11 / 12 / 6 channels) or colours land on the wrong channels. "
            "Home = value when the fixture is cleared."))
    for name, rows in MAPS.items():
        d.add(KeepTogether([P("**" + name + "**", "h3"), table(["Ch", "Function", "Home / rule"], [list(r) for r in rows],
                                                               [12 * mm, 50 * mm, 108 * mm])]))
    d.add(box("verify", "KEEP CONTROL-TYPE CHANNELS AT 0", "Control, Strobe, Reset, Auto speed, Other, Default and Colour macro "
              "can trigger resets, strobing or built-in programs. Every cue in the R13.1 file keeps them at 0; lightning is done "
              "with intensity (R-04). The Zoom library name is spelled TOUR PR0 (zero) on the desk — cosmetic only."))

    d.add(H1("3 DMX runs, network and fader map"))
    d.add(table(["Line", "Route"], [
        ["Universe 1 (desk XLR)", "Desk → LX1 Zooms #13–18 → LX2 (#19–20, 23–28, 39, 33–38) → SR boom (#21, 29–30) → SL boom (#22, 31–32) → hazer #40 · terminate"],
        ["Universe 2 (Ethernet)", "Desk → switch → node 2.0.0.10 → FOH truss C42 #1–8 → LX1 C42 #9–12 · terminate"]],
        [38 * mm, 132 * mm], bold_first=True))
    d.add(table(["Setting", "Desk (Mantra)", "Node for universe 2"], [
        ["IP address", "2.0.0.1 (static, DHCP off)", "2.0.0.10"], ["Subnet mask", "255.0.0.0", "255.0.0.0"],
        ["Protocols", "Art-Net on · sACN on — turn off the one the node doesn't use", "sACN universe 2, or Art-Net 0-0-1"]],
        [30 * mm, 80 * mm, 60 * mm]))
    d.add(table(["Faders", "Fixtures"], [["Console 1–12", "C42 #1–8 FOH · #9–12 LX1"], ["Console 13–24", "Zoom #13–18 LX1 · #19–20 LX2 · #21 SR · #22 SL · COB #23–24 LX2"],
                                         ["Wing 1 25–36", "COB #25–28 LX2 · #29–30 SR · #31–32 SL · PixBar #33–36"],
                                         ["Wing 2 37–48", "PixBar #37–38 · COB #39 · hazer #40 · pinspots #41–42 · 43–48 spare"]],
                [30 * mm, 140 * mm], bold_first=True))
    d.add(P("Both wings must be connected (fixtures 25–42). Printed fader labels: 03_Lighting_Mantra/TLM_R13_1_Mantra_Labels.pdf."))

    d.add(H1("4 Step-by-step patch procedure"))
    for title, items in [
        ("1 Back up what is on the desk", ["FAT32 USB stick in the Mantra. Home › Tools › Export Show — keep it untouched as the venue restore point.",
                                           "Keep BASE_SHOW_2026.mtr (the clean venue base) on the stick too."]),
        ("2 Load the R13.1 show file", ["Copy %s to the stick (check it in Mantra Editor first — Part D §9)." % S_.MTR_NAME,
                                        "Home › Tools › Import Show › choose it. Check five custom fixture types: CX 42 NEW, ZOOM 12 CHANNEL, TOURCOB PAR, PIXBAR 6CH, HAZER 2CH."]),
        ("3 Clear the output", ["A L, then O, so nothing is live while you check the patch."]),
        ("4 Check fixtures 1–40", ["Tools › Setup › Patch. Step through against section 1: number, library, universe, address.",
                                   "Expected: #1–12 U2:101–232 · #13–22 U1:301–420 · #23–32 U1:421–480 · #33–38 U1:1–36 · #39 U1:481–486 · #40 U1:487–488."]),
        ("5 Pinspots — only if the mirror ball is used", ["Generic dimmer, U1:37 as #41 and U1:38 as #42 → Patch.",
                                                          "Record both at full on **P5 M7** (free in R13.1). Save."]),
        ("6 Network and universe 2", ["Tools › Setup › Network: 2.0.0.1, 255.0.0.0; turn off Art-Net or sACN (whichever the node doesn't use).",
                                      "Set the node, connect it through the switch, run its DMX out to the FOH truss. Test C42 #1 at 50 %."]),
        ("7 Remote trigger for QLab (R13.1)", ["Tools › Setup › Remote Triggers › Add › OSC · Play Memory · port 8000. Save."]),
        ("8 Cable, power, terminate", ["One chain per universe in the order of section 3; label both ends; terminate the last fixture.",
                                       "No more than about 1,840 W per 10 A circuit."]),
        ("9 Rig check and save", ["Each fixture alone at 50 %, then 0 → 100 %, then each colour. Use the ROW memories (100–103) for each type.",
                                  "Confirm PixBar #38 and TourCOB #39 physically exist (R13.1 fix list). Save (T S), export to USB, tick the rig sheets."])]:
        d.add(KeepTogether([P("**" + title + "**", "h3")] + steps(items)))

    d.add(H1("5 Rig sheets by position"))
    for pos in ["FOH", "FOH SR end", "FOH SL end", "LX1", "LX2", "SR boom", "SL boom", "Floor, US"]:
        rows = [[str(n), typ, LIB[typ][1], addr, role, "☐", "☐", "☐", "☐"] for n, typ, p, addr, role in FOCUS if p == pos]
        if rows:
            d.add(KeepTogether([P("**%s**" % pos, "h3"), table(["#", "Type", "Mode", "Start", "Role / focus", "Addr", "DMX", "Pwr", "Test"],
                                                               rows, [8 * mm, 12 * mm, 12 * mm, 16 * mm, 86 * mm, 9 * mm, 9 * mm, 9 * mm, 9 * mm])]))

    d.add(H1("6 Power, labels and troubleshooting"))
    d.add(table(["Position", "Fixtures", "Known load", "Suggested"], [
        ["FOH", "8 × C42", "2,400 W (10.4 A)", "2 × 10 A"], ["LX1", "4 × C42 + 6 × Zoom", "~2,280 W (9.9 A)", "2 × 10 A"],
        ["LX2", "2 Zoom, 7 COB, 6 PixBar", "360 W + label ratings", "1 × 10 A"], ["SR / SL boom", "1 Zoom + 2 COB each", "180 W + labels", "1 × 10 A each"],
        ["Floor", "Hazer", "From label", "1 × 10 A"]], [30 * mm, 50 * mm, 50 * mm, 40 * mm]))
    d.add(table(["Symptom", "Likely cause", "Fix"], [
        ["Two fixtures respond together", "Duplicate address", "Check displays against the master patch"],
        ["Colours on the wrong channel", "Wrong DMX mode", "Set 11 / 12 / 6 ch to match section 2"],
        ["All C42s dead, U1 fine", "Universe 2 not reaching the node", "Switch, node IP, node universe"],
        ["Nothing past a fixture", "Broken cable / through-port", "Swap the cable after the last working unit"],
        ["Random flicker", "No terminator or mic cable", "Terminate; use DMX cable"],
        ["Fixture strobes or resets", "Control/Strobe/Reset not 0", "Clear it; record 0"],
        ["Looks stack with odd colours", "Another memory still playing (LTP)", "O (All Cues Off) and re-fire; check the QLab release cue"]],
        [48 * mm, 52 * mm, 70 * mm]))
    d.add(notes_area("Patch notes / changes", 6))
    return d.build()
