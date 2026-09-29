"""Part G — DSM Calling Script (R13.1)."""
from core import *  # noqa: F401,F403
import show as S_
from calls import SCENES

STBY = colors.HexColor("#fff9ec")
GO = colors.HexColor("#f1f9f1")


def scene_table(cues):
    data = [[Paragraph(md(h), S["head"]) for h in ("Q", "Page", "Standby at / GO on", "DSM calls", "Depts", "What happens")]]
    cmds = [("LINEABOVE", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 0), (-1, 0), 1.0, INK), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE), ("TOPPADDING", (0, 0), (-1, -1), 1.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6), ("LEFTPADDING", (0, 0), (-1, -1), 3)]
    for q, sp, sl, gp, gl, depts, what, note in cues:
        parts = [p.replace("QLAB", "QLab").replace("DECK", "Deck") for p in depts.split()]
        callname = ", ".join([parts[0] + " " + q] + parts[1:])
        songs = [s for s in S_.SONGS if s["at"] == q]
        r0 = len(data)
        crit = S_.CUE.get(q, {}).get("critical")
        data.append([Paragraph("<b>%s</b>" % q, S["cellb"]), Paragraph(md("p " + sp if sp != "—" else "—"), S["cell"]),
                     Paragraph(md(sl), S["cell"]), Paragraph(md("“Standby %s”" % callname), S["cell"]),
                     Paragraph(md(depts), S["cell"]), Paragraph(md(what + (("  —  **" + note + "**") if note else "")), S["cell"])])
        data.append(["", Paragraph(md("p " + gp if gp != "—" else "—"), S["cell"]), Paragraph(md(gl), S["cell"]),
                     Paragraph(md("“%s — GO”" % callname), S["cellb"]), "", ""])
        cmds += [("BACKGROUND", (0, r0), (-1, r0), STBY), ("BACKGROUND", (0, r0 + 1), (-1, r0 + 1), GO),
                 ("SPAN", (0, r0), (0, r0 + 1)), ("SPAN", (4, r0), (4, r0 + 1)), ("SPAN", (5, r0), (5, r0 + 1))]
        if crit:
            cmds.append(("LINEBEFORE", (0, r0), (0, r0 + 1), 3, CORAL))
        for so in songs:
            secs = so["sections"]
            data.append([Paragraph("<b>%s</b>" % so["num"], S["cellb"]), "", Paragraph(md(
                "Straight after Q%s: the track and %s start on the operator's GO" % (q, secs[0]["num"])), S["cell"]),
                Paragraph(md("“QLab %s — GO”, then section GOs to the music" % so["num"]), S["cell"]),
                Paragraph("QLab", S["cell"]),
                Paragraph(md("**%s** — %d GOs: %s" % (so["title"], len(secs), " · ".join(
                    "%s %s" % (s["num"], s["name"]) for s in secs))), S["cell"])])
            cmds.append(("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1), SONG))
    t = Table(data, colWidths=[11 * mm, 12 * mm, 50 * mm, 38 * mm, 17 * mm, 42 * mm], repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return t


def build(path):
    d = PartDoc(path, "G", "DSM Calling Script",
                "Every standby and GO placed on the licensed script pages, for all %d cues, the ten songs and the "
                "show-stop procedures." % S_.N_MASTER)
    d.add(title_block("PART G · %s · SCRIPT-LOCKED · %s" % (REV, DATE), "DSM Calling Script",
                      "The Little Mermaid by Nick Lawrence · Plantagenet Hall · one GO fires everything"))
    d.add(table(["Row", "Meaning"], [
        ["Amber", "Standby: give it on the page and words shown. Wait for every department to answer “Standing by”."],
        ["Green", "GO: say “GO” exactly on the words or action shown."],
        ["Blue", "Song: straight after its cue the QLab operator starts the song; section GOs follow the music (the DSM can delegate them)."],
        ["Coral edge", "Critical cue: flash, storm, water or transformation."],
        ["Pages", "Pages of the licensed script as supplied (Nick Lawrence Pantomimes, revised April 2026, 55 pp, “Page N of 55” footer). If your printed copy paginates differently, call on the words."]],
        [24 * mm, 146 * mm], bold_first=True))
    d.add(box("rule", "CALLS TO KNOW",
              ["**Q57b** — restore Ariel: called on Ariel's entrance after the haywire (Q57). It fires the white "
               "restore hit, stops the HAYWIRE chase and puts SP1 on Ariel.",
               "**Flash returns are automatic** (Q21, Q23, Q25, Q35, Q47, Q57b): call one GO per flash; the light comes "
               "back by itself.",
               "**Songs** each have section GOs (S1.2, S1.3 …). Agree at the paper tech whether the DSM calls them or "
               "the QLab operator takes them to the music.",
               "**Fades:** songs fade and stop on the next scene cue (Q9, Q15, Q15.5, Q19, Q41, Q52) — no separate call."]))
    d.add(box("rule", "ONE OPERATOR", "Call “Standby QLab 20” … “QLab 20 — GO” to the show operator, who presses GO; "
              "QLab fires the Mantra cue with the sound and video. If QLab fails the operator runs lighting from the "
              "matching Mantra scene memory (P2 Act One / P3 Act Two / P4 songs)."))

    d.add(H1("1 Pre-show, interval and end-of-show calls"))
    d.add(table(["When", "What the DSM says / does"], [
        ["Half-hour (35 min before)", "“Good evening company, this is your half-hour call. Half an hour, please. The house is not yet open.”"],
        ["House open (FOH confirms)", "“Company, the house is now open. Please keep the stage and wings clear and quiet.” · QLab 1 — house state, BG-01"],
        ["Quarter-hour (20 min)", "“Company, this is your quarter-hour call. Fifteen minutes, please.”"],
        ["Five minutes (10 min)", "“Company, this is your five-minute call. Five minutes, please.”"],
        ["Beginners (5 min)", "“Act One beginners to the stage, please: Spirit, Octavia, Flanders and opening ensemble.”"],
        ["Department check", "“All departments, report ready.” — QLab/LX, Sound, FX, Deck each answer “Ready”; FOH gives clearance."],
        ["Go for show", "“Standby house lights out, QLab 4, FX HZ-01 … House lights out … QLab 4 — GO.”"],
        ["Interval (tabs in at Q37)", "“Thank you company, that's the interval. Twenty minutes, please.” · QLab 38 interval music, BG-16"],
        ["Interval +10 / +15", "“Ten minutes to Act Two.” Deck reports reset done. “Act Two beginners: palace ensemble, Evan, Willis.”"],
        ["Act Two", "“Standby house lights out, QLab 39 … QLab 39 — GO.”"],
        ["Bows (Q64)", "Hold the bows call until the final line lands; watch the line-up."],
        ["End (Q65)", "“QLab 65 — GO.” House up via FOH. “Thank you company and crew, that's the show.”"]],
        [40 * mm, 130 * mm], bold_first=True))

    d.add(H1("2 Calling sequence"))
    for title, pages, cues in SCENES:
        first, last = cues[0][0], cues[-1][0]
        d.add(H2("%s%s · cues %s to %s" % (title, (" " + pages) if pages else "", first, last)))
        depts = sorted({x.replace("QLAB", "QLab") for c in cues for x in c[5].split()},
                       key=lambda s: ["QLab", "LX", "FX", "DECK", "FOH"].index(s))
        d.add(P("Group standby: “Standby %s for cues %s to %s, please.”" % (", ".join(depts), first, last), "muted"))
        d.add(scene_table(cues))

    d.add(H1("3 Holds, show stops and recovery"))
    d.add(steps([
        "“HOLD, please. Hold.” on Channel A and B. All operators freeze their current state.",
        "If anyone is at risk: “QLab, safe light — GO” (E3 / Mantra P2 M10) and “QLab, stop all — GO” (E1). FOH for house lights.",
        "Announcement: “Ladies and gentlemen, we're taking a short pause in the performance. Please remain in your seats "
        "and we'll continue as soon as possible. Thank you.”",
        "TD and DSM agree the restart cue; tell every department the cue number.",
        "“Standby to restart from Q__ … QLab __ — GO.” House lights out first."]))
    d.add(box("verify", "EVACUATION — FOLLOW THE VENUE PROCEDURE", "“HOLD. Stop the show.” QLab: E1 stop all, E3 safe "
              "light; FOH: house lights full. Make the venue's approved announcement; crew and cast leave by the agreed exits."))
    d.add(table(["Situation", "DSM action"], [
        ["An operator misses a GO", "Call it again once. If the moment has passed, go straight to the next cue."],
        ["Lightning / flash missed", "Skip it. Never call a late flash."],
        ["QLab down", "“LX, take it from the desk” — the operator runs the matching P2/P3/P4 memory with Next Cue; sound goes to emergency playback ch 13–14."],
        ["Q57b missed", "Call it as soon as Ariel is on — the HAYWIRE chase keeps running until it fires."],
        ["Two looks stacking", "“Hold” — operator presses O (All Cues Off) then re-fires the current cue."],
        ["Radio mic fails", "Sound tells DSM; Deck swaps to the spare pack at the next exit."],
        ["Water or haze unsafe", "“FX, stop.” Continue the dry version."]],
        [40 * mm, 130 * mm], bold_first=True))

    d.add(H1("4 Script findings"))
    d.add(bullets(["The contents page lists “Scene Eleven: On the Shore” but there is no Scene Eleven in the text: Scene Ten (pp 51–54) runs straight to Scene Twelve (p 55).",
                   "The contents list a Scene Five song (p 33) that isn’t in the text.",
                   "Octavia's palace entrance (p 36) comes before the cue cards (p 37), so cues 42 and 43 stay swapped.",
                   "The water pistols spray the audience (pp 20 and 46) — Manual R-23."]))
    d.add(notes_area("Paper-tech notes", 8))
    return d.build()
