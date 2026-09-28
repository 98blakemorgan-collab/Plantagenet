"""Part D — Mantra Editor on Mac: programming guide for the R13.1 show file."""
from core import *  # noqa: F401,F403
import show as S_

PAGEMAP = [
    ("P1", "Venue / rig base", "M1 STAGE WORK · M2 FULL WHITE · M3 WARM · M4 COOL · M5 BLUE · M6 RED · M9 PIXBAR WASH · M10 CURTAIN CALL", "Venue house looks (base file)"),
    ("P2", "Act One — scene sections", "M1 Q1–11 · M2 Q12–17 · M3 ship/storm Q18–27.5 · M4 shore/duet Q28–30.5 · M5 bar/transformation Q31–37 · M6 interval Q38 · M9 WORK/FOCUS · M10 SAFE LIGHT", "Performance"),
    ("P3", "Act Two — scene sections", "M1 palace Q39–44 · M2 jellyfish Q45–49 · M3 lair/voice/haywire Q50–58.5 · M4 dry land Q59–59.7 · M5 wedding Q60–63.5 · M6 bows/end Q64–65", "Performance"),
    ("P4", "Songs", "M1 S1 Rock Lobster … M10 S10 He's a Pirate", "Performance"),
    ("P5", "FX / chases", "M1 WARM CHASE · M2 COOL CHASE · M3 PARTY CHASE · M4 HAZE · M5 HAYWIRE · M6 JELLY PULSE", "Q57/Q57b + manual"),
    ("P6", "Look library", "M01 BLACKOUT … M10 MAGIC", "Rehearsal / rebuild"),
    ("P7", "Look library", "M11 LAIR … M16 BOWS · M7 = M17 SAFE LIGHT", "Rehearsal / rebuild"),
    ("P8", "Backup / reference", "M1 = the full 153-position list (BACKUP - 01 PRESHOW …)", "Emergency only"),
]


def section_rows(p, m):
    rows, tints = [], []
    for r in S_.MAP_ROWS:
        if int(r["Performance Page"]) == p and int(r["Playback Memory"]) == m:
            c = int(r["Cue In Section"])
            _, summ, _ = S_.position_summary(p, m, c)
            auto = "auto" in r["QLab trigger"]
            rows.append([str(c), "**%s**" % r["Cue Name"], swatch_strip(summ, cell=4.3 * mm, h=4 * mm),
                         r["Fade In (s)"], r["QLab trigger"].replace(" (auto", " · auto").replace(")", "") if auto
                         else r["QLab trigger"], r["Backup Position"]])
            if auto:
                tints.append((len(rows) - 1, "auto"))
            elif r["Fade In (s)"] == "0":
                tints.append((len(rows) - 1, "crit"))
    return rows, tints


def build(path):
    d = PartDoc(path, "D", "Mantra Editor on Mac",
                "Mac setup, show transfer, the R13.1 page map, look library, scene and song memories with every "
                "cue as programmed, critical sequences, QLab OSC triggers and the built show file.")
    d.add(title_block("PART D · %s · %s" % (REV, DATE), "Mantra Editor on Mac",
                      "LSC Mantra Lite programming guide for %s" % S_.MTR_NAME))
    d.add(stats([("8", "pages in use (P1–P8)"), (str(S_.N_POSITIONS), "cue positions"),
                 ("0", "desk link times needed"), ("2.0.0.1:8000", "OSC Play Memory"), ("153", "P8 backup steps")]))
    d.add(box("rule", "HOW THE SHOW FILE WORKS",
              ["The show is split into scene memories (P2 Act One, P3 Act Two) and song memories (P4); "
               "QLab plays the exact memory and cue for every step. The six flash returns are **fired by QLab** "
               "(timed pre-waits), so no link times are set on the desk. Each time QLab moves to a new memory it "
               "also sends **Level=0 to the memory it is leaving** (31 release messages), so looks can't stack. "
               "Page 8 keeps the full 153-step list as a manual backup."]))

    d.add(H1("1 Getting Mantra Editor running on a Mac"))
    d.add(table(["Option", "How", "Notes"], [
        ["A. Native Mac app", "Check LSC's Mantra Editor download (mantralite.lsccontrol.com.au) for a macOS build.",
         "If macOS blocks it: System Settings › Privacy & Security › Open Anyway."],
        ["B. Windows on the Mac", "Parallels Desktop or VMware Fusion running Windows 11, then the Windows editor.",
         "Set the VM network to Bridged for on-line editing; share a Mac folder for show files."],
        ["C. Borrow a Windows laptop", "Install the editor on any Windows PC.",
         "Simplest for on-line editing at the venue. Network profile = Private."]],
        [34 * mm, 72 * mm, 64 * mm], bold_first=True))
    d.add(H3("Prepare the USB stick"))
    d.add(steps(["Disk Utility › select the stick (device) › Erase: **MS-DOS (FAT)**, Master Boot Record, name MANTRA.",
                 "Keep the stick for show files only. `dot_clean /Volumes/MANTRA` removes macOS's hidden ._ files.",
                 "Always Eject before pulling the stick out of the Mac or the console."]))
    d.add(table(["Step", "Where", "Action"], [
        ["1", "Mantra Lite", "Rear USB socket · Home › Tools › Export Show › Save (backup of what is on the desk)"],
        ["2", "Mac / editor", "Home › Tools › Import Show › choose the file"],
        ["3", "Editor", "Edit. An * after the show name means unsaved changes. Save with T then S"],
        ["4", "Editor", "Tools › Export Show to the stick"],
        ["5", "Mantra Lite", "Home › Tools › Import Show, then save as the Default Show so it loads on power-up"]],
        [12 * mm, 26 * mm, 132 * mm]))
    d.add(H2("Editor shortcuts"))
    d.add(table(["Key", "Function", "Key", "Function"], [
        ["Esc", "Back / Home", "O", "All Cues Off"],
        ["A then L", "Clear All (empty the programmer)", "T then S", "Save show"],
        ["↑ / ↓", "Intensity ±1 %", "fn + ↑ / fn + ↓", "Intensity ±10 % (MacBook)"],
        ["Rec + click displayer", "Record to a memory", "Rec + hold 1 s", "Update the playing cue"]],
        [30 * mm, 55 * mm, 30 * mm, 55 * mm]))

    d.add(H1("2 Show architecture — the R13.1 page map"))
    d.add(table(["Page", "Purpose", "Memories", "Used for"], [list(r) for r in PAGEMAP],
                [12 * mm, 38 * mm, 90 * mm, 30 * mm], bold_first=True,
                tints=[(1, "new"), (2, "new"), (3, "new")]))
    d.add(box("rule", "OPERATING PRINCIPLE",
              ["QLab normally calls every lighting cue. If the link fails, continue from the matching **P2 / P3 "
               "scene memory or P4 song memory** with Next Cue — not from Page 8. SAFE LIGHT stays on **P2 M10** "
               "(and P7 M7 = M17), always reachable.",
               "LTP rule: Mantra attributes are latest-takes-precedence. Don't play library looks (P6–P7) over the "
               "show in performance."]))
    d.add(P("Numbering: the desk numbers cues by position inside each memory. Every cue is **named with its master "
            "cue number** (for example `21 LIGHTNING 1`, `21b STORM RETURN`, `S1.3 LOBSTER CHORUS`), so the "
            "operator follows the names. Section tables below give both the in-memory cue and the P8 backup "
            "position."))

    d.add(H1("3 Patch"))
    d.add(P("The venue base patch travels in the show file: C42 #1–12 at U2:101–232 (11 ch), "
            "Zooms #13–22 at U1:301–420 (12 ch), TourCOB #23–32 and #39 at U1:421–486 (6 ch), PixBars #33–38 at "
            "U1:1–36 (6 ch), hazer #40 at U1:487–488. Pinspots #41–42 (U1:37–38) only if the mirror ball is used. "
            "Full table and procedure: Part C. Network in the file: **2.0.0.1 / 255.0.0.0, Art-Net and sACN both on, "
            "DHCP off** — turn off whichever protocol the U2 node doesn't use."))

    d.add(H1("4 Look library (P6–P7)"))
    d.add(P("The 17 looks as programmed (full recipes in Part B §4). Use them to rebuild or relight, not in shows."))
    d.add(swatch_legend())
    rows = [["**%s**" % L["name"], "P%d M%d" % (L["page"], L["mem"]), swatch_strip(L["summary"]),
             describe(L["summary"])] for L in S_.LOOKS]
    d.add(table(["Look", "Desk", "Layers", "As programmed"], rows, [30 * mm, 14 * mm, 57 * mm, 69 * mm]))

    d.add(H1("5 Scene memories — every cue as programmed"))
    d.add(P("Cue = position inside the memory (what QLab sends). Fade = Fade In seconds. Green rows are flash "
            "returns fired automatically by QLab; tinted rows are 0-second hits. P8 = the same cue on the backup list."))
    d.add(swatch_legend())
    for sec in [s for s in S_.SECTIONS if s["p"] in (2, 3)]:
        mm_ = S_.mem(sec["p"], sec["m"])
        rows, tints = section_rows(sec["p"], sec["m"])
        d.add(H2("P%d M%d — %s … %s (%d cues)" % (sec["p"], sec["m"], sec["first"], sec["last"], sec["count"])))
        d.add(table(["Cue", "Name on desk", "Layers", "Fade", "Fired by QLab", "P8"], rows,
                    [10 * mm, 42 * mm, 27 * mm, 11 * mm, 70 * mm, 10 * mm], tints=tints))
    d.add(H2("P2 M9 WORK / FOCUS · P2 M10 SAFE LIGHT"))
    d.add(P("Open white work light and the recovery look (FOH #1–6 at about 70 % white, no colour). QLab **E3** "
            "plays P2 M10 over 2 s; the operator can also press it on the desk."))

    d.add(H1("6 Song memories (P4)"))
    rows = []
    for so in S_.SONGS:
        summs = [S_.position_summary(4, s["m"], s["c"])[1] for s in so["sections"]]
        rows.append(["**%s**" % so["num"], "%s<br/>P4 M%d · at Q%s" % (so["title"], so["mem"], so["at"]),
                     section_strip(summs, 70 * mm),
                     " · ".join("%s %s" % (s["num"], s["fade"] if s["fade"] else "0") for s in so["sections"])])
    t = table(["Song", "Memory", "Sections as programmed", "Cue · fade (s)"], rows,
              [12 * mm, 38 * mm, 72 * mm, 48 * mm])
    d.add(t)
    d.add(P("QLab starts each song with its track: it releases the scene memory underneath and plays cue 1 of the "
            "song memory. Later sections are separate GOs. When the next scene cue fires, QLab releases the song "
            "memory (Level=0)."))

    d.add(H1("7 Critical sequences"))
    d.add(H2("Flash returns — fired by QLab (no link times)"))
    fl = []
    for num, x in S_.FLASHES:
        r = S_.BY_PMC.get((x["p"], x["m"], x["c"]), {})
        hit = S_.BY_PMC.get((x["p"], x["m"], x["c"] - 1), {})
        fl.append(["**Q%s**" % num, "P%d M%d" % (x["p"], x["m"]), "cue %d %s" % (x["c"] - 1, hit.get("Cue Name", "")),
                   "cue %d %s" % (x["c"], r.get("Cue Name", "")), "+%g s" % x["pre"], "%g s" % x["fade"]])
    d.add(table(["QLab cue", "Memory", "Flash (fade 0)", "Return", "Pre-wait", "Return fade"], fl,
                [18 * mm, 18 * mm, 46 * mm, 46 * mm, 20 * mm, 22 * mm], tints=[(i, "crit") for i in range(len(fl))]))
    d.add(box("rule", "IF QLAB IS DOWN", "Run the flash with Next Cue, then press Next Cue again straight away for "
              "the return (or set Link Times on those cues if you prefer — only when running the desk by hand). "
              "Never replay a missed flash after the moment has passed."))
    d.add(H2("Transformation (Q33–Q36 · P2 M5 cues 3–7)"))
    d.add(P("Q33 standby state, Q34 build (violet/teal up), **Q35 white hit** then 35b new state after 0.3 s, Q36 "
            "SP1 → SP4 shell with a dark surround."))
    d.add(H2("Voice transfer and HAYWIRE (Q52–Q57b · P3 M3 cues 3–10)"))
    d.add(table(["Cue", "Desk", "What happens"], [
        ["Q52", "P3 M3 cue 3", "M12 VOICE SHELL — SP4 shell isolated"],
        ["Q53–Q56", "cues 4–7", "Shell → V1 Dame → V2 Flanders → V3 Theodore → V4 Marina (0.3 s crossfades)"],
        ["Q57", "cue 8 + **P5 M5 ON**", "Dark state; QLab starts the HAYWIRE chase (V1, SP4, V2, V3, V4 at 85 %, 120 BPM)"],
        ["Q57b", "cue 9 → cue 10 + **P5 M5 OFF**", "White restore hit, HAYWIRE off, then 57c SP1 Ariel (+0.3 s) and the restore SFX"]],
        [18 * mm, 42 * mm, 110 * mm], bold_first=True, tints=[(2, "crit"), (3, "crit")]))
    d.add(H2("Jellyfish (Q45–Q49 · P3 M2)"))
    d.add(P("Q47 is a 0.25 s cyan pulse; QLab returns to M13 after 1 s (47b). For extra repeats bump **P5 M6 "
            "JELLY PULSE** by hand."))

    d.add(H1("8 QLab triggering (OSC)"))
    d.add(steps([
        "Connect the Mantra to the show LAN (2.0.0.1 / 255.0.0.0).",
        "**Home › Tools › Setup › Remote Triggers › Add → OSC, Play Memory, port 8000.** This trigger is not "
        "stored in the show file — add it on the desk and save.",
        "In QLab the MANTRA network patch is already in the workspace: OSC over UDP to 2.0.0.1 port 8000. Set its "
        "interface to the wired Ethernet port on the show Mac (Workspace Settings › Network)."]))
    d.add(P("Message format (Mantra Lite manual): `/PlayMemory/Page=$p/Memory=$m/Cue=$c/Level=$l/Fade=$ms`. "
            "Level=0 fades the memory down — R13.1 uses that to release the memory it is leaving."))
    ex = []
    for num in ("4", "12", "21", "57", "57b", "65"):
        c = S_.CUE[num]
        for x in c["lx"] + c["fx5"]:
            ex.append(["Q" + num, "/PlayMemory/Page=%d/Memory=%d/Cue=%d/Level=%d/Fade=%d" %
                       (x["p"], x["m"], x["c"], x["lvl"], x["fade"] * 1000) + ("  (+%gs)" % x["pre"] if x["pre"] else "")])
        for p, m, cc, lv, f in c["release"]:
            ex.append(["Q" + num, "/PlayMemory/Page=%d/Memory=%d/Cue=%d/Level=0/Fade=%d  (release)" % (p, m, cc, f)])
    ex.append(["E3", "/PlayMemory/Page=2/Memory=10/Cue=1/Level=100/Fade=2000  (SAFE LIGHT)"])
    d.add(table(["QLab", "Network cue message (examples from the workspace)"], ex, [18 * mm, 152 * mm]))

    d.add(H1("9 The built show file"))
    d.add(table(["Page · memory", "What it is"], [
        ["P1, P2 M9–M10", "Venue base looks, WORK/FOCUS, SAFE LIGHT"],
        ["P2 M1–M6, P3 M1–M6", "The 87 scene cues split into 12 scene memories (names carry the master cue number)"],
        ["P4 M1–M10", "The 66 song-section cues, one memory per song"],
        ["P5 M1–M6", "Chases (150/144/168 BPM), HAZE #40 50 %/fan 50 %, HAYWIRE (5 steps, 120 BPM), JELLY PULSE"],
        ["P6–P7", "Look library M01–M17"],
        ["P8 M1", "Full 153-position backup list"],
        ["Base file", "Patch, custom fixtures, network, rig view and ROW/AREA memories 100–109 from PLANTAGENET_HALL_BASE"]],
        [40 * mm, 130 * mm], bold_first=True))
    d.add(H3("Load it"))
    d.add(steps([
        "Open it in Mantra Editor on the Mac first (Tools › Import Show) and play through P2, P3 and P4.",
        "At the desk: Home › Tools › Export Show (back up what is there).",
        "Copy %s to the root of the FAT32 stick · Home › Tools › Import Show › choose it." % S_.MTR_NAME,
        "Check: P2 shows six scene memories + WORK/FOCUS + SAFE LIGHT; P3 six; P4 ten songs; P5 FX; P6–P7 looks; P8 backup.",
        "Add the OSC Play Memory remote trigger on port 8000 (section 8). Turn off Art-Net or sACN — whichever the node doesn't use.",
        "Fire E3 SAFE LIGHT from QLab, then one cue from every P2/P3 memory and every P4 song. Save (T S) and set as the Default Show."]))
    d.add(P("R13.1 corrected the file-size footer to the real size (4,479,331 bytes). SHA-256 of the checked file "
            "is in BUILD_METADATA.json in the show folder. No strobe values are stored."))

    d.add(H1("10 Checklists and troubleshooting"))
    d.add(checklist(["Editor installed and opens the show", "Show imports without errors", "Patch 1–40 checked",
                     "P2/P3 scene memories named with master cues", "P4 ten song memories", "P5 FX and chases",
                     "OSC Play Memory trigger on port 8000", "E3 SAFE LIGHT from QLab plays P2 M10",
                     "One cue from every memory fired from QLab", "Flash returns come back on their own",
                     "Q57 starts HAYWIRE and Q57b stops it", "Final show exported to USB + Mac"], cols=2))
    d.add(table(["Problem", "Check"], [
        ["Editor can't see the console", "Same network; DHCP on both; firewall; VM network bridged"],
        ["USB stick not recognised", "Reformat MS-DOS (FAT), Master Boot Record; eject properly"],
        ["Wrong colour stays after a look", "LTP: an earlier memory still owns colour. O (All Cues Off), then replay. R13.1 releases should prevent this — check the release cue in that QLab group"],
        ["QLab cue does nothing", "Remote trigger added? Port 8000; Mantra IP 2.0.0.1; MANTRA patch interface = wired Ethernet"],
        ["Two looks stacking", "A release message missing or fired too early — look in the QLab group for `MANTRA RELEASE`"],
        ["Fixture ignores the console", "Address/mode mismatch, termination, or fixture in stand-alone mode (Part C)"]],
        [48 * mm, 122 * mm], bold_first=True))
    d.add(notes_area("Programming notes", 6))
    return d.build()
