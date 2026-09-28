"""Part L — Stream Deck & Tech Test Run (R13.1)."""
from core import *  # noqa: F401,F403
import show as S_


def build(path):
    d = PartDoc(path, "L", "Stream Deck & Tech Test Run",
                "Stream Deck key layout and profile set-up, emergency hotkeys, and the tech test run that steps through every "
                "cue, song section and critical sequence of the show.")
    d.add(title_block("PART L · %s · %s" % (REV, DATE), "Stream Deck & Tech Test Run",
                      "The show operator's Stream Deck, and a structured run through every cue"))
    d.add(stats([("8", "Stream Deck keys"), (str(S_.N_MASTER), "master cues"), (str(S_.N_SONG_SECTIONS), "song-section GOs"),
                 ("4", "critical sequences")]))
    d.add(H1("1 Stream Deck"))
    d.add(table(["Key", "Where", "Does"], [
        ["GO", "row 1, key 1", "QLab GO (Space)"], ["PREV", "row 1, key 2", "Playhead up (↑)"],
        ["NEXT", "row 1, key 3", "Playhead down (↓)"], ["PANIC", "row 1, key 5", "QLab Panic (Esc) — fades and stops everything in QLab"],
        ["VIDEO BLACK", "row 2, key 1", "F13 → E2 VID-99 BLACK"], ["SAFE LIGHT", "row 2, key 2", "F14 → E3 SAFE LIGHT (Mantra P2 M10)"],
        ["STOP SOUND", "row 2, key 3", "F15 → E1 STOP ALL"], ["SAVE", "row 3, key 5", "Cmd+S — rehearsals only"]],
        [30 * mm, 30 * mm, 110 * mm], bold_first=True))
    d.add(P("Every key is a plain Hotkey, so QLab must be the front window. The profile (05_Stream_Deck/TLM QLab "
            "Show.streamDeckProfile) holds this layout."))
    d.add(H2("A Import the profile"))
    d.add(steps(["Install the Elgato Stream Deck app; plug the Stream Deck in.",
                 "Double-click TLM QLab Show.streamDeckProfile › Import. Select the TLM QLab Show profile.",
                 "If the import fails, build the keys by hand: System › Hotkey on each key, press the key in the table, add the title."]))
    d.add(H2("B Give the emergency cues their hotkeys in QLab"))
    d.add(box("verify", "NOT SET IN THE WORKSPACE", "E1–E3 exist below cue 66 but have no hotkeys yet."))
    d.add(steps(["Select **E1 STOP ALL** › Inspector › Triggers › tick Hotkey › press F15.",
                 "Select **E2 VID-99 BLACK** › Triggers › Hotkey › F13.",
                 "Select **E3 SAFE LIGHT** › Triggers › Hotkey › F14.",
                 "Save. Press each Stream Deck key once with the projector and the Mantra on."]))
    d.add(P("Optional: Figure 53's QLab plugin can fire GO, Panic and any cue even when QLab isn't in front — keep the same "
            "positions and icons. Allow OSC access in Workspace Settings › Network (no passcode)."))

    d.add(H1("2 Tech test run"))
    d.add(P("Run the test straight from the workspace in the passes below; no script is needed."))
    d.add(H2("Before you start"))
    d.add(checklist(["QLab front window, Edit Mode", "Mantra on, Default Show loaded, O (All Cues Off)", "Haze off, water disconnected",
                     "Playback low on the StudioLive", "Anyone on stage warned before storm and flash cues",
                     "SAFE LIGHT (F14) ready throughout"], cols=2))
    d.add(H2("Run order"))
    d.add(table(["Pass", "How", "Pass criteria"], [
        ["1 Check", "Scroll the cue list: no red (broken) cues. Workspace Settings: audio, video, network set.", "No red cues except known placeholders"],
        ["2 Emergency", "F14 → P2 M10 · F13 → black · F15 → stop", "Desk, projector and audio respond"],
        ["3 Step through", "From Q1 with SM, show operator and Sound on headset: GO each cue, tick the table below", "Every cue fires light, sound and video"],
        ["4 Critical", "Step again from Q20 (storm), Q33 (transformation), Q45 (jellyfish), Q52 (voice transfer)", "Flashes return; releases; HAYWIRE on/off"],
        ["5 Songs", "From each song group: S# GO, then each section GO", "Track starts; scene memory released; sections change"],
        ["6 Show day", "Quick step-through of one cue per memory with sound low", "System check before the house opens"]],
        [26 * mm, 94 * mm, 50 * mm], bold_first=True))
    d.add(H2("Step-through record"))
    rows = []
    for c in S_.CUES:
        lx = " · ".join("P%d M%d c%d" % (x["p"], x["m"], x["c"]) for x in c["lx"][:1])
        rows.append(["**%s**" % c["num"], c["name"], lx, " ".join(c["video"]), "☐", "☐", "☐", ""])
        if c["song"]:
            so = S_.SONG[c["song"]]
            rows.append(["**%s**" % so["num"], "%s (%d sections)" % (so["title"], len(so["sections"])), "P4 M%d" % so["mem"], "", "☐", "☐", "—", ""])
    d.add(table(["Q", "Cue", "Desk", "Video", "LX", "Snd", "Vid", "Problem / note"], rows,
                [11 * mm, 44 * mm, 22 * mm, 14 * mm, 9 * mm, 9 * mm, 9 * mm, 52 * mm]))
    d.add(box("verify", "SAFETY DURING THE TEST", "Haze off and water disconnected. Warn anyone on stage before storm, flash and "
              "HAYWIRE cues. Keep playback low — songs start for real. SAFE LIGHT stays one key away."))
    d.add(notes_area("Test notes / faults to fix", 8))
    return d.build()
