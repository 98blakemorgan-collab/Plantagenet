"""Build the R13.1 production folder: python3 tools/book/build.py

Writes production/TLM_nov_2026_final/, mirroring the TLM_Show 2 folder on Drive (00_START_HERE, 01_Production_Book with
Sections, 02_QLab ... 99_Show_Backups), and refreshes the printouts in package/TLM_nov_2026_final/docs.

Part J (prompt copy) is built from the licensed script render in production/script_source/. Licensed material: keep
this repository private.
"""
import csv
import os
import re
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
import lighting_plot  # noqa: E402
import lx_moves  # noqa: E402
import backdrop_sheets  # noqa: E402
import part_00, part_a, part_b, part_c, part_d, part_e, part_g, part_h, part_i, part_j, part_k, part_l  # noqa: E402
import to_find  # noqa: E402

OUT = os.path.join(ROOT, "production", "TLM_nov_2026_final")
PKG = os.path.join(ROOT, "package", "TLM_nov_2026_final")
BOOK = os.path.join(OUT, "01_Production_Book")
SECT = os.path.join(BOOK, "Sections")
TAG = "TLM_nov_2026_final"

PARTS = [  # letter, title, file stem
    ("A", "Master Technical Production Manual", "A_Master_Technical_Production_Manual"),
    ("B", "Lighting Design", "B_Lighting_Design"),
    ("B2", "Stage Lighting Layout Plan (A3)", "B2_Stage_Lighting_Layout_Plan"),
    ("B3", "Rig Move Guide", "B3_Rig_Move_Guide"),
    ("C", "DMX Patch and Step-by-Step Guide", "C_DMX_Patch_and_Step_by_Step_Guide"),
    ("D", "Mantra Editor on Mac Programming Guide", "D_Mantra_Editor_on_Mac_Programming_Guide"),
    ("E", "QLab 5 Programming Guide", "E_QLab_5_Programming_Guide"),
    ("F", "Operator Cue Sheets", "F_Operator_Cue_Sheets"),
    ("G", "DSM Calling Script", "G_DSM_Calling_Script"),
    ("H", "Props List and Preset Sheets", "H_Props_List_and_Preset_Sheets"),
    ("I", "Projection Backgrounds", "I_Projection_Backgrounds"),
    ("I2", "Backdrop Sheets (one page per backdrop)", "I2_Backdrop_Sheets"),
    ("J", "Prompt Copy (Licensed Script)", "J_Prompt_Copy_Licensed_Script"),
    ("K", "Quick Reference Cards", "K_Quick_Reference_Cards"),
    ("L", "Stream Deck and Tech Test Run", "L_Stream_Deck_and_Tech_Test_Run"),
]
# Parts kept out of the merged book to save printer ink (image-heavy); they stay as their own PDFs in Sections.
SEPARATE = {"I2"}
BUILDERS = {"A": part_a.build, "B": part_b.build, "B2": lighting_plot.build, "B3": lx_moves.build_moves, "I2": backdrop_sheets.build, "C": part_c.build, "D": part_d.build, "E": part_e.build,
            "G": part_g.build, "H": part_h.build, "I": part_i.build, "K": part_k.build, "L": part_l.build}

ABOUT = {
    "01_Production_Book": "The R13.1 production book: the complete book, one PDF per part in Sections, the quick guide and the to-find list.",
    "01_Production_Book/Sections": "One PDF per part of the book (00 cover, A-L). Part J reproduces the licensed script: production use only.",
    "01_Production_Book/Cue_Sheets_Printed": "Scans or photos of the marked-up printed cue sheets from tech and each show.",
    "02_QLab": "QLab: README, the cue list as a spreadsheet. The show folder itself is package/TLM_nov_2026_final.",
    "03_Lighting_Mantra": "Mantra: memory map, section map, show labels, lighting changes, show and venue base previz, and reference copies of the venue base printouts. The show file is in package/TLM_nov_2026_final; the venue base is its own package, base/Plantagenet_Players_Base_2026_r1.",
    "03_Lighting_Mantra/Backups": "Dated Mantra exports (Tools > Export Show) from the desk: YYYY-MM-DD_TLM_R13_1.mtr",
    "04_Sound_StudioLive": "StudioLive scene notes and template (TLM_StudioLive_SIII16_Show_Template.xlsx).",
    "04_Sound_StudioLive/Backups": "StudioLive scene backups.",
    "05_Stream_Deck": "TLM QLab Show.streamDeckProfile. Hotkeys: see Part L.",
    "06_Projection_Source": "Projection source material: originals, rejects and the rights/prompt log. Not used in the show.",
    "06_Projection_Source/Generated_Originals": "Full-resolution AI originals of the backdrops before export.",
    "06_Projection_Source/Rejects": "Rejected generations.",
    "06_Projection_Source/Rights_Log": "How each backdrop was made: Backdrop_Prompt_Log.csv (tool, prompts, date).",
    "07_Rehearsal_and_Tech_Notes": "Rehearsal reports, tech notes, show reports (Part A appendices).",
    "08_Venue_and_Rig": "Venue plans, rig photos, site-walk notes, power and rigging confirmations. The stage lighting layout plan is here and in Sections (B2).",
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
            w.writerow([c["num"], c["name"], re.sub(r"\s*\(p\d+\)", "", c["trigger"]), calls.GO_PAGE.get(c["num"], ""), tgt, c["look"], c["sound"],
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
02_QLab                README + cue list. THE SHOW FOLDER is package/TLM_nov_2026_final:
                         {qlab}  ({ncues} cues, {nmaster} master cues, songs S1-S10)
                         media/  80 files (TLM_nov_2026_final_MEDIA_MANIFEST.csv) - assembled on the Mac by
                         package/ASSEMBLE_TLM_nov_2026_final.command from the Drive zips
03_Lighting_Mantra     {mtr} + memory map, section map, labels, lighting changes,
                       show previz and venue base previz
04_Sound_StudioLive    mixer template + backups
05_Stream_Deck         exported profile
06_Projection_Source   originals, rejects, rights/prompt log (not used in the show)
07_Rehearsal_and_Tech_Notes
08_Venue_and_Rig       layout plan (B2), rig move guide (B3), venue and rig photos
99_Show_Backups
TLM_nov_2026_final_File_Guide.pdf     every file in the build, what it is and who uses it
TLM_nov_2026_final_Build_Check.txt    the latest triple check of the build (tools/verify_show.py)
VENUE BASE PACKAGE           base/Plantagenet_Players_Base_2026_r1 - the venue rig on its own (base Mantra file,
                             QLab base, guide, printouts, previz)

THE SHOW
- The Mantra show is split by scene: P2 Act One, P3 Act Two, P4 the ten songs, P5 FX, P6-P7 looks, P8 backup.
  QLab fires every cue by page/memory/cue and releases each memory as it leaves it (31 releases).
- Flash returns are QLab pre-waits - no link times to type into the desk.
- Songs are QLab groups S1-S10 with {nsec} section GOs.
- The book is paged to the licensed script revised April 2026, with the 28 Sep 2026 casting.
- The 12 Lightsky C42s and the 3 pelmet PixBars are fixed. C42 jobs go by position: faces #1+4, #5+8,
  #9+12; SP2 #2, V1 #3, SP1 #6, V2 #7, SP4 #10, SP3 #11. Eight moves from the installed rig: Part B3.
- Lighting and sound review: white flash hits, one storm palette, house backlight, shell levels,
  starting sound levels, storm layer fades, looping house music (TLM_nov_2026_final_Lighting_Changes.pdf).

BOOK: 01_Production_Book/The_Little_Mermaid_Complete_Production_Book_{rev}.pdf
      (Includes Part J, the prompt copy with the licensed script - production use only.)
FIRST: 01_Production_Book/TLM_nov_2026_final_To_Find_and_Confirm.pdf - what is still to supply or decide.
SET-UP: 01_Production_Book/TLM_nov_2026_final_Setup_and_Startup_Quick_Guide.pdf (cards 6-7).

Rebuild everything in this folder with: python3 tools/book/build.py
"""

QLAB_README = """THE LITTLE MERMAID - Plantagenet Hall - QLab ({rev}, {date})

THE SHOW FOLDER: package/TLM_nov_2026_final  (copy it to the show Mac's Desktop with that exact name)
  {qlab}   {ncues} cues: {nmaster} master cue groups, songs S1-S10 ({nsec} section GOs), E1-E3 emergency
  media/audio, media/video, media/stills   80 files listed in TLM_nov_2026_final_MEDIA_MANIFEST.csv
  TLM_nov_2026_final_MANTRA_SECTION_MAP.csv              every Mantra target QLab fires
  TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv        show-control fixes, what is still to do

STEPS (Part E and the Quick Guide, card 6)
1. Run package/ASSEMBLE_TLM_nov_2026_final.command on the Mac - it unpacks the Drive zips into the show folder.
2. Open {qlab}. Workspace Settings:
     Audio  - Patch 1 -> StudioLive USB (outs 1-2 -> desk ch 11-12)
     Video  - Stage 1 -> projector
     Network - MANTRA patch (OSC, 2.0.0.1 port 8000) -> the wired Ethernet interface
3. Give E1 STOP ALL F15, E2 VID-99 BLACK F13, E3 SAFE LIGHT F14 (Triggers > Hotkey). Save.
4. On the Mantra add the OSC remote trigger: Play Memory, port 8000.
5. Supply the placeholder sounds (To Find and Confirm list) - save under NEW file names, drag onto the cue.

TLM_QLab_cue_list.csv   the {nmaster} master cues and 10 songs as a spreadsheet, with script pages (April 2026 script)

The workspace is already built - no scripts are needed. See Part L for the tech test run.
"""

MEMORY_MAP = """{mtr} - memory map ({rev}, {date})
Patch, custom fixtures, rig view and network as Plantagenet_Players_Base_2026_r1 (venue base). Desk opens on Page 2.
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
            part_j.build(path)
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
            if L in SEPARATE:
                rows.append((L, title + " — separate file (full-colour images)", n, "—"))
                continue
            rows.append((L, title, n, start))
            start += n
        part_00.build(cover, [("00", "Cover and Contents", ncover, 1)] + rows)
        ncover = pages(cover)
    print("00 %3d pages" % ncover)

    order = [("00 Cover and Contents", cover)] + [("%s %s" % (L, t), built[L]) for L, t, _s in PARTS if L not in SEPARATE]
    merge(order, os.path.join(BOOK, "TLM_nov_2026_final_Complete_Production_Book.pdf"))
    part_k.build_quick_guide(os.path.join(BOOK, "TLM_nov_2026_final_Setup_and_Startup_Quick_Guide.pdf"))
    to_find.build(os.path.join(BOOK, "TLM_nov_2026_final_To_Find_and_Confirm.pdf"))
    changes = lx_moves.build_changes(os.path.join(BOOK, "TLM_nov_2026_final_Lighting_Changes.pdf"))
    os.makedirs(os.path.join(OUT, "03_Lighting_Mantra"), exist_ok=True)
    shutil.copy(changes, os.path.join(OUT, "03_Lighting_Mantra", "TLM_nov_2026_final_Lighting_Changes.pdf"))
    shutil.copy(changes, os.path.join(PKG, "docs", "TLM_nov_2026_final_Lighting_Changes.pdf"))

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
    for f in ("TLM_nov_2026_final_MANTRA_SECTION_MAP.csv", "TLM_nov_2026_final_MANTRA_SECTION_MAP.txt"):
        shutil.copy(os.path.join(PKG, f), os.path.join(OUT, "03_Lighting_Mantra", f))
    shutil.copy(os.path.join(PKG, "TLM_nov_2026_final_MEDIA_MANIFEST.csv"), os.path.join(OUT, "02_QLab", "TLM_nov_2026_final_MEDIA_MANIFEST.csv"))
    backdrop_log(os.path.join(OUT, "06_Projection_Source", "Rights_Log", "Backdrop_Prompt_Log.csv"))

    # lighting plan copy and venue photos for 08_Venue_and_Rig
    shutil.copy(built["I2"], os.path.join(OUT, "06_Projection_Source", "%s_Backdrop_Sheets.pdf" % TAG))
    shutil.copy(built["B2"], os.path.join(OUT, "08_Venue_and_Rig", "%s_Stage_Lighting_Layout_Plan.pdf" % TAG))
    shutil.copy(built["B3"], os.path.join(OUT, "08_Venue_and_Rig", "%s_Rig_Move_Guide.pdf" % TAG))
    photos = os.path.join(ROOT, "production", "assets", "venue_photos")
    if os.path.isdir(photos):
        dst = os.path.join(OUT, "08_Venue_and_Rig", "Photos")
        os.makedirs(dst, exist_ok=True)
        for f in sorted(os.listdir(photos)):
            shutil.copy(os.path.join(photos, f), os.path.join(dst, f))

    # labels and the package printouts (same content, package names)
    sheets, labels = cue_sheets(os.path.join(PKG, "docs"))
    shutil.copy(labels, os.path.join(OUT, "03_Lighting_Mantra", "%s_Mantra_Labels.pdf" % TAG))
    print("package docs:", os.path.relpath(sheets, ROOT), os.path.relpath(labels, ROOT))


if __name__ == "__main__":
    main()
