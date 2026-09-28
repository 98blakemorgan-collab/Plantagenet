"""Part K — Quick Reference Cards (seven one-page cards) + the stand-alone Setup & Start-up Quick Guide."""
from core import *  # noqa: F401,F403
import show as S_
from part_d import PAGEMAP


def card1():
    return [P("1 Rig layout", "h1"),
            P("One FOH bar, two stage bars (LX1, LX2) and a floor boom in each wing. Projector centre stage towards the back, "
              "throwing upstage onto the screen.", "muted"),
            table(["Position", "Fixtures (desk numbers)", "Qty"], [
                ["FOH bar", "8 × Lightsky C42 #1–8 (#1–6 faces, #7 SP1 Ariel, #8 SP2 Spirit)", "8"],
                ["LX1 — downstage bar", "4 × C42 #9–12 (SP3 Octavia, SP4 Shell, V1 Dame, V2 Flanders) · 6 × Zoom #13–18 colour wash", "10"],
                ["LX2 — upstage bar", "2 × Zoom #19–20 (V3 Theodore, V4 Marina) · 7 × TourCOB #23–28, 39 · 6 × PixBar #33–38", "15"],
                ["SR floor boom", "Zoom #21 high · TourCOB #29 mid, #30 shin", "3"],
                ["SL floor boom", "Zoom #22 high · TourCOB #31 mid, #32 shin", "3"],
                ["Floor, upstage", "Hazer #40", "1"], ["Optional", "Pinspots #41–42 on the FOH bar ends (mirror ball only)", "(2)"]],
                [36 * mm, 120 * mm, 14 * mm], bold_first=True),
            box("rule", "THE RULES", "Faces come from FOH (C42 #1–6). LX1 = colour top wash. LX2 = backlight + PixBars, focused "
                "downstage and never onto the screen (R-25). Booms = side colour across the stage (R-26). Every fixture keeps its "
                "desk number and address wherever it hangs. Proposed wet zone mid-stage audience-left — confirm at the site walk.")]


def card2():
    rows = [[r[0], r[1], r[2]] for r in PAGEMAP]
    return [P("2 Desk layout", "h1"),
            P("LSC Mantra Lite + 2 wings · %s · QLab fires every cue — the desk is the backup." % S_.MTR_NAME, "muted"),
            table(["Page", "Purpose", "Memories"], rows, [12 * mm, 40 * mm, 118 * mm], bold_first=True,
                  tints=[(1, "new"), (2, "new"), (3, "new")]),
            table(["Control", "Use"], [
                ["P2 M10 SAFE LIGHT", "Emergency face light (QLab E3 fires it too)"],
                ["Next Cue on a P2/P3/P4 memory", "Backup only, if QLab or the network fails — press again after each flash"],
                ["P5 M4 HAZE", "Hazer #40 on its fader (50 %, fan 50 %)"],
                ["P5 M5 HAYWIRE", "QLab starts it at Q57 and stops it at Q57b"],
                ["P5 M6 JELLY PULSE", "Bump for extra Q47 repeats"],
                ["O · A then L · T then S", "All Cues Off · Clear All · Save"]], [52 * mm, 118 * mm], bold_first=True),
            box("rule", "NO LINK TIMES", "No link times are set on the desk: QLab fires every flash return "
                "(Q21, Q23, Q25 +0.2 s · Q35 +0.3 s · Q47 +1 s · Q57b +0.3 s) and releases each memory as it leaves it.")]


def card3():
    return [P("3 DMX and network", "h1"),
            P("Universe 1 on the desk XLR, universe 2 over Ethernet to a node. One chain per universe, terminated.", "muted"),
            table(["U", "Addresses", "Fixtures"], [["U1", "1–36", "PixBars #33–38 (6 ch)"], ["U1", "37–38", "Pinspots #41–42 (optional)"],
                                                   ["U1", "301–420", "Zooms #13–22 (12 ch)"], ["U1", "421–486", "TourCOB #23–32, #39 (6 ch)"],
                                                   ["U1", "487–488", "Hazer #40 (2 ch)"], ["U2", "101–232", "Lightsky C42 #1–12 (11 ch)"]],
                  [12 * mm, 30 * mm, 128 * mm]),
            table(["Item", "Setting"], [["Desk", "2.0.0.1 / 255.0.0.0, DHCP off · Art-Net + sACN on (turn off the unused one)"],
                                        ["U1 route", "Desk XLR → LX1 → LX2 → SR boom → SL boom → hazer · terminate"],
                                        ["U2 route", "Desk Ethernet → switch → node 2.0.0.10 → FOH C42 #1–8 → LX1 #9–12 · terminate"],
                                        ["Node", "sACN universe 2, or Art-Net 0-0-1"],
                                        ["QLab → desk", "OSC Play Memory, UDP 2.0.0.1 port 8000 (add the trigger on the desk)"]],
                  [30 * mm, 140 * mm], bold_first=True),
            box("verify", "KEEP AT 0", "Control, Strobe, Reset, Auto speed, Other, Default, Zoom (except in focus), CCT and Colour "
                "macro. Modes: C42 11 ch · Zoom 12 ch · COB 6 ch · PixBar 6 ch · hazer 2 ch.")]


def card4():
    looks = [[L["name"], "P%d M%d" % (L["page"], L["mem"]), swatch_strip(L["summary"], cell=6 * mm, h=4 * mm)] for L in S_.LOOKS]
    half = (len(looks) + 1) // 2
    lt = Table([[table(["Look", "Desk", "Colour"], looks[:half], [30 * mm, 13 * mm, 38 * mm]),
                 table(["Look", "Desk", "Colour"], looks[half:], [30 * mm, 13 * mm, 38 * mm])]], colWidths=[85 * mm, 85 * mm])
    lt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return [P("4 Specials, looks and critical sequences", "h1"),
            table(["Special", "Character", "Fixture", "Mark"], [
                ["SP1", "Ariel", "#7 C42 FOH", "DSC"], ["SP2", "Spirit", "#8 C42 FOH", "DS audience-left"],
                ["SP3", "Octavia", "#9 C42 LX1", "US audience-right"], ["SP4", "Shell", "#10 C42 LX1", "Plinth"],
                ["V1–V2", "Dame, Flanders", "#11–12 C42 LX1", "Voice marks 1–2"], ["V3–V4", "Theodore, Marina", "#19–20 Zoom 13° LX2", "Voice marks 3–4"]],
                [18 * mm, 34 * mm, 44 * mm, 74 * mm], bold_first=True),
            lt,
            table(["Sequence", "Cues", "Desk", "Note"], [
                ["Storm", "Q20–27.5", "P2 M3", "Flashes 21/23/25 return +0.2 s (QLab)"],
                ["Transformation", "Q33–36", "P2 M5", "35 white hit → 35b +0.3 s"],
                ["Voice transfer", "Q52–57b", "P3 M3", "Shell → Dame → Flanders → Theodore → Marina; HAYWIRE Q57 → Q57b"],
                ["Jellyfish", "Q45–49", "P3 M2", "47 pulse returns +1 s; repeats on P5 M6"]], [30 * mm, 22 * mm, 18 * mm, 100 * mm], bold_first=True)]


def card5():
    return [P("5 System connections", "h1"),
            P("How QLab, the Mantra, the StudioLive, the node and the projector link. Subnet 255.0.0.0 for everything.", "muted"),
            table(["Device", "IP", "Settings"], [
                ["Mantra Lite", "2.0.0.1", "Art-Net + sACN · OSC Play Memory trigger port 8000"],
                ["Art-Net / sACN node", "2.0.0.10", "Universe 2"],
                ["QLab Mac", "2.0.0.20", "Manual IPv4 · Wi-Fi off · MANTRA patch → 2.0.0.1:8000 on the Ethernet interface"],
                ["Backup Mac", "2.0.0.21", "Optional — songs as plain files (R-08)"],
                ["StudioLive 16", "2.0.0.30", "Optional — iPad / UC Surface"]], [36 * mm, 24 * mm, 110 * mm], bold_first=True),
            table(["Link", "Carries"], [["QLab → StudioLive (USB)", "Playback on ch 11–12 · backup playback ch 13–14 · radios ch 1–8"],
                                        ["QLab → projector (HDMI via HDBaseT)", "Backdrops · VID-99 black"],
                                        ["Stream Deck → QLab (USB)", "GO · Panic · F13/F14/F15 → E2/E3/E1"],
                                        ["Desk XLR / Ethernet", "Universe 1 DMX · universe 2 Art-Net/sACN via node"]],
                  [60 * mm, 110 * mm], bold_first=True),
            box("rule", "TEST IN THIS ORDER", "1 Sound: any QLab cue — level on ch 11–12. 2 Lights: QLab E3 SAFE LIGHT — desk "
                "plays P2 M10; then Q4 — desk plays P2 M1 cue 4. 3 Universe 2: C42 #1 up. 4 Video: Q4 — BG-02 fades up; E2 → black.")]


def card6():
    return [P("6 First-time setup", "h1"),
            P("Once, at the first venue session. About three hours with the rig hung.", "muted"),
            P("**1 Rig and patch**"), *steps(["Hang and focus (card 1); booms weighted; projector on the bar with its bond.",
                                             "Check modes and addresses (Part C); cable U1 and U2; terminate both."]),
            P("**2 Network**"), *steps(["Mantra, node and QLab Mac on the show switch. No internet, no Wi-Fi.",
                                       "Mac: Network › Ethernet › TCP/IP › Manually 2.0.0.20 / 255.0.0.0, router blank. Node 2.0.0.10."]),
            P("**3 Mantra**"), *steps(["Tools › Export Show (venue backup).",
                                      "Tools › Import Show › %s. Check P2 Act One, P3 Act Two, P4 songs, P5 FX, P8 backup." % S_.MTR_NAME,
                                      "Tools › Setup › Remote Triggers › Add › OSC · Play Memory · port 8000. Turn off Art-Net or sACN (whichever the node doesn't use).",
                                      "Save (T S) and set as Default Show. **No link times needed.**"]),
            P("**4 QLab Mac**"), *steps(["Harden the Mac (R-07); install QLab 5 and the licence.",
                                        "Put %s on the Desktop (exact name). Open %s." % (S_.FOLDER, S_.QLAB_NAME),
                                        "Workspace Settings: Audio → StudioLive USB · Video Stage 1 → projector · Network MANTRA → Ethernet interface. Save.",
                                        "Check no red cues; select Q4's audio — target ends in _v2.wav."]),
            P("**5 StudioLive**"), *steps(["USB to the Mac: ch 11–12 = USB (QLab), 13–14 = backup, radios 1–8.",
                                          "Gains/EQ; principals on one DCA; save scene TLM SHOW."]),
            P("**6 Stream Deck**"), *steps(["Import TLM QLab Show.streamDeckProfile.",
                                           "In QLab give E2 hotkey F13, E3 F14, E1 F15 (Triggers tab); save."]),
            P("**7 Test and back up**"), *steps(["Step through a cue-to-cue from Q1 (Part L); fix anything red.",
                                                "Export the Mantra show to USB; copy the whole show folder to a second drive."])]


def card7():
    return [P("7 Start-up and shut-down — every session", "h1"),
            table(["When", "Do"], [
                ["T−90 power up", "Mains/RCDs → fixtures, node, switch → Mantra (loads the Default Show) → projector → StudioLive (scene TLM SHOW) → amps last"],
                ["T−80 QLab Mac", "Wi-Fi off, charger in. Open %s from the Desktop folder. No red cues; Stream Deck profile; projector = Stage 1 (not mirrored)" % S_.QLAB_NAME],
                ["T−70 system check", "E3 SAFE LIGHT → desk plays P2 M10; ROW memories check every fixture; a QLab cue → ch 11–12; Q4 → BG-02; E2 → black"],
                ["T−45 reset", "Esc (Panic) in QLab; Mantra O (All Cues Off). Playhead on Q1; Show Mode. Haze check and detector isolation logged (R-13)"],
                ["T−30 house open", "SM calls Q1 → GO. From here every cue is one GO in QLab (Space or Stream Deck)"]],
                [30 * mm, 140 * mm], bold_first=True),
            table(["Shut-down", ""], [["1", "QLab: Esc (Panic), then save"], ["2", "Amps / speakers off first"],
                                      ["3", "StudioLive off (save the scene if changed)"], ["4", "Projector standby — let the fan finish"],
                                      ["5", "Mantra: save if changed, export to USB, power off"], ["6", "Fixtures, node, switch off; Mac off; hazer off and clean"]],
                  [14 * mm, 156 * mm]),
            box("verify", "IF SOMETHING FAILS MID-SHOW", "Lights: the matching Mantra P2/P3/P4 memory with Next Cue (again after "
                "each flash) · SAFE LIGHT = P2 M10. Sound: backup playback ch 13–14. Video: E2 black or AV-mute. Keep going — the SM "
                "decides on any hold.")]


CARDS = [card1, card2, card3, card4, card5, card6, card7]


def build(path):
    d = PartDoc(path, "K", "Quick Reference Cards",
                "Seven one-page cards: rig layout, desk layout, DMX and network, specials and looks, system connections, "
                "first-time setup, and session start-up and shut-down.")
    for i, c in enumerate(CARDS):
        d.add(c())
        if i < len(CARDS) - 1:
            d.add(PageBreak())
    return d.build()


def build_quick_guide(path):
    d = PartDoc(path, "", "Setup and Start-up Quick Guide", divider=False,
                header_left="THE LITTLE MERMAID · QUICK REFERENCE CARDS · " + REV)
    d.add(card6(), PageBreak(), card7())
    return d.build()
