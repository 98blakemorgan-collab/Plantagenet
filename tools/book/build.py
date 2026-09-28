"""Build the R13.1 production folder: python3 tools/book/build.py

Writes production/TLM_Show_R13_1/, mirroring the TLM_Show 2 folder on Drive (00_START_HERE, 01_Production_Book with
Sections, 02_QLab ... 99_Show_Backups), and refreshes the printouts in package/TLM_R13_REBUILT_Show_Files/docs.

Part J (prompt copy) contains the licensed script. It is built only when production/private/ holds the script render,
and it is written to production/private/ — never into the public tree.
"""
import csv
import os
import shutil
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import calls  # noqa: E402
import show as S_  # noqa: E402
from core import REV, DATE  # noqa: E402
import make_printouts as mp  # noqa: E402  (tools/ is on sys.path via show)
import part_00, part_a, part_b, part_c, part_d, part_e, part_g, part_h, part_i, part_j, part_k, part_l  # noqa: E402
import to_find  # noqa: E402

OUT = os.path.join(ROOT, "production", "TLM_Show_R13_1")
PRIVATE = os.path.join(ROOT, "production", "private")
PKG = os.path.join(ROOT, "package", "TLM_R13_REBUILT_Show_Files")
BOOK = os.path.join(OUT, "01_Production_Book")
SECT = os.path.join(BOOK, "Sections")
TAG = "TLM_R13_1"

PARTS = [  # letter, title, file stem
    ("A", "Master Technical Production Manual", "A_Master_Technical_Production_Manual"),
    ("B", "Lighting Design", "B_Lighting_Design"),
    ("C", "DMX Patch and Step-by-Step Guide", "C_DMX_Patch_and_Step_by_Step_Guide"),
    ("D", "Mantra Editor on Mac Programming Guide", "D_Mantra_Editor_on_Mac_Programming_Guide"),
    ("E", "QLab 5 Programming Guide", "E_QLab_5_Programming_Guide"),
    ("F", "Operator Cue Sheets", "F_Operator_Cue_Sheets"),
    ("G", "DSM Calling Script", "G_DSM_Calling_Script"),
    ("H", "Props List and Preset Sheets", "H_Props_List_and_Preset_Sheets"),
    ("I", "Projection Backgrounds", "I_Projection_Backgrounds"),
    ("J", "Prompt Copy (Licensed Script)", "J_Prompt_Copy_Licensed_Script"),
    ("K", "Quick Reference Cards", "K_Quick_Reference_Cards"),
    ("L", "Stream Deck and Tech Test Run", "L_Stream_Deck_and_Tech_Test_Run"),
]
BUILDERS = {"A": part_a.build, "B": part_b.build, "C": part_c.build, "D": part_d.build, "E": part_e.build,
            "G": part_g.build, "H": part_h.build, "I": part_i.build, "K": part_k.build, "L": part_l.build}

ABOUT = {
    "01_Production_Book": "The R13.1 production book: the complete book, one PDF per part in Sections, the quick guide and the to-find list.",
    "01_Production_Book/Sections": "One PDF per part of the book (00 cover, A-L). Part J is private - see the note in this folder.",
    "01_Production_Book/Cue_Sheets_Printed": "Scans or photos of the marked-up printed cue sheets from tech and each show.",
    "02_QLab": "QLab: README, the R13.1 cue list as a spreadsheet. The show folder itself is package/TLM_R13_REBUILT_Show_Files.",
    "03_Lighting_Mantra": "Mantra: memory map, section map, labels. The R13.1 show file is in package/TLM_R13_REBUILT_Show_Files.",
    "03_Lighting_Mantra/Backups": "Dated Mantra exports (Tools > Export Show) from the desk: YYYY-MM-DD_TLM_R13_1.mtr",
    "04_Sound_StudioLive": "StudioLive scene notes and template (TLM_StudioLive_SIII16_Show_Template.xlsx, unchanged from R8).",
    "04_Sound_StudioLive/Backups": "StudioLive scene backups.",
    "05_Stream_Deck": "TLM QLab Show.streamDeckProfile - unchanged in R13.1. Hotkeys: see Part L.",
    "06_Projection_Source": "Projection source material: originals, rejects and the rights/prompt log. Not used in the show.",
    "06_Projection_Source/Generated_Originals": "Full-resolution AI originals of the R10 backdrops before export.",
    "06_Projection_Source/Rejects": "Rejected generations.",
    "06_Projection_Source/Rights_Log": "How each backdrop was made: R10_Backdrop_Prompt_Log.csv (tool, prompts, date).",
    "07_Rehearsal_and_Tech_Notes": "Rehearsal reports, tech notes, show reports (Part A appendices).",
    "08_Venue_and_Rig": "Venue plans, rig photos, site-walk notes, power and rigging confirmations.",
    "99_Show_Backups": "Whole-folder backups: copy the show folder here after each session, dated.",
}


def pages(path):
    with pymupdf.open(path) as d:
        return d.page_count


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.rstrip("\n") + "\n")


def cue_sheets(out_dir):
    """Part F: the operator cue sheets, with page references from the April 2026 script."""
    mp.PAGE_OVERRIDE.clear()
    mp.PAGE_OVERRIDE.update({q: p for q, p in calls.GO_PAGE.items() if str(p).isdigit()})
    mp.OUT = out_dir
    groups = [mp.parse_group(g) for g in mp.load_qlab()]
    mems = mp.load_mtr()
    _, by_pmc = mp.load_map()
    return mp.build_cue_sheets(groups, by_pmc, mems), mp.build_labels(mems)


def j_placeholder(path):
    doc = pymupdf.open()
    pg = doc.new_page(width=595, height=842)
    pg.insert_textbox(pymupdf.Rect(60, 300, 535, 600),
                      "PART J · PROMPT COPY (LICENSED SCRIPT)\n\nThis part reproduces the licensed script, so it is not "
                      "included in this copy of the book. The production copy is held privately with the show's Drive "
                      "folder (01_Production_Book/Sections/%s_J_Prompt_Copy_Licensed_Script.pdf).\n\nThe cues and page "
                      "numbers it carries are the same as Part G, the DSM calling script." % TAG,
                      fontname="helv", fontsize=12, align=0)
    doc.save(path)


def merge(files, path):
    out = pymupdf.open()
    toc = []
    for title, f in files:
        toc.append([1, title, out.page_count + 1])
        with pymupdf.open(f) as d:
            out.insert_pdf(d)
    out.set_toc(toc)
    out.save(path, garbage=3, deflate=True)


def cue_list_csv(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Cue", "Name", "Trigger", "Script page", "Mantra target", "Look", "Sound", "Video", "FX", "Song", "Critical"])
        for c in S_.CUES:
            tgt = "; ".join("P%d M%d cue %d" % (x["p"], x["m"], x["c"]) for x in c["lx"])
            w.writerow([c["num"], c["name"], c["trigger"], calls.GO_PAGE.get(c["num"], ""), tgt, c["look"], c["sound"],
                        " ".join(c["video"]), c["fx"], c["song"] or "", "yes" if c["critical"] else ""])
            if c["song"]:
                s = S_.SONG[c["song"]]
                w.writerow([s["num"], s["title"], "Straight after Q%s" % c["num"], calls.GO_PAGE.get(c["num"], ""),
                            "P4 M%d (%d sections)" % (s["mem"], len(s["sections"])), "", s["file"], "", "", s["num"], ""])


def backdrop_log(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Backdrop", "Title", "Image prompt", "Motion prompt", "Note"])
        for k, (t, img, mot, note) in part_i.BACKDROPS.items():
            w.writerow([k, t, img, mot, note])


START_HERE = """THE LITTLE MERMAID - Plantagenet Hall - show folder - {rev} ({date})

01_Production_Book     Complete book + one PDF per part (Sections), quick guide, to-find list
02_QLab                README + cue list. THE SHOW FOLDER is package/TLM_R13_REBUILT_Show_Files:
                         {qlab}  ({ncues} cues, {nmaster} master cues, songs S1-S10)
                         media/  80 files (R13_MEDIA_MANIFEST.csv) - assembled on the Mac by
                         package/ASSEMBLE_R13_1.command from the Drive zips
03_Lighting_Mantra     {mtr} + memory map, section map, labels
04_Sound_StudioLive    mixer template + backups
05_Stream_Deck         exported profile (unchanged)
06_Projection_Source   originals, rejects, rights/prompt log (not used in the show)
07_Rehearsal_and_Tech_Notes
08_Venue_and_Rig
99_Show_Backups

WHAT CHANGED FROM R8
- The Mantra show is split by scene: P2 Act One, P3 Act Two, P4 the ten songs, P5 FX, P6-P7 looks, P8 backup.
  QLab fires every cue by page/memory/cue and releases each memory as it leaves it (31 releases).
- Flash returns are QLab pre-waits - no link times to type into the desk.
- Songs are QLab groups S1-S10 with {nsec} section GOs.
- The book is re-paged to the licensed script revised April 2026, with the 28 Sep 2026 casting.

BOOK: 01_Production_Book/The_Little_Mermaid_Complete_Production_Book_{rev}.pdf
      (Part J, the prompt copy, contains the licensed script and is kept privately - not in the public repo.)
FIRST: 01_Production_Book/TLM_To_Find_and_Confirm_R13_1.pdf - what is still to supply or decide.
SET-UP: 01_Production_Book/TLM_Setup_and_Startup_Quick_Guide_R13_1.pdf (cards 6-7).

Rebuild everything in this folder with: python3 tools/book/build.py
"""

QLAB_README = """THE LITTLE MERMAID - Plantagenet Hall - QLab ({rev}, {date})

THE SHOW FOLDER: package/TLM_R13_REBUILT_Show_Files  (copy it to the show Mac's Desktop with that exact name)
  {qlab}   {ncues} cues: {nmaster} master cue groups, songs S1-S10 ({nsec} section GOs), E1-E3 emergency
  media/audio, media/video, media/stills   80 files listed in R13_MEDIA_MANIFEST.csv
  R13_MANTRA_SECTION_MAP.csv              every Mantra target QLab fires
  R13_1_QLAB_AND_DESK_FIX_LIST.csv        what R13.1 changed, what is still to do

STEPS (Part E and the Quick Guide, card 6)
1. Run package/ASSEMBLE_R13_1.command on the Mac - it unpacks the Drive zips into the show folder.
2. Open {qlab}. Workspace Settings:
     Audio  - Patch 1 -> StudioLive USB (outs 1-2 -> desk ch 11-12)
     Video  - Stage 1 -> projector
     Network - MANTRA patch (OSC, 2.0.0.1 port 8000) -> the wired Ethernet interface
3. Give E1 STOP ALL F15, E2 VID-99 BLACK F13, E3 SAFE LIGHT F14 (Triggers > Hotkey). Save.
4. On the Mantra add the OSC remote trigger: Play Memory, port 8000.
5. Supply the placeholder sounds (To Find and Confirm list) - save under NEW file names, drag onto the cue.

TLM_QLab_cue_list.csv   the {nmaster} master cues and 10 songs as a spreadsheet, with script pages (April 2026 script)

The R8/R11 AppleScripts (Build_TLM_QLab_Workspace, Tech_Test_Run, Relink_Media) were written for the old single-list
workspace and are not needed for R13.1 - the workspace is already built. See Part L for the R13.1 tech test run.
"""

MEMORY_MAP = """{mtr} - memory map ({rev}, {date})
Patch, custom fixtures, rig view and network unchanged from BASE_SHOW_2026 / R8. Desk opens on Page 2.
QLab fires /PlayMemory/Page=P/Memory=M/Cue=C/Level=100/Fade=ms  and releases with Level=0.

{pages}

LOOK LIBRARY
{looks}

NOT STORED IN THE FILE - SET ON THE DESK
  Tools > Setup > Remote Triggers: OSC, Play Memory, port 8000
  Turn off Art-Net or sACN, whichever the universe-2 node does not use
  NO link times: flash returns are fired by QLab pre-waits (Q21/23/25 +0.2 s, Q35 +0.3 s, Q47 +1 s, Q57b +0.3 s)

Levels and colours are starting recipes - set final levels in the venue with performers.
No strobe anywhere; lightning = single flash cues. HAYWIRE (P5 M5) starts at Q57 and stops at Q57b.
"""


def main():
    private_ok = os.path.exists(part_j.SCRIPT)
    os.makedirs(SECT, exist_ok=True)
    fmt = dict(rev=REV, date=DATE, tag=TAG, qlab=S_.QLAB_NAME, mtr=S_.MTR_NAME, ncues=S_.TOTAL_QLAB_CUES,
               nmaster=S_.N_MASTER, nsec=S_.N_SONG_SECTIONS)

    # parts
    built = {}
    for L, title, stem in PARTS:
        path = os.path.join(SECT, "%s_%s.pdf" % (TAG, stem))
        if L == "F":
            sheets, labels = cue_sheets(SECT)
            os.replace(sheets, path)
            os.remove(labels)  # the labels go in 03_Lighting_Mantra (below)
        elif L == "J":
            path = os.path.join(SECT, "_Part_J_is_private.pdf")
            j_placeholder(path)
            if private_ok:
                built["J_private"] = part_j.build(os.path.join(PRIVATE, "%s_%s.pdf" % (TAG, stem)))
        else:
            BUILDERS[L](path)
        built[L] = path
        print("%s %3d pages  %s" % (L, pages(path), os.path.relpath(path, ROOT)))

    # cover: build twice so the contents page numbers include the cover itself
    cover = os.path.join(SECT, "%s_00_Cover_and_Contents.pdf" % TAG)
    ncover = 2
    for _ in range(2):
        start, rows = ncover + 1, []
        for L, title, _s in PARTS:
            n = pages(built[L])
            rows.append((L, title + (" — held privately" if L == "J" else ""), n, start))
            start += n
        part_00.build(cover, [("00", "Cover and Contents", ncover, 1)] + rows)
        ncover = pages(cover)
    print("00 %3d pages" % ncover)

    order = [("00 Cover and Contents", cover)] + [("%s %s" % (L, t), built[L]) for L, t, _s in PARTS]
    merge(order, os.path.join(BOOK, "The_Little_Mermaid_Complete_Production_Book_%s.pdf" % REV))
    if private_ok:
        merge([(t, built["J_private"] if t.startswith("J ") else f) for t, f in order],
              os.path.join(PRIVATE, "The_Little_Mermaid_Complete_Production_Book_%s_with_J.pdf" % REV))
    part_k.build_quick_guide(os.path.join(BOOK, "TLM_Setup_and_Startup_Quick_Guide_R13_1.pdf"))
    to_find.build(os.path.join(BOOK, "TLM_To_Find_and_Confirm_R13_1.pdf"))

    # text files and folders
    write(os.path.join(OUT, "00_START_HERE.txt"), START_HERE.format(**fmt))
    for rel, text in ABOUT.items():
        write(os.path.join(OUT, rel, "_ABOUT_THIS_FOLDER.txt"), text)
    write(os.path.join(SECT, "_ABOUT_THIS_FOLDER.txt"), ABOUT["01_Production_Book/Sections"])
    write(os.path.join(OUT, "02_QLab", "README.txt"), QLAB_README.format(**fmt))
    cue_list_csv(os.path.join(OUT, "02_QLab", "TLM_QLab_cue_list.csv"))
    pagelines = "\n".join("%-3s %-26s %s\n    %s" % (p, what, use, mems) for p, what, mems, use in part_d.PAGEMAP)
    looks = "\n".join("  %-16s P%d M%d" % (L["name"], L["page"], L["mem"]) for L in S_.LOOKS)
    write(os.path.join(OUT, "03_Lighting_Mantra", "%s_memory_map.txt" % TAG),
          MEMORY_MAP.format(pages=pagelines, looks=looks, **fmt))
    for f in ("R13_MANTRA_SECTION_MAP.csv", "R13_MANTRA_SECTION_MAP.txt"):
        shutil.copy(os.path.join(PKG, f), os.path.join(OUT, "03_Lighting_Mantra", f))
    shutil.copy(os.path.join(PKG, "R13_MEDIA_MANIFEST.csv"), os.path.join(OUT, "02_QLab", "R13_MEDIA_MANIFEST.csv"))
    backdrop_log(os.path.join(OUT, "06_Projection_Source", "Rights_Log", "R10_Backdrop_Prompt_Log.csv"))

    # labels and the package printouts (same content, package names)
    sheets, labels = cue_sheets(os.path.join(PKG, "docs"))
    shutil.copy(labels, os.path.join(OUT, "03_Lighting_Mantra", "%s_Mantra_Labels.pdf" % TAG))
    print("package docs:", os.path.relpath(sheets, ROOT), os.path.relpath(labels, ROOT))
    print("J private:", built.get("J_private", "not built (no private script render)"))


if __name__ == "__main__":
    main()
