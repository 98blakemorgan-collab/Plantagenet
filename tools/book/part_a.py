"""Part A — Master Technical Production Manual (R13.1)."""
import os

from core import *  # noqa: F401,F403
import show as S_
import calls
from part_i import thumb

RECS = [
    ("R-01", "High", "Script", "Scene Eleven is in the contents but not the text; confirm with director/licensor", "SM / Director", "§12"),
    ("R-02", "High", "Lighting", "Use the venue's 12 Lightsky profiles for face light and specials", "LX / TD", "§6"),
    ("R-03", "High", "Show control", "One cue language across every system (QLab number = master cue; desk names carry it)", "SM / all ops", "§7"),
    ("R-04", "High", "Safety", "Flash, haze and loud-effect warnings; single hits only, ≤3 flashes/s — FOH notice supplied", "TD / FOH", "§10"),
    ("R-05", "High", "Electrical", "RCD protection and test-and-tag for all show power", "TD / venue", "§5"),
    ("R-06", "High", "Audio", "Wireless mic frequencies legal and coordinated", "Sound op", "§8"),
    ("R-07", "High", "QLab", "Harden the show Mac", "QLab op", "§7"),
    ("R-08", "High", "Redundancy", "Emergency playback rig on StudioLive ch 13–14", "Sound / QLab op", "§16"),
    ("R-09", "Medium", "Audio", "Wireless count 8 + 1 spare minimum", "Sound / producer", "§8"),
    ("R-10", "Medium", "Lighting", "Keep the venue's two-universe patch", "LX", "§6"),
    ("R-11", "Medium", "Projection", "Projector centre stage towards the back: throw, shadows, signal", "Projection", "§9"),
    ("R-12", "Medium", "Stage", "Make blackout scene changes safe", "SM / deck", "§11"),
    ("R-13", "Medium", "Haze", "Written haze plan with the venue", "TD / venue", "§10"),
    ("R-14", "Medium", "Rigging", "Secondary safety on the mirror ball", "Venue / TD", "§10"),
    ("R-15", "Medium", "Rehearsal", "Paper tech and dry tech", "SM / TD", "§14"),
    ("R-16", "Medium", "Comms", "Two-channel headset plan", "SM / TD", "§2"),
    ("R-17", "Medium", "Network", "Fixed 2.0.0.x addresses on one wired show network", "TD", "§3"),
    ("R-18", "Medium", "Crew", "Name a Deck/ASM and a FOH manager", "Producer", "§2"),
    ("R-19", "Low", "Audience", "Consider a relaxed performance", "Producer / Sound", "§8"),
    ("R-20", "Low", "Documentation", "Photograph each look at dress", "LX", "§6"),
    ("R-21", "High", "QLab", "Licence QLab — R13.1 fires every lighting cue from QLab", "Producer / QLab op", "§7"),
    ("R-22", "High", "Rigging", "Rate the projector bar and bond the projector", "Venue / TD", "§9"),
    ("R-23", "High", "Safety", "Water pistols are scripted to hit the audience", "Director / TD / FOH", "§11"),
    ("R-24", "High", "Rigging", "Two stage bars and side booms: loads, bases, wing space", "Venue / TD", "§4"),
    ("R-25", "Medium", "Lighting", "Turn the upstage bar away from the projection screen", "LX", "§4"),
    ("R-26", "High", "Rigging", "Floor booms in place of side trusses", "TD / producer", "§4"),
    ("R-27", "High", "Crew", "One show operator: keep the sound mix simple", "Producer / Sound", "§2"),
    ("R-28", "High", "Audio", "Supply the backing tracks (S2, S3, S5, check S4), the S7 song and the ten silent placeholders before dress", "MD / Sound", "§8"),
    ("R-29", "High", "Show control", "Set the show-Mac QLab settings (audio, video, network interface) and add the Mantra OSC trigger", "QLab op / LX", "§7"),
    ("R-30", "Medium", "Lighting", "Check the colour-forward looks from the house — faces, screen washout, bold backlight choices", "LX / Director", "§6"),
    ("R-31", "Medium", "Show control", "Agree who calls the 56 song-section GOs (DSM or QLab op to the music)", "SM / QLab op", "§12"),
]

MICS = [("1", "Ariel (Hayley)", "Headset/radio", "Lead vocal: Part of Your World, Time of My Life; offstage voice lines (Scene Eight)"),
        ("2", "Prince Evan (Jett)", "Headset/radio", "Sea Shanty, Time of My Life"),
        ("3", "Octavia (Hannah)", "Headset/radio", "Poor Unfortunate Souls; villain dialogue"),
        ("4", "Dame Beluga (Michelle)", "Headset/radio", "Feeling Good; audience interaction"),
        ("5", "Willis (Eliott)", "Headset/radio", "Sea Shanty"),
        ("6", "Flanders (Kelly)", "Headset/radio", "Comedy lead — watch peaks"),
        ("7", "Queen Marina (Lorraine)", "Headset/radio", "Dialogue; man's voice offstage at Q56"),
        ("8", "Theodore / Godfrey (Emma / Jeff)", "Radio, shared only if changes allow", "Mute the inactive performer"),
        ("9–10", "Area / overhead L/R", "Condensers", "Sailors (Grace, Aubrey, Isobelle) in the Sea Shanty; ensemble"),
        ("11–12", "QLab L/R", "USB return", "Playback, minimal processing"),
        ("13–14", "Emergency playback L/R", "Backup device (R-08)", "Muted; unmute only on SM call"),
        ("15–16", "Spare / Spirits", "Spare radio", "Candidate: Spirit of the Sea 1/2 (Kerry, Tracey) — key speeches at Q28, Q62")]


def cue_run():
    rows, tints = [], []
    interval = None
    for c in S_.CUES:
        strip = ""
        if c["lx"]:
            x = c["lx"][0]
            strip = swatch_strip(S_.position_summary(x["p"], x["m"], x["c"])[1], cell=3.4 * mm, h=3.6 * mm)
        pg = calls.GO_PAGE.get(c["num"], "")
        trig = c["trigger"].split(" (p")[0]
        media = []
        if c["video"]:
            media.append(" ".join(c["video"]))
        if c["audio"]:
            media.append("; ".join(a.replace(" [silent placeholder]", " (placeholder)") for a, _ in c["audio"]))
        rows.append(["**%s**" % c["num"], c["name"], trig, [P(c["look"], "cell")] + ([strip] if strip else []),
                     " · ".join(media) or "—", c["fx"], ("p " + pg) if pg and pg != "—" else ""])
        if c["critical"]:
            tints.append((len(rows) - 1, "crit"))
        if c["song"]:
            so = S_.SONG[c["song"]]
            rows.append(["**%s**" % so["num"], so["title"], "Straight after Q%s" % so["at"],
                         "P4 M%d · %d sections" % (so["mem"], len(so["sections"])), so["file"], so["status"], ""])
            tints.append((len(rows) - 1, "song"))
        if c["num"] == "38":
            interval = len(rows) - 1
    t = table(["Q", "Moment", "Trigger", "LX / Mantra", "QLab sound · video", "FX / note", "Page"], rows,
              [10 * mm, 25 * mm, 28 * mm, 30 * mm, 38 * mm, 28 * mm, 11 * mm], tints=tints)
    return t


def build(path):
    d = PartDoc(path, "A", "Master Technical Production Manual",
                "Production basis, systems, lighting, sound, projection, effects, the %d-cue show run, "
                "procedures, recommendations and worksheets — for the R13.1 show." % S_.N_MASTER)
    d.add(title_block("PLANTAGENET HALL · REVISION %s · %s" % (REV, DATE.upper()), "Master Technical Production Manual",
                      "Lighting · Sound · Projection · QLab · LSC Mantra · StudioLive · Haze · Stage management · Effects · Show control"))
    d.add(table(["System", "Project configuration"], [
        ["Production basis", "Licensed script, Nick Lawrence Pantomimes, revised April 2026 (55 pp as supplied); casting sheet 28 Sep 2026"],
        ["Venue", "Plantagenet Hall — installed LED rig, FOH truss, two stage bars, floor booms, projector and screen"],
        ["Lighting control", "LSC Mantra Lite + 2 wings · %s" % S_.MTR_NAME],
        ["Show control / media", "QLab 5 · %s — one GO fires light, sound and video" % S_.QLAB_NAME],
        ["Audio", "PreSonus StudioLive 16 · radio mics + QLab stereo return ch 11–12"],
        ["Effects", "Hazer #40, optional mirror ball + pinspots, water pistols where approved"]],
        [40 * mm, 130 * mm], bold_first=True))
    d.add(box("verify", "IMPORTANT STATUS", "A production planning, programming and operating manual. Fixture modes, "
              "rigging loads, power, projector throw, fire-alarm interaction and final stage dimensions must be verified "
              "on site. It is not a structural, rigging, electrical or fire-engineering certification."))

    d.add(H1("Document control"))
    d.add(table(["Item", "Detail"], [
        ["Revision", "%s" % REV],
        ["Date", DATE],
        ["Show files", "%s · %s · folder %s" % (S_.QLAB_NAME, S_.MTR_NAME, S_.FOLDER)],
        ["Companion parts", "B Lighting · C Patch · D Mantra · E QLab · F Cue sheets · G DSM script · H Props · I Projection · J Prompt copy · K Quick reference · L Stream Deck & tech test"]],
        [34 * mm, 136 * mm], bold_first=True))
    d.add(H2("The show at a glance"))
    d.add(bullets([
        "**Show control:** the Mantra show is split — P2 Act One scenes, P3 Act Two scenes, P4 songs, P5 FX, "
        "P6–P7 look library, P8 the full 153-position backup. QLab targets the exact memory and cue for every step.",
        "**Colour-forward lighting:** strong LX1 colour, side light, LX2 backlight and PixBar movement over neutral faces; "
        "fast colour snaps on musical impacts; no strobe (Part B).",
        "**Songs:** ten song memories (S1–S10) with %d section cues; nine tracks supplied (S2, S3, S5 still vocal versions; S7 "
        "to choose)." % S_.N_SONG_SECTIONS,
        "**Timing:** flash returns are fired by QLab (no desk link times), memory releases stop looks stacking, HAYWIRE runs "
        "from Q57 to Q57b, Q19.2 is the rain burst, and songs fade and stop on the next scene cue.",
        "**Projection:** 21 backdrops in the cue plan, matched to the script's cyclorama calls, seamless 15–16 s loops (Part I).",
        "**Script:** paged to the licensed script (revised April 2026, 55 pp); the contents list a Scene Eleven that has no text (R-01).",
        "**Casting:** microphone plan and beginners built from the casting sheet (§8)."]))
    d.add(P("Key: teal boxes = recommendations (R-xx), coral = verify on site / safety, navy = operating rules, yellow = to action before tech.", "muted"))

    d.add(H1("R Recommendations register"))
    d.add(stats([(str(len([r for r in RECS if r[1] == "High"])), "high priority"),
                 (str(len([r for r in RECS if r[1] == "Medium"])), "medium priority"),
                 (str(len([r for r in RECS if r[1] == "Low"])), "low priority"),
                 ("4", "to action before tech (R-28 to R-31)")]))
    d.add(table(["ID", "Priority", "Area", "Recommendation", "Owner", "Ref", "Done"],
                [[r[0], r[1], r[2], r[3], r[4], r[5], "☐"] for r in RECS],
                [13 * mm, 15 * mm, 22 * mm, 70 * mm, 27 * mm, 11 * mm, 12 * mm],
                tints=[(i, "new") for i, r in enumerate(RECS) if r[0] in ("R-28", "R-29", "R-30", "R-31")]))

    d.add(H1("1 Production basis and technical philosophy"))
    d.add(P("Fixed lighting and reliable local fallback rather than moving-head dependence or fragile automation. "
            "The projector gives scenery and motion, the fixed rig lights performers, QLab plays media and fires the "
            "Mantra, the StudioLive mixes microphones. Haze and the mirror ball are selective effects."))
    d.add(table(["Requirement", "Technical response"], [
        ["No moving heads", "Zone washes and pre-focused specials; crossfade specials to suggest movement (voice transfer)"],
        ["Projection screen", "Front/key beams kept off the screen; projection for environment, lighting for performers"],
        ["Colour-forward design", "Energy from LX1, side, back and PixBars; FOH faces stay near-white"],
        ["One show operator", "QLab GO fires light, sound and video together; Mantra and StudioLive beside the Mac as fallback"],
        ["Haze", "Short, controlled bursts for underwater, storm, magic and lair; clear air for dialogue"]],
        [48 * mm, 122 * mm], bold_first=True))
    d.add(box("rule", "OPERATING PRINCIPLES", ["1 Actor-paced cues are manual GOs — never hard-timed to a line.",
          "2 Mantra is the lighting master: the show must stay runnable from the desk (P2/P3/P4 memories).",
          "3 StudioLive is the live-audio master; QLab playback is separate from live mics.",
          "4 Projection is enhancement: every scene must read with lighting alone.",
          "5 Safety and visibility first: stop water, haze or flash effects if conditions become unsafe.",
          "6 The same cue numbers in the prompt book and every operator sheet (R-03)."]))

    d.add(H1("2 Crew structure and communications"))
    d.add(table(["Role", "Responsibility", "Comms"], [
        ["Technical Director", "Integration, safety sign-off, patch, backups, technical decisions", "B"],
        ["Stage Manager (DSM)", "Prompt book (Part J), standbys/GOs (Part G), scene changes, emergency calls", "A + B"],
        ["Show operator (QLab + desks)", "GO in QLab (fires light, sound, video); Mantra and StudioLive fallback", "A"],
        ["Sound (if separate)", "StudioLive mix, radio mics, spare-mic response", "A"],
        ["Haze / FX", "Haze and effects on cue, within venue rules", "A"],
        ["Deck / ASM", "Props, tabs, water, shell/plinth, jellyfish, drying and resets (R-18)", "B"],
        ["FOH manager", "Audience safety, house-light moments (Q13, Q64), sensory warnings (R-04)", "B / phone"]],
        [40 * mm, 110 * mm, 20 * mm], bold_first=True))
    d.add(table(["Call", "Meaning"], [
        ["STANDBY", "Operator prepares the cue and confirms (“QLab standing by”)"], ["GO", "Execute the called cue now"],
        ["HOLD", "Do not execute; keep the current safe state"], ["GO LX ONLY / GO SOUND ONLY", "Execute that part only"],
        ["STOP PLAYBACK", "Stop QLab playback without muting live mics"]], [48 * mm, 122 * mm], bold_first=True))
    d.add(box("rec", "R-16 · R-18 · R-27", "Channel A carries show calls, Channel B tech/backstage. Name a Deck/ASM and a FOH "
              "manager. With one show operator, keep the sound mix simple: principals on one DCA, playback on another."))

    d.add(H1("3 System architecture, signal flow and network"))
    d.add(table(["From", "To", "Connection / purpose"], [
        ["QLab Mac", "Mantra Lite (2.0.0.1)", "OSC /PlayMemory over UDP port 8000 — every lighting cue, releases, flash returns"],
        ["QLab Mac", "StudioLive ch 11–12", "Stereo playback return (USB)"],
        ["QLab Mac", "Projector", "HDMI via HDBaseT/active cable to centre stage — backdrops and VID-99 black"],
        ["Stream Deck", "QLab Mac", "USB — GO, Panic, E1–E3 hotkeys"],
        ["Mantra", "Fixtures", "U1 DMX from the desk XLR · U2 Art-Net/sACN to a node (2.0.0.10) for the C42s"],
        ["StudioLive", "PA / monitors", "Main L/R, Aux 1–2"]], [30 * mm, 38 * mm, 102 * mm]))
    d.add(table(["Device", "Address", "Notes"], [
        ["Mantra Lite", "2.0.0.1", "In the show file; Art-Net + sACN on (turn off the unused one)"],
        ["Art-Net/sACN node", "2.0.0.10", "Universe 2"], ["QLab Mac", "2.0.0.20", "Manual IPv4, Wi-Fi off"],
        ["Backup Mac", "2.0.0.21", "Optional"], ["StudioLive (UC Surface)", "2.0.0.30", "Optional"],
        ["Tablet / remote", "2.0.0.40", "Optional"]], [40 * mm, 30 * mm, 100 * mm]))
    d.add(box("rule", "FALLBACK HIERARCHY", "Network fails: run lighting from the Mantra P2/P3/P4 memories. QLab fails: live "
              "mics stay on the StudioLive, lighting from the desk, songs from emergency playback (R-08). Projection fails: "
              "continue on lighting. One failure never stops the show on its own."))

    d.add(H1("4 Venue, stage and lighting layout"))
    d.add(P("The venue's own rig as patched: 12 Lightsky 8800-C42 profiles (#1–12), 10 Tour Pro Zooms (#13–22), 11 TourCOB "
            "PARs (#23–32, 39), 6 PixBars (#33–38) and the hazer (#40). FOH truss #1–8; LX1 #9–18; LX2 #19–20, 23–28, 33–39; "
            "SR boom #21, 29, 30; SL boom #22, 31, 32. The projector hangs centre stage towards the back and throws upstage. "
            "Rig plan, positions and focus: Part B §1 and §7; Quick Reference card 1."))
    d.add(box("rec", "R-24 · R-25 · R-26", "Confirm bar loads, boom bases and wing space. Turn LX2 away from the screen — the show runs "
              "the backlight hard. Use a weighted floor boom in each wing (no side trusses)."))

    d.add(H1("5 Power, data, cable and rigging"))
    d.add(table(["System", "Arrangement", "Pre-show check"], [
        ["Lighting power", "Venue lighting circuits, RCD-protected", "Circuit ID, connectors, strain relief"],
        ["Audio power", "Same phase/earth where possible", "Hum, overload, chargers"],
        ["Projector", "Dedicated outlet", "Warm-up, ventilation, signal, bond"],
        ["Haze", "Supply to rating and venue policy", "Fluid, detector isolation logged"],
        ["Show network", "Unmanaged switch, labelled Cat6", "Link lights, addresses"],
        ["Compliance", "In-date test-and-tag (AS/NZS 3760)", "Untagged items quarantined"]], [30 * mm, 70 * mm, 70 * mm]))
    d.add(P("Keep water trajectories 2 m from joins, floor boxes, the projector and FOH control. Terminate every DMX line; "
            "never Y-split DMX. Rigging, loads and permanent wiring are for the venue or a qualified person (R-05)."))

    d.add(H1("6 Lighting system and LSC Mantra"))
    d.add(P("Full design in Part B and programming in Part D. The R13.1 show file holds:"))
    d.add(table(["Page", "Contents"], [[r[0], "%s — %s" % (r[1], r[2])] for r in __import__("part_d").PAGEMAP],
                [14 * mm, 156 * mm]))
    d.add(H2("Look library as programmed"))
    d.add(swatch_legend())
    d.add(table(["Look", "Desk", "Layers", "As programmed"],
                [["**%s**" % L["name"], "P%d M%d" % (L["page"], L["mem"]), swatch_strip(L["summary"]), describe(L["summary"])]
                 for L in S_.LOOKS], [30 * mm, 14 * mm, 57 * mm, 69 * mm]))
    d.add(box("rec", "R-30", "The looks are deliberately bold. At the focus session check every look from the house: "
              "faces readable, screen not washed out, and bold choices (e.g. coral-red backlight in M03 UNDERWATER) agreed with "
              "the director. Photograph each look at dress (R-20)."))
    d.add(table(["Before the show", "During the show", "If something goes wrong"], [[
        "Load the show; fire E3 SAFE LIGHT and one cue per memory from QLab",
        "Single operator: GO in QLab on the SM's call fires the lighting",
        "QLab/network down: run the matching P2/P3/P4 memory with Next Cue; press Next Cue again after each flash. "
        "Emergency: SAFE LIGHT P2 M10. Never replay a missed flash."]], [56 * mm, 56 * mm, 58 * mm]))

    d.add(H1("7 QLab programming and show control"))
    d.add(P("Full guide in Part E. The workspace is already built: %d cues — %d master cue groups, 10 song groups and "
            "E1–E3. Cue number = master cue number; Mantra desk cues carry the same number in their names (R-03)."
            % (S_.TOTAL_QLAB_CUES, S_.N_MASTER)))
    d.add(checklist(["Dedicated show user; sleep, screen saver, notifications, updates off", "Wi-Fi and Bluetooth off",
                     "Show folder on the Desktop with its exact name", "Licence active (R-21)",
                     "Audio patch → StudioLive, video stage → projector, network interface → Ethernet (R-29)",
                     "Mantra OSC Play Memory trigger on port 8000 (R-29)", "E1–E3 hotkeys F15/F13/F14",
                     "Show Mode for every performance"], cols=2))
    d.add(box("rec", "R-21 · R-29", "R13.1 fires every lighting cue from QLab, so the licence is essential. The audio device, "
              "video screen and network interface can't be stored in the file — set them on the show Mac, and add the OSC "
              "remote trigger on the desk."))

    d.add(H1("8 Sound system and StudioLive"))
    d.add(H2("Input plan (from the casting sheet)"))
    d.add(table(["Ch", "Source", "Method", "Notes"], [list(m) for m in MICS], [14 * mm, 48 * mm, 40 * mm, 68 * mm]))
    d.add(H2("Who sings what (casting sheet)"))
    d.add(table(["Role", "Actor", "Sings", "Dances"], [list(r) for r in calls.CASTING],
                [52 * mm, 18 * mm, 42 * mm, 58 * mm]))
    d.add(H2("Music — the ten songs"))
    d.add(table(["Song", "At", "Performed by", "Track", "Status"],
                [["**%s** %s" % (s["num"], s["title"]), "Q" + s["at"], s["credit"].split(" - ")[-1] if False else s["mus"],
                  s["track_kind"], s["status"]] for s in S_.SONGS], [50 * mm, 12 * mm, 26 * mm, 42 * mm, 40 * mm],
                tints=[(i, "crit") for i, s in enumerate(S_.SONGS) if s["status"] != "supplied"]))
    d.add(box("rec", "R-28", "Before dress: backing tracks for S2 Feeling Good, S3 Part of Your World and S5 Time of My "
              "Life (and S4 if the file has vocals); choose the S7 jellyfish chorus; supply house/preshow, end of Act One, "
              "interval and exit music (Q1, Q2, Q37, Q38, Q65), Ariel's recorded line (Q42.5), the cue-card underscore (Q43), "
              "the soft resolve (Q11) and land ambience (Q59). Save each under a NEW file name and drag it onto the cue."))
    d.add(H2("Sound effects"))
    d.add(P("38 *_v2 files built from the 40-sound SFX pack, plus Q19.2 rain burst and Q57.5 voice-restore resolve. Beds "
            "loop (Q4, Q20, Q22, Q31, Q45, Q50, Q60); Q25 runs 60 s and Q26 90 s. Full map: Part E §6."))
    d.add(box("rec", "R-06 · R-09 · R-19", "Legal, coordinated wireless frequencies (no 694–820 MHz). 8 radio packs + 1 spare; "
              "consider packs for the two Spirits. Check levels with an SPL meter for a family audience."))

    d.add(H1("9 Projection and media"))
    d.add(P("The backdrops in the cue plan (Part I). Each picture change is a 2 s crossfade in the same GO as its light "
            "and sound; blackouts fade to black (plus projector AV-mute)."))
    story = []
    items = [("Q4", "BG-02"), ("Q8", "BG-22"), ("Q20", "BG-07"), ("Q27", "BG-21"), ("Q39", "BG-18"), ("Q40", "BG-23"),
             ("Q50", "BG-19"), ("Q60", "BG-20"), ("Q64", "BG-26")]
    cells = [[picture(thumb(bg), 52 * mm), P("**%s · %s** %s" % (q, bg, __import__("part_i").BACKDROPS[bg][0]), "small")]
             for q, bg in items]
    g = Table([cells[i:i + 3] for i in range(0, 9, 3)], colWidths=[56.6 * mm] * 3)
    g.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 1)]))
    d.add(g)
    d.add(box("rec", "R-11 · R-22", "Confirm throw and screen fill, treat the strip between projector and screen as a shadow "
              "zone, run HDBaseT or active HDMI from FOH, and rate the bar and bond the projector."))

    d.add(H1("10 Haze, mirror ball and atmosphere"))
    d.add(table(["Cue", "When", "Action", "Master cue"], [
        ["HZ-01", "Before opening", "Short burst", "03–04"], ["HZ-02", "Opening / underwater", "Low haze", "04–08"],
        ["HZ-03", "Before clear comedy", "Stop / clear", "09"], ["HZ-04", "Storm standby", "Short burst", "20"],
        ["HZ-05", "Storm peak", "Controlled burst", "25"], ["HZ-06", "Storm end", "OFF", "27"],
        ["HZ-07", "Magic standby", "Short burst", "33–34"], ["HZ-08", "Octavia's lair", "Low haze", "50"],
        ["HZ-09", "Voice transfer", "Reduce / OFF", "57"], ["HZ-10", "Finale (optional)", "Low only", "63"]],
        [16 * mm, 50 * mm, 50 * mm, 54 * mm]))
    d.add(P("Haze = hazer #40 on Mantra **P5 M4** (50 % output, fan 50 %), run on its fader 20–40 s before the look. Mirror "
            "ball only with a rated motor and bond (R-14); pinspots #41–42 if used."))
    d.add(box("verify", "R-04 · FLASH AND HAZE NOTICE", "Single white hits only (Q21, Q23, Q25, Q35, Q57b), never above 3 a "
              "second. Post the printed notice (docs/FOH_Flashing_Lights_and_Haze_Notice.pdf) at the doors and add a line "
              "to the programme. Written haze plan with the venue (R-13)."))

    d.add(H1("11 Stage, props and practical effects"))
    d.add(P("Props list and presets: Part H. Water pistols at Q19.2 and Q58 spray the audience (R-23): clean water, small "
            "amounts, below head height, away from electronics and hearing aids, warning before the show."))
    d.add(table(["Cue", "Change", "Controls (R-12)"], [
        ["17", "Scene Two → Ship", "Glow-tape marks; crew in blacks; SM confirms clear before Q18"],
        ["37", "Act One end", "Tabs close first; house up only after the stage is clear"],
        ["44", "Palace → Jellyfish", "Cue cards struck; jellyfish preset"],
        ["49", "Jellyfish → Lair", "Shell plinth onto the SP4 glow mark; HZ-08 standby"],
        ["58.5", "Lair → Dry land", "Towels, dry, strike plinth"]], [14 * mm, 40 * mm, 116 * mm]))

    d.add(H1("12 Master cue run — %d cues + 10 songs" % S_.N_MASTER))
    d.add(P("One shared sequence for the prompt book and all operators, read from the R13.1 workspace. Page = GO page in the "
            "licensed script as supplied. Tinted = critical; blue = song (its section GOs follow the music)."))
    d.add(swatch_legend(), cue_run())
    d.add(box("rec", "R-01 · R-31", ["The contents page lists “Scene Eleven: On the Shore” but the text runs Scene Ten (pp 51–54) "
              "straight to Scene Twelve (p 55); the Scene Five song listed on p 33 is also missing. Confirm with the director and "
              "licensor before cue lock.", "Agree at the paper tech whether the DSM or the QLab operator calls the song-section GOs."]))

    d.add(H1("13 Critical-sequence cards"))
    d.add(table(["Sequence", "Step", "Lighting (Mantra)", "Sound / video (QLab)", "Haze / practical"], [
        ["Storm Q20–27", "20", "P2 M3 c4 M08 storm", "Wind/rain loop · BG-07", "HZ-04 burst"],
        ["", "21 / 23 / 25", "White hit → return +0.2 s", "Crack + thunder", "Short flash only"],
        ["", "22 / 24", "Storm build / ship lurch", "Creaks · groan + water", "Water only if approved"],
        ["", "26 / 27", "Low tail → shore", "Splash + bed · storm layers out · BG-21", "HZ-06 off; dry stage"],
        ["Transformation Q33–36", "33 → 36", "M10 build · white hit → 35b (+0.3 s) · SP1 → SP4", "Magic build · impact · shell voice · BG-09", "HZ-07"],
        ["Voice transfer Q52–57b", "52 → 56", "Shell → V1 → V2 → V3 → V4 (0.3 s)", "Shell magic · transfer sting ×4", "Actors on marks"],
        ["", "57 / 57b", "HAYWIRE chase on · restore hit, chase off, SP1 (+0.3 s)", "Haywire SFX · restore resolve", "HZ-09 reduce/off"],
        ["Jellyfish Q45–49", "45 → 47", "M13 · pulse → return +1 s · repeats on P5 M6", "Comic bed · S7 chorus · sting", "Performer sightline"]],
        [30 * mm, 18 * mm, 48 * mm, 46 * mm, 28 * mm], bold_first=True))
    d.add(box("rule", "RECOVERY", "Storm: stay in the storm and wait for the next action. Transformation: continue with the new "
              "state; never repeat the hit. Voice: go straight to the next correct special. HAYWIRE keeps running until Q57b fires."))

    d.add(H1("14 Rehearsal and technical week"))
    d.add(table(["Session", "Focus", "Result"], [
        ["Paper tech", "SM + operators walk all cues and song sections", "Every cue has a trigger, page and owner (R-15, R-31)"],
        ["Tech 1", "Hang, patch, focus", "All fixtures respond; specials focused; looks checked from the house (R-30)"],
        ["Tech 2", "QLab / projection", "Show-Mac settings set (R-29); every backdrop on the real screen"],
        ["Tech 3", "StudioLive / mics", "Casting-based mic plan; spare tested; scan done"],
        ["Dry tech", "Storm, transformation, voice transfer + HAYWIRE", "Timings proven with stand-ins"],
        ["Tech 4 / 5", "Cue-to-cue Act One / Act Two", "Flash returns, releases, song fades, Q57 → Q57b"],
        ["Wet tech", "Water + haze + projector", "Effects safe with final cable positions"],
        ["Dress 1–2", "Full runs", "Timing lock; photos of looks (R-20)"]], [26 * mm, 62 * mm, 82 * mm], bold_first=True))

    d.add(H1("15 Pre-show, interval and post-show"))
    d.add(table(["Time", "Action"], [
        ["T-90", "Power up in order (Quick Reference card 7); Mantra loads the Default Show"],
        ["T-80", "QLab Mac: open the show from the Desktop folder; no red cues; Stream Deck profile"],
        ["T-70", "E3 SAFE LIGHT → desk responds; test tone on ch 11–12; Q4 backdrop; E2 black"],
        ["T-60", "Storm, transformation, voice-transfer checks (low level, haze off)"],
        ["T-45", "Panic, O (All Cues Off), playhead on Q1, Show Mode; props, shell, cue cards, water preset"],
        ["T-30", "House open: SM calls Q1"]], [16 * mm, 154 * mm], bold_first=True))
    d.add(checklist(["Interval: dry water areas; refill pistols for Q58", "Interval: haze fluid; batteries", "Interval: QLab on Q39; desk ready on P3",
                     "Post-show: Panic, save, back up any change", "Post-show: projector cool-down", "Post-show: dry props, log faults"], cols=2))

    d.add(H1("16 Emergency, recovery and troubleshooting"))
    d.add(table(["Failure", "Immediate action", "Continue?"], [
        ["QLab freezes", "E1/Panic if possible; lighting from the desk memories; emergency playback ch 13–14 on SM call", "Yes"],
        ["QLab → Mantra link fails", "Run P2/P3/P4 memories with Next Cue (Next Cue again after each flash)", "Yes"],
        ["Looks stacking / wrong colour", "O (All Cues Off) then re-fire the current cue", "Yes"],
        ["Radio mic dies", "Mute the channel; spare pack at the next exit", "Yes"],
        ["Projector fails", "E2 black / AV-mute; continue on lighting", "Yes"],
        ["Water or haze unsafe", "Stop it; continue the dry version", "Yes"],
        ["Fire alarm / evacuation", "HOLD; house lights full; E1 stop; venue procedure", "Venue decides"]],
        [40 * mm, 100 * mm, 30 * mm], bold_first=True))
    d.add(table(["Recovery state", "Where"], [["SAFE LIGHT", "QLab E3 · Mantra P2 M10 (also P7 M7 = M17)"],
                                               ["Projector black", "QLab E2 · projector AV-mute"],
                                               ["Stop playback", "QLab E1 / Esc — live mics continue"],
                                               ["Emergency playback", "Backup device on StudioLive ch 13–14 (R-08)"]],
                [40 * mm, 130 * mm], bold_first=True))

    d.add(H1("17 Backup, version control and handover"))
    d.add(table(["Asset", "Method", "When"], [
        ["Show folder (%s)" % S_.FOLDER, "Dated copy of the whole folder on a USB SSD and a second Mac", "After every change session and at lock"],
        ["Mantra show", "Desk + USB export", "After patch, cue-to-cue and lock"],
        ["StudioLive scenes", "Save baseline scene TLM SHOW", "After sound lock"],
        ["Cue sheets / book", "PDF + printed copies", "After cue lock"]], [48 * mm, 82 * mm, 40 * mm]))
    d.add(P("Checksums of the checked QLab and Mantra files are in BUILD_METADATA.json. Only one copy is LIVE; record every "
            "post-lock change in the change log."))
    d.add(table(["Date/time", "System", "Change", "Reason", "Tested by", "Approved"], [[""] * 6 for _ in range(6)],
                [22 * mm, 22 * mm, 50 * mm, 36 * mm, 20 * mm, 20 * mm]))

    d.add(H1("18 Equipment checklist"))
    d.add(table(["Category", "Item", "Qty", "Status", "✓"], [
        ["Lighting", "LSC Mantra Lite + 2 wings", "1", "Venue", "☐"],
        ["Lighting", "Lightsky C42 / Zoom / TourCOB / PixBar / hazer", "12/10/11/6/1", "Venue — confirm #38 and #39 exist", "☐"],
        ["Rigging", "Floor booms SR + SL with bases, arms, bonds, sandbags", "2", "R-26", "☐"],
        ["Control", "Art-Net/sACN node, show switch, labelled Cat6", "1 each", "R-17", "☐"],
        ["Playback", "Mac with QLab 5 + licence", "1", "R-07, R-21", "☐"],
        ["Playback", "Emergency playback device", "1", "R-08", "☐"],
        ["Sound", "StudioLive 16, 8 radio packs + spare, area mics", "—", "R-06, R-09", "☐"],
        ["Projection", "Epson projector + HDBaseT", "1", "R-11, R-22", "☐"],
        ["Show control", "Stream Deck 15-key", "1", "Part L", "☐"],
        ["Safety", "Glow tape, running lights, towels, squeegee, non-slip mat", "—", "R-12", "☐"]],
        [24 * mm, 76 * mm, 20 * mm, 40 * mm, 10 * mm]))

    d.add(H1("19 Final technical sign-off"))
    d.add(checklist(["Licensed script and prompt copy confirmed", "Cue numbers locked in every system",
                     "Show-Mac QLab settings set (R-29)", "Mantra OSC trigger added", "SAFE LIGHT from QLab and desk",
                     "Every P2/P3/P4 memory fired from QLab", "Flash returns and Q57 → Q57b checked",
                     "Song fades and releases checked", "Backing tracks and placeholders replaced (R-28)",
                     "S7 jellyfish song chosen", "Backdrops checked on the real screen", "Looks checked from the house (R-30)",
                     "Wireless scanned; spare tested", "Emergency playback tested", "Water and haze rehearsed",
                     "FOH notice posted", "Test-and-tag / RCD confirmed", "All show files backed up"], cols=2))
    d.add(table(["Role", "Name", "Signature", "Date"], [[r, "", "", ""] for r in
                ["Technical Director", "Stage Manager", "Show operator", "Sound", "Deck / ASM", "Venue contact"]],
                [44 * mm, 50 * mm, 50 * mm, 26 * mm]))

    d.add(H1("Appendices — worksheets"))
    d.add(H2("A Focus and position worksheet"))
    d.add(table(["#", "Position", "Focus / mark", "Colour / level notes"], [["#%d" % n, p, "", ""] for n, _, p, _, _ in
                __import__("part_b").FOCUS if n <= 39], [12 * mm, 22 * mm, 68 * mm, 68 * mm]))
    d.add(H2("B Operator show report"))
    d.add(table(["Cue / time", "Department", "Issue", "Action taken", "Owner"], [[""] * 5 for _ in range(10)],
                [24 * mm, 26 * mm, 50 * mm, 46 * mm, 24 * mm]))
    d.add(H2("C Sources"))
    d.add(bullets(["Licensed script, Nick Lawrence Pantomimes, revised April 2026 (as supplied); casting sheet 28 Sep 2026.",
                   "R13.1 show files: %s, %s, section map, media manifest, SFX retarget map, fix list." % (S_.QLAB_NAME, S_.MTR_NAME),
                   "Show user guide, review and fix list, backdrop set BG-01–BG-26.",
                   "LSC Mantra Lite User Manual v3; Figure 53 QLab 5 documentation."]))
    d.add(notes_area("Technical notes", 8))
    return d.build()
