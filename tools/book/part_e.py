"""Part E — QLab 5 Programming Guide for TLM_Show_R13_1.qlab5."""
import os

from core import *  # noqa: F401,F403
import show as S_


def build_sheet():
    rows, tints = [], []
    for c in S_.CUES:
        aud = "<br/>".join(md(a) for a, _ in c["audio"]) or "—"
        vid = " ".join(c["video"]) or ""
        lx = " · ".join("P%d M%d c%d%s" % (x["p"], x["m"], x["c"], (" +%gs" % x["pre"]) if x["pre"] else "")
                        for x in c["lx"])
        if c["fx5"]:
            lx += " · " + " ".join("P5 M%d %s" % (x["m"], "on" if x["lvl"] else "off") for x in c["fx5"])
        rel = ", ".join("P%d M%d" % (p, m) for p, m, *_ in c["release"])
        rows.append(["**%s**" % c["num"], c["name"], Paragraph(aud, S["cell"]), vid, lx, rel])
        if c["critical"]:
            tints.append((len(rows) - 1, "crit"))
        if c["song"]:
            so = S_.SONG[c["song"]]
            rows.append(["**%s**" % so["num"], "%s (song group)" % so["title"],
                         Paragraph(md("TRACK " + so["file"]), S["cell"]), "",
                         "P4 M%d c1…c%d" % (so["mem"], len(so["sections"])),
                         ", ".join("P%d M%d" % (p, m) for p, m, *_ in so["release"])])
            tints.append((len(rows) - 1, "song"))
    return rows, tints


def build(path):
    d = PartDoc(path, "E", "QLab 5 Programming Guide",
                "The R13.1 workspace: settings, show folder, cue anatomy, the full build sheet, sound files and "
                "songs, critical sequences, emergency cues and routines.")
    d.add(title_block("PART E · %s · %s" % (REV, DATE), "QLab 5 Programming Guide",
                      "%s — audio, video and Mantra triggers in one GO" % S_.QLAB_NAME))
    d.add(stats([(str(S_.TOTAL_QLAB_CUES), "cues in the workspace"), (str(S_.N_MASTER), "master cue groups"),
                 ("10", "song groups, %d section GOs" % S_.N_SONG_SECTIONS), ("80", "media files · 99 targets"),
                 ("3", "emergency cues E1–E3")]))
    d.add(box("rule", "HOW THE WORKSPACE WORKS",
              ["The workspace is already built: open `%s` from the show folder — no build script." % S_.QLAB_NAME,
               "Every lighting cue targets the split Mantra memories (P2/P3/P4). Flash returns are timed Network cues "
               "(0.2–1.0 s pre-wait). Each section/song change also releases the memory it leaves (Level=0). Q57 "
               "starts the HAYWIRE chase and **Q57b** restores Ariel. 58 audio cues play the SFX pack "
               "and the 9 supplied songs; Q19.2 plays a rain burst; songs fade and stop at Q9, Q15, Q15.5, Q19, "
               "Q41 and Q52. Media is found by its path inside the show folder."]))

    d.add(H1("1 Licence and Mac preparation"))
    d.add(table(["Need", "Unlicensed", "With any licence"], [
        ["Stereo playback to the StudioLive", "Yes (2 channels)", "Yes"],
        ["One projector, full screen", "Yes (1 single-output stage)", "Yes"],
        ["Stream Deck controlling QLab", "Yes (OSC remote control)", "Yes"],
        ["QLab firing the Mantra (Network cues)", "**No**", "Yes"]], [70 * mm, 50 * mm, 50 * mm]))
    d.add(box("rec", "R-21 · LICENCE", "The R13.1 show relies on QLab firing every lighting cue, so a licence is "
              "required. Rent the cheapest licence (Rent-to-Own, by calendar day) for cue-to-cue, dress and show "
              "days. Without it, run lighting from the Mantra scene memories (Part D §5)."))
    d.add(checklist(["Dedicated macOS user for the show", "Sleep, display sleep, screen saver off",
                     "Focus / Do Not Disturb on", "Automatic updates off for the production",
                     "Wi-Fi and Bluetooth off in show (Ethernet only)", "Charger connected",
                     "Audio sample rate matches the StudioLive (48 kHz)", "Projector a separate display (not mirrored)"],
                    cols=2))

    d.add(H1("2 The show folder"))
    d.add(P("Put the whole folder, named exactly **%s**, on the Desktop of the show Mac "
            "(`/Users/zmorgan/Desktop/%s/`). QLab finds every file by its path inside it." % (S_.FOLDER, S_.FOLDER)))
    d.add(table(["Item", "What it is"], [
        [S_.QLAB_NAME, "The show — open this one"],
        [S_.MTR_NAME, "Mantra show file (Part D)"],
        ["media/audio/01_Music_Songs", "S01–S10 song tracks (S07 still to choose)"],
        ["media/audio/02–08 …", "House/interval music, underscore, ambience beds, storm, magic, stings, voice"],
        ["media/video · media/stills", "BG backdrops (Part I) and VID-99 black"],
        ["R13_MEDIA_MANIFEST.csv", "The 80 media files the workspace uses, by relative path"],
        ["R13_1_SFX_RETARGET_MAP.csv", "Which new SFX file plays on which cue"],
        ["R13_MANTRA_SECTION_MAP.csv/.txt", "Which QLab cue fires each Mantra cue"],
        ["R13_1_QLAB_AND_DESK_FIX_LIST.csv", "Done / still to do"],
        ["docs/", "Cue sheets, Mantra labels, FOH notice, review and fix list"]],
        [60 * mm, 110 * mm]))
    d.add(P("To assemble the folder from the Drive zips use `ASSEMBLE_R13_1.command` from the R13.1 package "
            "(it checks all 80 media paths and the file checksums)."))

    d.add(H1("3 Workspace settings"))
    d.add(table(["Setting", "Where", "R13.1"], [
        ["Audio output patch", "Workspace Settings › Audio", "**TO DO on the show Mac:** Patch 1 → StudioLive USB (outs 1–2 → desk ch 11–12)"],
        ["Video stage", "Workspace Settings › Video", "**TO DO:** Stage 1 → projector output (not the built-in display)"],
        ["Network patch MANTRA", "Workspace Settings › Network", "Already set: OSC/UDP 2.0.0.1 port 8000. **TO DO:** interface → wired Ethernet"],
        ["OSC access (Stream Deck)", "Workspace Settings › Network › OSC Access", "Allow OSC connections, no passcode"],
        ["GO", "—", "Space bar; switch to Show Mode for performances"]],
        [36 * mm, 50 * mm, 84 * mm], bold_first=True))
    d.add(box("verify", "MACHINE-SPECIFIC", "Audio device, video screen and network interface depend on the show Mac's "
              "hardware, so they can't be set in the file. Set them once, then File › Save."))

    d.add(H1("4 Cue anatomy"))
    d.add(table(["Part", "How R13.1 builds it"], [
        ["Master cue group (1 … 65 + point cues)", "Group cue, all children start together. Number = master cue. Group Notes carry Trigger / LX / Sound / FX, shown to the operator."],
        ["Children", "SFX audio · VIDEO + 2 s FADE IN · FADE OUT of the previous picture · MANTRA network cue · FADE OUT of beds/songs · MANTRA RELEASE (Level=0) of the memory being left"],
        ["Flash return", "A second MANTRA cue in the same group with a pre-wait (0.2 / 0.3 / 1.0 s)"],
        ["Song group S1–S10", "'Start first child and go into the group': S#.0 TRACK auto-continues into the release and S#.1; S#.2 … are one GO each on the music"],
        ["Song fade-and-stop", "At the next scene cue: 3 s fade on the track, stop when done, release the song memory"],
        ["Emergency E1–E3", "Below cue 66 END OF SHOW: Panic, VID-99 black, SAFE LIGHT"]],
        [48 * mm, 122 * mm], bold_first=True))
    d.add(box("rule", "ONE GO FIRES EVERYTHING", "Each GO fires light, sound and video together, and each Mantra "
              "message names the exact page, memory and cue — the desk can never drift out of step. One operator runs "
              "the show from QLab; the Mantra and StudioLive sit beside the Mac as the manual fallback."))

    d.add(H1("5 Build sheet — every cue"))
    d.add(P("Read from the workspace. Mantra = page/memory/cue fired (with the flash-return pre-wait); Release = "
            "memory sent Level=0. Tinted = critical; blue = song group."))
    rows, tints = build_sheet()
    d.add(table(["Q", "Cue", "Audio", "Video", "Mantra", "Release"], rows,
                [11 * mm, 33 * mm, 48 * mm, 14 * mm, 42 * mm, 22 * mm], tints=tints))

    d.add(H1("6 Sound and music files"))
    d.add(H2("Songs"))
    d.add(table(["Song", "At", "File in 01_Music_Songs", "Track", "Status"],
                [["**%s** %s" % (s["num"], s["title"]), "Q" + s["at"], s["file"], s["track_kind"], s["status"]]
                 for s in S_.SONGS], [40 * mm, 12 * mm, 52 * mm, 34 * mm, 32 * mm],
                tints=[(i, "crit") for i, s in enumerate(S_.SONGS) if s["status"] != "supplied"]))
    d.add(H2("Sound effects (R13.1 SFX pack)"))
    rows = [[r["QLab_cues"], os.path.basename(r["New_file"]), r["Duration_s"] + " s", r["Loop_in_QLab"],
             r["Built_from"], r["In QLab R13.1"]] for r in S_.SFX_MAP]
    d.add(table(["Cue(s)", "File", "Length", "Loop", "Built from", "Status"], rows,
                [22 * mm, 52 * mm, 13 * mm, 17 * mm, 50 * mm, 16 * mm]))
    d.add(box("verify", "STILL SILENT PLACEHOLDERS", "S07 jellyfish song, Q1 house music, Q2 preshow, Q11 soft "
              "resolve, Q37 end of Act One, Q38 interval, Q42.5 Ariel's recorded line, Q43 cue-card underscore, Q59 "
              "land ambience, Q65 exit music. Their lengths already match the cues, so a real file drops straight in."))
    d.add(box("verify", "STARTING LEVELS — SET FINAL LEVELS AT TECH", "Every sound has a starting level on its cue: "
              "songs and Ariel's recorded line 0 dB · thunder cracks and the transformation impact −3 dB · stings, magic, "
              "palace intro, chase music and house/interval music −6 dB · storm wind/rain loops and the rain burst −9 dB · "
              "cue-card underscore −12 dB · ambience beds −15 dB · Q41 underscore −18 dB. The FADE TO cues keep the same "
              "drop from those levels (Q3 −16 dB, Q46 and Q51 −27 dB). House, preshow, end-of-act, interval and exit "
              "music loop until faded. Q19's wind/rain bed is disarmed so the rain lands on Q19.2."))
    d.add(box("rule", "SWAPPING AUDIO — ALWAYS A NEW FILE NAME", "Save the new file under a new name (e.g. "
              "`S02 Feeling Good (backing).mp3`), drag it onto the cue, and check the cue's end time. Replacing a file "
              "under the same name keeps the old end time in QLab."))

    d.add(H1("7 Critical sequences"))
    d.add(table(["Sequence", "QLab", "Mantra"], [
        ["Storm Q20–27", "Q20 wind/rain loop + BG-07; Q21/23/25 crack + thunder; Q22 creaks; Q24 groan + water; Q26 splash + low bed (90 s), fades out Q25 and takes Q22 to −21 dB; Q22 fades out Q20; Q27 fades the rest over 2.5 s, BG-21", "P2 M3 cues 4–14; flashes 5/8/11 return +0.2 s"],
        ["Transformation Q33–36", "Q33 magic build + BG-09; Q34 swell; Q35 impact; Q36 shell voice", "P2 M5 cues 3–7; flash 5 returns +0.3 s"],
        ["Voice transfer Q52–57b", "Q52 shell magic + BG-09; Q53–56 transfer sting ×4; Q57 haywire SFX; Q57b restore SFX", "P3 M3 cues 3–10; HAYWIRE P5 M5 on at Q57, off at Q57b; 57c +0.3 s"],
        ["Jellyfish Q45–49", "Q45 comic bed (fades to −27 dB at Q46); S7 chorus; Q47 sting", "P3 M2; Q47 pulse returns +1 s"],
        ["Cue cards Q43", "Cue-card underscore (placeholder — choose music)", "P3 M1 cue 6"]],
        [32 * mm, 88 * mm, 50 * mm], bold_first=True))
    d.add(P("Actor-paced cues (voice transfer, jellyfish repeats) are GO only when the actor is on the mark. If a "
            "lightning or magic GO is missed, skip it — never fire two late."))

    d.add(H1("8 Emergency cues and Stream Deck"))
    d.add(table(["Cue", "Does", "Stream Deck key"], [
        ["E1 STOP ALL", "Panic all QLab cues (lighting holds)", "F15 — give E1 a Hotkey trigger"],
        ["E2 VID-99 BLACK", "Black frame on the projector stage (also AV-mute)", "F13 — give E2 a Hotkey trigger"],
        ["E3 SAFE LIGHT", "Mantra P2 M10 over 2 s", "F14 — give E3 a Hotkey trigger"]],
        [36 * mm, 80 * mm, 54 * mm], bold_first=True))
    d.add(box("verify", "HOTKEYS ARE NOT SET IN THE FILE", "The R13.1 workspace has no hotkeys on E1–E3. Select each "
              "cue › Inspector › Triggers › Hotkey and press F15 / F13 / F14, then save (Part L)."))

    d.add(H1("9 Rehearsal, show and backup routine"))
    d.add(checklist(["Open the LIVE workspace from the Desktop show folder", "No red (broken) cues",
                     "Test tone reaches StudioLive ch 11–12", "Projector stage on the right display; E2 black works",
                     "E3 SAFE LIGHT: the desk responds", "Stream Deck keys respond", "Playhead on Q1; Show Mode on",
                     "Save after every session; dated copy of the whole folder", "One copy on a USB SSD, one on a second Mac",
                     "Emergency playback device loaded with the songs (R-08)"], cols=2))
    d.add(table(["Problem", "Check"], [
        ["No sound at the desk", "Audio patch device; outputs 1–2; StudioLive channel source = USB"],
        ["Video on the laptop screen", "Stage 1 assigned to the wrong display; displays mirrored"],
        ["Mantra doesn't respond", "Licence; MANTRA patch interface = wired Ethernet; OSC trigger on the desk; port 8000"],
        ["Media shows red / missing", "Check the show folder name and that it sits on the Desktop"],
        ["A cue plays the wrong length", "Audio was replaced under the same name — use a new name and re-drag"]],
        [48 * mm, 122 * mm], bold_first=True))
    d.add(notes_area("QLab notes", 6))
    return d.build()
