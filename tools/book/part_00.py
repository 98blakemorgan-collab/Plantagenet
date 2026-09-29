"""00 — Cover and Contents. Built last, from the page counts of the finished parts."""
import os

from core import *  # noqa: F401,F403
import show as S_

HERE = os.path.dirname(os.path.abspath(__file__))
THUMBS = os.path.join(HERE, "..", "..", "production", "assets", "thumbs")

AT_A_GLANCE = [
    "**Show control:** QLab fires every cue. The Mantra show is split by scene — Act One on P2, Act Two on P3, the ten songs on "
    "P4, FX on P5, looks on P6–P7 and a full backup list on P8.",
    "**Flashes:** the six flash returns are timed by QLab pre-waits, so no link times are typed into the desk.",
    "**Releases:** 31 Level=0 messages release each memory as the show leaves it.",
    "**Songs:** ten song groups (S1–S10) with 66 section GOs on their own P4 looks.",
    "**Key sequences:** the storm, the transformation, the jellyfish and the voice transfer with HAYWIRE from Q57 to Q57b.",
    "**Looks:** the colour-forward looks are shown as colour swatches for every cue (Parts A, B, D, I).",
    "**Backdrops:** 21 in the cue plan plus 5 spares, shown as real images with their prompts (Part I).",
    "**Script:** paged to the licensed script revised April 2026 (Parts G, H, J and the cue sheets). Casting is from the "
    "28 September 2026 casting sheet.",
    "**Open items:** Part A R-28 to R-31, plus the To Find and Confirm list.",
]


def build(path, parts):
    """parts: [(letter, title, pages, start_page)] in book order."""
    d = PartDoc(path, "", "Cover and Contents", divider=False)
    d.add(title_block("PRODUCTION BOOK · %s · %s" % (REV, DATE), "The Little Mermaid",
                      "by Nick Lawrence · Plantagenet Hall · complete technical production book"))
    imgs = ["BG-02", "BG-07", "BG-12", "BG-15"]
    files = sorted(os.listdir(THUMBS))
    cells = [picture(os.path.join(THUMBS, next(f for f in files if f.startswith(b))), 41 * mm) for b in imgs]
    t = Table([cells], colWidths=[42.5 * mm] * 4)
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0.7 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 0.7 * mm)]))
    d.add(t, P("Backdrops BG-02 Beneath the Waves · BG-07 Storm · BG-12 Lair · BG-15 Finale (Part I).", "muted"))
    d.add(stats([(str(S_.N_MASTER), "master cues"), (str(S_.TOTAL_QLAB_CUES), "QLab cues"),
                 (str(S_.N_POSITIONS), "Mantra positions"), ("10", "songs"), ("21", "backdrops in use")]))
    d.add(H1("Contents"))
    rows = [["**%s**" % L if L else "", T, str(n), str(s)] for L, T, n, s in parts]
    d.add(table(["Part", "Title", "Pages", "Starts on page"], rows, [16 * mm, 110 * mm, 18 * mm, 26 * mm]))
    d.add(P("Laid out to print economically: rules instead of solid fills, pale row tints and swatches. "
            "Page numbers are the page of the complete book PDF. Each part is also a separate PDF in "
            "01_Production_Book/Sections. Part J reproduces the licensed script: production use only.", "muted"))
    d.add(PageBreak(), H1("The show at a glance"))
    d.add(bullets(AT_A_GLANCE))
    d.add(H2("Show files this book describes"))
    d.add(table(["File", "What"], [
        [S_.QLAB_NAME, "QLab 5 workspace — %d cues, %d master groups, songs S1–S10, emergency E1–E3" % (S_.TOTAL_QLAB_CUES, S_.N_MASTER)],
        [S_.MTR_NAME, "Mantra Lite show — %d positions over P2/P3/P4, FX P5, looks P6–P7, backup P8" % S_.N_POSITIONS],
        ["TLM_nov_2026_final_MANTRA_SECTION_MAP.csv", "Every QLab → Mantra target (page, memory, cue)"],
        ["TLM_nov_2026_final_MEDIA_MANIFEST.csv", "The 80 media files the workspace uses"],
        ["TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv", "Show-control fixes and what is still to do"],
        ["docs/FOH_Flashing_Lights_and_Haze_Notice.pdf", "Front-of-house notice, ready to print"]], [70 * mm, 100 * mm], bold_first=True))
    d.add(H2("Document control"))
    d.add(table(["Rev", "Date", "Notes"], [
        [REV, "28 Sep 2026", "Production book for the show files listed above, the April 2026 script and the 28 Sep 2026 casting"]],
        [24 * mm, 26 * mm, 120 * mm], bold_first=True))
    d.add(box("verify", "WORKING DOCUMENT", "Everything is built from the show files. Levels, colours and timings are starting "
              "recipes. Confirm them in the venue and record changes in pencil and in the show report."))
    return d.build()
