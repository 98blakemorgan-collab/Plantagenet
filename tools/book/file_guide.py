"""The File Guide: every file in the R13.1 build, what it is, who uses it and when — plus the build check.

Scans the real folders (package/, base/, production/TLM_nov_2026_final/, tools/) so nothing is missed; each file is
described by DESCRIBE. tools/verify_show.py fails if a file has no description here.

Usage: python3 tools/book/file_guide.py      (run after tools/verify_show.py, so the results are current)
"""
import fnmatch
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from core import PartDoc, title_block, stats, box, table, H1, H2, P, steps, REV, DATE, mm  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "production", "TLM_nov_2026_final", "TLM_nov_2026_final_File_Guide.pdf")
PKG_COPY = os.path.join(ROOT, "package", "TLM_nov_2026_final", "docs", "TLM_nov_2026_final_File_Guide.pdf")
CHECK = os.path.join(ROOT, "production", "TLM_nov_2026_final", "TLM_nov_2026_final_Build_Check")
PKG_CHECK = os.path.join(ROOT, "package", "TLM_nov_2026_final_BUILD_CHECK.txt")

# pattern (relative to its area) -> (what it is, who / when)
DESCRIBE = {
    # ---- package/ -------------------------------------------------------------------------------------------
    "package/READ_ME_FIRST.txt": ("How to turn this package into the show folder on the show Mac", "QLab op — first"),
    "package/ASSEMBLE_TLM_nov_2026_final.command": ("Assembler: merges the media from the three Drive zips around the control files, "
                                       "places all 80 media files and checks the four control-file checksums",
                                       "QLab op — double-click once"),
    "package/SOURCE_ZIPS.csv": ("Links to the three Drive media zips the assembler needs", "QLab op — before assembling"),
    "package/TLM_nov_2026_final_REVIEW_NOTES.txt": ("What was checked and changed in each round, and what is still to do", "Production / LX"),
    "package/TLM_nov_2026_final_BUILD_CHECK.txt": ("The latest triple check of the whole build (tools/verify_show.py)", "Anyone — before tech"),
    "package/TLM_nov_2026_final/00_START_HERE.txt": ("Show-Mac setup steps and the list of show files",
                                                             "QLab op / LX — setup"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final.qlab5": ("THE QLab 5 show workspace: 479 cues, every sound, "
                                                                "backdrop and lighting GO", "QLab op — every show"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final.mtr": (
        "THE Mantra show file: P2 Act One, P3 Act Two, P4 songs, P5 FX, P6–P7 looks, P8 backup; built on the venue base",
        "LX — import on the desk"),
    "package/TLM_nov_2026_final/BUILD_METADATA.json": ("Checksums of the show QLab and Mantra files and the "
                                                               "history of every change", "Checking a copy"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final_MEDIA_MANIFEST.csv": ("The 80 media files QLab uses, by exact path",
                                                                  "Assembler / QLab op"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final_MANTRA_SECTION_MAP.csv": ("Every Mantra position: page, memory, cue, name, "
                                                                      "fade, the QLab cue that fires it, P8 backup "
                                                                      "position", "LX — backup running"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final_MANTRA_SECTION_MAP.txt": ("The page/section layout and flash returns in plain "
                                                                      "text", "LX"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final_SFX_RETARGET_MAP.csv": ("Which new SFX file each audio cue plays, its "
                                                                      "length and what it was built from", "Sound"),
    "package/TLM_nov_2026_final/TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv": ("Done / to-do list for QLab, the desk and the "
                                                                            "rig", "Production / LX"),
    "package/TLM_nov_2026_final/docs/TLM_nov_2026_final_Operator_Cue_Sheets.pdf": ("SM calls, QLab GO list, Mantra backup, "
                                                                                  "haze/FX and deck sheets", "Operators — print"),
    "package/TLM_nov_2026_final/docs/TLM_nov_2026_final_Mantra_Labels.pdf": ("Show fader labels, playback rows, reminder "
                                                                            "strips, page tabs", "LX — print"),
    "package/TLM_nov_2026_final/docs/TLM_nov_2026_final_Zoom_Adjustment.pdf": ("How to set zoom on the Zooms #13–22, with a "
                                                                              "record sheet", "LX — focus"),
    "package/TLM_nov_2026_final/docs/TLM_nov_2026_final_Review_and_Fix_List.pdf": ("The R13.1 review and fix list as "
                                                                                  "supplied", "Reference"),
    "package/TLM_nov_2026_final/docs/TLM_nov_2026_final_Lighting_Changes.pdf": ("Every lighting change: programming fixes, "
                                                                               "fixed FOH jobs, rig moves, files",
                                                                               "LX / production"),
    "package/TLM_nov_2026_final/docs/TLM_nov_2026_final_File_Guide.pdf": ("This guide", "Everyone"),
    "package/TLM_nov_2026_final/docs/FOH_Flashing_Lights_and_Haze_Notice.pdf": ("A4 notice for the doors: flashing "
                                                                                         "lights and haze", "FOH — print and post"),
    "package/TLM_nov_2026_final/media/*": ("Bundled placeholder sounds (10) and the Q19.2 rain burst; the rest of "
                                                   "the media comes from the Drive zips", "Assembler"),
    # ---- base/ ------------------------------------------------------------------------------------------------
    "base/Plantagenet_Players_Base_2026_r1/00_READ_ME_FIRST.txt": ("What the base package is and the first steps", "LX / venue"),
    "base/Plantagenet_Players_Base_2026_r1/Plantagenet_Players_Base_2026_r1.*": ("The venue base Mantra file and its QLab base (their only home: "
                                                     "not in the show package)", "LX / venue"),
    "base/Plantagenet_Players_Base_2026_r1/BASE_METADATA.json": ("Checksums of the two base files", "Checking a copy"),
    "base/Plantagenet_Players_Base_2026_r1/docs/Plantagenet_Players_Base_2026_r1_Guide.pdf": ("The base guide: rig as installed, addresses, "
                                                                          "venue looks, QLab base cues, how to", "LX / venue — start here"),
    "base/Plantagenet_Players_Base_2026_r1/docs/Plantagenet_Players_Base_2026_r1_Preview.pdf": ("The base lighting drawn on photos of the stage",
                                                                           "Everyone"),
    "base/Plantagenet_Players_Base_2026_r1/docs/Plantagenet_Players_Base_2026_r1_*.pdf": ("Base link map, desk labels and rig ID test", "LX — rig day"),
    # ---- production/ ------------------------------------------------------------------------------------------
    "production/TLM_nov_2026_final/00_START_HERE.txt": ("Map of the show folder and what changed", "Everyone"),
    "production/TLM_nov_2026_final/TLM_nov_2026_final_File_Guide.pdf": ("This guide", "Everyone"),
    "production/TLM_nov_2026_final/TLM_nov_2026_final_Build_Check.*": ("The latest triple check of the build (text and data)", "Anyone"),
    "production/TLM_nov_2026_final/*/_ABOUT_THIS_FOLDER.txt": ("What belongs in this folder", "Everyone"),
    "production/TLM_nov_2026_final/*/*/_ABOUT_THIS_FOLDER.txt": ("What belongs in this folder", "Everyone"),
    "production/TLM_nov_2026_final/01_Production_Book/TLM_nov_2026_final_Complete_Production_Book.pdf": (
        "The complete production book, Parts 00–L in one PDF (I2 backdrop sheets kept separate)", "Everyone"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_00_*": ("Book cover and contents", "Everyone"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_A_*": ("Part A: master technical production manual "
                                                                             "and risks", "Production / TD"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_B_*": ("Part B: lighting design, rig, looks, songs, "
                                                                             "focus plan", "LX"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_B2_*": ("Part B2: stage lighting layout plan (A3)",
                                                                              "LX / venue"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_B3_*": ("Part B3: rig move guide", "LX crew — rig day"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_C_*": ("Part C: DMX patch, network, power, patch "
                                                                             "procedure", "LX"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_D_*": ("Part D: Mantra programming guide and every "
                                                                             "cue as programmed", "LX"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_E_*": ("Part E: QLab 5 guide, songs, sound files, "
                                                                             "levels", "QLab op / sound"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_F_*": ("Part F: operator cue sheets", "Operators"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_G_*": ("Part G: DSM calling script", "DSM"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_H_*": ("Part H: props list and preset sheets", "Props / deck"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_I_*": ("Part I: projection backgrounds", "Projection"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_I2_*": ("Part I2: one page per backdrop", "Projection"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_J_*": ("Part J: prompt copy (licensed script) — "
                                                                             "production use only", "DSM"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_K_*": ("Part K: quick reference cards", "Operators"),
    "production/TLM_nov_2026_final/01_Production_Book/Sections/TLM_nov_2026_final_L_*": ("Part L: Stream Deck and tech test run",
                                                                             "QLab op"),
    "production/TLM_nov_2026_final/01_Production_Book/TLM_nov_2026_final_Lighting_Changes.pdf": ("Every lighting change in one "
                                                                                    "document", "LX / production"),
    "production/TLM_nov_2026_final/01_Production_Book/TLM_nov_2026_final_Setup_and_Startup_Quick_Guide.pdf": ("Setup and start-up "
                                                                                                 "quick guide", "Operators"),
    "production/TLM_nov_2026_final/01_Production_Book/TLM_nov_2026_final_To_Find_and_Confirm.pdf": ("Everything still to find, supply "
                                                                                       "or decide", "Production — now"),
    "production/TLM_nov_2026_final/02_QLab/README.txt": ("Where the QLab show folder lives and how it is laid out", "QLab op"),
    "production/TLM_nov_2026_final/02_QLab/TLM_QLab_cue_list.csv": ("Every master cue and song as a spreadsheet, with script "
                                                                "pages", "SM / QLab op"),
    "production/TLM_nov_2026_final/02_QLab/TLM_nov_2026_final_MEDIA_MANIFEST.csv": ("Copy of the 80-file media manifest", "QLab op"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/TLM_nov_2026_final_memory_map.txt": ("Mantra pages, memories and look library in "
                                                                              "plain text", "LX"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/TLM_nov_2026_final_MANTRA_SECTION_MAP.*": ("Copies of the section map", "LX"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/TLM_nov_2026_final_Mantra_Labels.pdf": ("Show desk labels", "LX — print"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/TLM_nov_2026_final_Zoom_Adjustment.pdf": ("Zoom adjustment sheet", "LX — focus"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/Plantagenet_Players_Base_2026_r1_*.pdf": ("Venue base link map, labels, rig ID test",
                                                                          "LX — rig day"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/TLM_nov_2026_final_Lighting_Changes.pdf": ("Every lighting change (copy)", "LX"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/TLM_nov_2026_final_Lighting_Previz.pdf": ("Show lighting previz: whole rig, "
                                                                                   "looks, each fixture, every cue and song",
                                                                                   "Everyone"),
    "production/TLM_nov_2026_final/03_Lighting_Mantra/Plantagenet_Players_Base_2026_r1_Preview.pdf": ("Venue base lighting preview",
                                                                                       "Everyone"),
    "production/TLM_nov_2026_final/06_Projection_Source/TLM_nov_2026_final_Backdrop_Sheets.pdf": ("Backdrop sheets (copy of Part I2)",
                                                                                     "Projection"),
    "production/TLM_nov_2026_final/06_Projection_Source/Rights_Log/Backdrop_Prompt_Log.csv": ("How each backdrop was made "
                                                                                          "(rights log)", "Producer"),
    "production/TLM_nov_2026_final/08_Venue_and_Rig/TLM_nov_2026_final_Stage_Lighting_Layout_Plan.pdf": ("Layout plan (copy of B2)",
                                                                                           "LX / venue"),
    "production/TLM_nov_2026_final/08_Venue_and_Rig/TLM_nov_2026_final_Rig_Move_Guide.pdf": ("Rig move guide (copy of B3)", "LX crew"),
    "production/TLM_nov_2026_final/08_Venue_and_Rig/Photos/*": ("Venue and rig photos", "Everyone"),
}

TOOLS = [("tools/verify_show.py", "Triple check of the whole build (files, show logic, paperwork)", "After any change"),
         ("tools/book/build.py", "Builds the production book, sections, cue list, maps and printouts", "After any change"),
         ("tools/make_base_printouts.py", "Base link map, desk labels, rig ID test", "After a base or rig change"),
         ("tools/make_zoom_sheet.py", "Zoom adjustment sheet", "After a rig change"),
         ("tools/lighting_previz.py", "Lighting previz renders and PDF (show; --base for the venue base)",
          "After a lighting change"),
         ("tools/build_base_package.py", "The separate venue base package and its guide", "After a base change"),
         ("tools/book/file_guide.py", "This guide", "Last"),
         ("tools/build_package.sh", "Zips the show package for download", "Last"),
         ("tools/apply_lx_sound_edits.py", "The lighting and sound review edits (already applied, guarded by checksum)",
          "History"),
         ("tools/apply_fixed_foh_jobs.py", "The fixed-FOH C42 job move (already applied, guarded by checksum)", "History"),
         ("tools/make_qlab_base.py", "Builds Plantagenet_Players_Base_2026_r1.qlab5 from the base and the show workspace settings",
          "Only if the base changes"),
         ("tools/check_mantra_base.py", "Checks the venue base still matches the show file", "Run by verify_show.py"),
         ("tools/make_printouts.py", "Show cue sheets and desk labels (called by the book build)", "Via build.py")]

AREAS = [("1 The show package — package/", "package"),
         ("2 The venue base package — base/Plantagenet_Players_Base_2026_r1/", "base"),
         ("3 The production folder — production/TLM_nov_2026_final/", "production/TLM_nov_2026_final")]


def describe(rel):
    if rel in DESCRIBE:
        return DESCRIBE[rel]
    for pat, v in DESCRIBE.items():
        if fnmatch.fnmatch(rel, pat):
            return v
    return None


def files_of(area):
    out = []
    for dp, _dn, fs in os.walk(os.path.join(ROOT, area)):
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(dp, f), ROOT)
            if "__pycache__" in rel:
                continue
            out.append(rel)
    return sorted(out)


def undocumented():
    return [r for _t, a in AREAS for r in files_of(a) if describe(r) is None]


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024


def build(path=OUT):
    if os.path.exists(CHECK + ".txt"):
        shutil.copy(CHECK + ".txt", PKG_CHECK)
    d = PartDoc(path, "", "File Guide", divider=False)
    d.add(title_block("%s · %s" % (REV, DATE), "File Guide",
                      "Every file in the Little Mermaid build — what it is, who uses it and when — and the latest "
                      "triple check"))
    counts = {t: len(files_of(a)) for t, a in AREAS}
    results = json.load(open(CHECK + ".json")) if os.path.exists(CHECK + ".json") else []
    fails = [r for r in results if r["status"] == "FAIL"]
    d.add(stats([(str(counts[AREAS[0][0]]), "files in the show package"), (str(counts[AREAS[1][0]]), "in the base package"),
                 (str(counts[AREAS[2][0]]), "in the production folder"),
                 ("%d/%d" % (sum(r["status"] == "OK" for r in results), len(results)), "build checks passed")]))
    d.add(box("rule", "HOW THE BUILD FITS TOGETHER",
              ["**The show folder is the one source for the show.** package/TLM_nov_2026_final holds the QLab "
               "workspace, the Mantra show file and their maps. The assembler adds the media from Drive to make the "
               "folder that goes on the show Mac's Desktop.",
               "**The venue base package** (base/Plantagenet_Players_Base_2026_r1, its own zip) is the venue's rig on its own: the "
               "base Mantra file and QLab base with their guide, printouts and previz. It is not in the show package; "
               "the show file is built on it and checked to match.",
               "**The production folder** holds the book, printouts, plans and previz, all rebuilt from the show files by "
               "the tools, so the paperwork always matches the files."]))

    d.add(H1("Build check"))
    if results:
        d.add(P("From tools/verify_show.py (full text: TLM_nov_2026_final_Build_Check.txt; a copy is in the package as "
                "TLM_nov_2026_final_BUILD_CHECK.txt). **Result: %s** — %d checks, %d failed."
                % ("PASS" if not fails else "FAIL", len(results), len(fails))))
        names = {1: "Files", 2: "The show", 3: "Paperwork"}
        d.add(table(["", "Check", "Result", "Detail"],
                    [[r["id"], names[r["pass"]] + " · " + r["title"], "**%s**" % r["status"], r["detail"][:170]]
                     for r in results], [10 * mm, 62 * mm, 14 * mm, 84 * mm],
                    tints=[(i, "crit") for i, r in enumerate(results) if r["status"] == "FAIL"]))
    else:
        d.add(P("Run tools/verify_show.py, then rebuild this guide."))

    for title, area in AREAS:
        d.add(H1(title))
        rows = []
        for rel in files_of(area):
            what, who = describe(rel) or ("(not described)", "")
            name = os.path.relpath(rel, area)
            if "/Photos/" in rel or "/media/" in rel:
                continue
            rows.append([name, what, who, human(os.path.getsize(os.path.join(ROOT, rel)))])
        grouped = [r for r in files_of(area) if "/Photos/" in r or "/media/" in r]
        if grouped:
            rows.append([os.path.dirname(os.path.relpath(grouped[0], area)).split("/")[0] + "/…  (%d files)" % len(grouped),
                         describe(grouped[0])[0], describe(grouped[0])[1],
                         human(sum(os.path.getsize(os.path.join(ROOT, g)) for g in grouped))])
        d.add(table(["File", "What it is", "Who / when", "Size"], rows, [62 * mm, 70 * mm, 26 * mm, 12 * mm]))

    d.add(H1("4 The tools and the rebuild order"))
    d.add(table(["Tool", "What it does", "When"], [list(t) for t in TOOLS], [52 * mm, 88 * mm, 30 * mm]))
    d.add(H2("Rebuild everything after a change"))
    d.add(steps(["python3 tools/book/build.py — the book, sections, cue list, maps, show printouts",
                 "python3 tools/make_base_printouts.py and python3 tools/make_zoom_sheet.py",
                 "python3 tools/lighting_previz.py, then python3 tools/lighting_previz.py --base",
                 "python3 tools/build_base_package.py — the venue base package and its zip "
                 "(dist/Plantagenet_Players_Base_2026_r1.zip)",
                 "python3 tools/verify_show.py — the triple check (must PASS)",
                 "python3 tools/book/file_guide.py — this guide, with the new results",
                 "bash tools/build_package.sh — the show package zip (dist/TLM_nov_2026_final.zip)"]))

    d.add(H1("5 Checksums of the control files"))
    meta = dict(json.load(open(os.path.join(ROOT, "package", "TLM_nov_2026_final", "BUILD_METADATA.json")))["sha256"])
    bm = os.path.join(ROOT, "base", "Plantagenet_Players_Base_2026_r1", "BASE_METADATA.json")
    if os.path.exists(bm):
        meta.update(json.load(open(bm))["sha256"])
    names = {"qlab": "TLM_nov_2026_final.qlab5", "mantra": "TLM_nov_2026_final.mtr",
             "mantra_base": "Plantagenet_Players_Base_2026_r1.mtr (base package)", "qlab_base": "Plantagenet_Players_Base_2026_r1.qlab5 (base package)"}
    d.add(table(["File", "SHA-256"], [[names[k], v] for k, v in meta.items() if k in names], [64 * mm, 106 * mm]))
    d.build()
    os.makedirs(os.path.dirname(PKG_COPY), exist_ok=True)
    shutil.copy(path, PKG_COPY)
    return path


if __name__ == "__main__":
    missing = undocumented()
    if missing:
        print("Not described in DESCRIBE:\n  " + "\n  ".join(missing))
    print(build())
