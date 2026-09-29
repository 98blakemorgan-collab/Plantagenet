"""TLM_To_Find_and_Confirm_R13_1.pdf — the open-items list for the R13.1 show."""
from core import *  # noqa: F401,F403
import show as S_

# (area, item, who, when)
ITEMS = [
    ("Audio", "Backing tracks for S2 Feeling Good, S3 Part of Your World, S5 Time of My Life (the files are vocal versions)", "MD / Sound", "Before dress"),
    ("Audio", "Check S4 Wellerman for vocals; swap for a backing track if needed", "MD", "Before dress"),
    ("Audio", "Choose the S7 jellyfish chorus song (script: SONG TBA) — silent placeholder until then", "Director / MD", "Before tech"),
    ("Audio", "House, preshow, end of Act One, interval and exit music (Q1, Q2, Q37, Q38, Q65)", "Sound", "Before tech"),
    ("Audio", "Ariel's recorded line Q42.5; confirm Q11, Q43, Q59 sounds (placeholders)", "Director / Sound", "Before tech"),
    ("Audio", "S1 Rock Lobster is the 7:05 music-video cut — confirm the edit and where it fades (Q9)", "MD / choreographer", "Before tech"),
    ("Audio", "Save every new file under a NEW file name, then drag it onto the cue (Part E)", "Sound", "Always"),
    ("Script", "Scene Eleven: On the Shore is in the contents (p 55) but has no text — cut or missing?", "Director", "Now"),
    ("Script", "The Scene Five song on the contents page is not in the text — which song, and where?", "Director / MD", "Now"),
    ("Script", "Sisters' names: script says Persil, Lenor, Daz, Own Brand; casting says Scarlotte, Paulette, Charlotte, Kandy", "Director", "Now"),
    ("Script", "Crab Rave (S6) is dance-only per the casting sheet — confirm no one sings", "Choreographer", "Now"),
    ("Show control", "Show Mac QLab settings: audio → StudioLive USB, Video Stage 1 → projector, MANTRA patch → Ethernet interface (R-29)", "QLab op", "Tech"),
    ("Show control", "Add the Mantra OSC remote trigger: Play Memory, port 8000 (not stored in the .mtr)", "LX", "Tech"),
    ("Show control", "Give E1/E2/E3 their hotkeys F15/F13/F14 in QLab; test the Stream Deck", "QLab op", "Tech"),
    ("Show control", "Turn off Art-Net or sACN on the Mantra (whichever the node doesn't use)", "LX", "Tech"),
    ("Show control", "Who calls the 56 song-section GOs — DSM or QLab op to the music (R-31)", "SM / QLab op", "Before tech"),
    ("Lighting", "Confirm fixtures #38 (PixBar) and #39 (TourCOB) exist and are patched", "LX / venue", "Rig day"),
    ("Lighting", "All 12 C42s on the FOH bar — APPROVED (runs back to the dimmer setup). Set the FOH dimmer channels feeding them to NON-DIM, 4 C42 per circuit", "LX / venue", "Rig day"),
    ("Lighting", "Is the dimmer rack also on DMX? If so, which universe/addresses — it must never fade the C42 feeds", "Venue", "Site walk"),
    ("Lighting", "Check the colour-forward looks from the house: faces, screen washout, backlight (R-30)", "LX / director", "Focus"),
    ("Lighting", "Cue-to-cue: flash returns Q21/23/25/35/47/57b, the Q57 → Q57b HAYWIRE sequence, the Level=0 releases (run Q8 > S1 > Q9) and the six song fade-outs", "LX / QLab op", "Tech"),
    ("Lighting", "Pinspots #41–42 (P5 M7) only if the mirror ball is used", "LX", "Rig day"),
    ("Projection", "Projector bar rating and bond (R-22); screen size and throw", "Venue / TD", "Site walk"),
    ("Projection", "Spare backdrops BG-10, 12, 14, 15, 24 — keep or delete after tech", "Director", "After tech"),
    ("Safety", "Water pistols hit the audience (R-23): front-row notice, towels, stage-dry checks", "Director / FOH", "Before first show"),
    ("Safety", "Haze: detector isolation procedure agreed with the venue; post the FOH notice", "Venue / FOH", "Before first show"),
    ("Rig", "Stage bars, floor-boom bases and wing space (R-24, R-26); wet zone at the site walk", "Venue / TD", "Site walk"),
    ("Props", "Decide the battered-fish swap (P07) and the P24 bridal quick change; P26 optional", "Props / wardrobe", "Rehearsal"),
    ("Crew", "Name a Deck/ASM and a FOH manager; one show operator runs QLab (R-27)", "Producer", "Now"),
]


def build(path):
    d = PartDoc(path, "", "To Find and Confirm", divider=False)
    d.add(title_block("%s · %s" % (REV, DATE), "To Find and Confirm",
                      "Everything the show files can't settle on their own — tick it off as it's found or agreed"))
    d.add(stats([(str(len(ITEMS)), "open items"), ("10", "placeholder sounds"), ("3", "script questions"),
                 ("4", "settings not stored in the files")]))
    areas = []
    for a, *_ in ITEMS:
        if a not in areas:
            areas.append(a)
    for a in areas:
        d.add(H2(a))
        d.add(table(["", "Item", "Who", "When", "Done / note"],
                    [["☐", i, w, t, ""] for aa, i, w, t in ITEMS if aa == a],
                    [7 * mm, 88 * mm, 27 * mm, 20 * mm, 28 * mm]))
    d.add(box("rule", "WHERE THINGS ARE", "Placeholders: Part E §6. Script questions: Part G. Settings: Part E §3 and Quick Guide "
              "card 6. Recommendations R-01 to R-31: Part A."))
    return d.build()
