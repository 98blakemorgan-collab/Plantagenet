# The Little Mermaid — R13.1 show package (Plantagenet Hall)

Source for the single R13.1 download package.

- `package/` — contents of the package: the edited R13.1 show control files
  in the correct `TLM_nov_2026_final` layout, the
  `ASSEMBLE_TLM_nov_2026_final.command` script that merges in the media from the three
  Drive zips, and the read-me / review notes.
- `tools/build_package.sh` — builds `dist/TLM_nov_2026_final_Package.zip`.
- `tools/make_printouts.py` — rebuilds the R13.1 operator cue sheets and Mantra
  labels in `docs/` from the QLab workspace, Mantra file and section map
  (`pip install reportlab`).
- `tools/apply_lx_sound_edits.py` — the lighting and sound review edits to the
  Mantra and QLab files (white flash hits, one storm palette, house backlight,
  shell levels, starting sound levels, storm layer fades, looping house music).
  Already applied; it refuses to run on anything but the original R13.1 files.
- `tools/apply_fixed_foh_jobs.py` — the 12 Lightsky C42s are fixed on the FOH bar in
  number order and cannot be moved, so their jobs go by position (faces #1+4, #5+8,
  #9+12; specials #2, 3, 6, 7, 10, 11) and the show programming moves with each job.
  Already applied; the venue base is untouched.
- `tools/book/lx_moves.py` — Part B3 Rig Move Guide (what moves from the installed rig,
  kit, order of work, safety, test and focus) and `TLM_nov_2026_final_Lighting_Changes.pdf`
  (every lighting change in one document). Built by `tools/book/build.py`.
- `tools/lighting_previz.py` — draws the lighting onto photos of the stage (tabs open /
  closed): the whole rig, every look, each fixture on its own, every cue and song section,
  with colours and levels from the show file. Writes the renders and
  `03_Lighting_Mantra/TLM_nov_2026_final_Lighting_Previz.pdf` (`pip install numpy pillow reportlab`).
- `tools/make_qlab_base.py` — builds `Plantagenet_Players_Base_2026_r1.qlab5`, the QLab base for the
  Mantra venue base, from `Plantagenet_Players_Base_2026_r1.mtr` and the R13.1 workspace settings.
- `tools/make_base_printouts.py` — builds the base show link map (QLab cue → Mantra
  page/memory → fixture → fader/DMX), base label sheet and rig ID test in `docs/`.
- `tools/make_zoom_sheet.py` — builds the zoom adjustment sheet for the Tour Pro
  Zooms #13–22 (where zoom lives, the stored values, a fill-in table).
- `tools/check_mantra_base.py` — checks that the venue base `Plantagenet_Players_Base_2026_r1.mtr`
  still matches the R13.1 Mantra show file (patch, fixtures, network, rig view,
  P1 looks, memories 100–109), and that `Plantagenet_Players_Base_2026_r1.qlab5` fires exactly its
  P1–P5 memories.

- `base/Plantagenet_Players_Base_2026_r1/` — the venue base package on its own (base Mantra file,
  QLab base, guide, printouts, previz); `tools/build_base_package.py` builds it and
  `dist/Plantagenet_Players_Base_2026_r1.zip`.
- `tools/verify_show.py` — the triple check of the whole build (files, show logic,
  paperwork); writes `production/TLM_nov_2026_final/TLM_nov_2026_final_Build_Check.txt`.
- `tools/book/file_guide.py` — `TLM_nov_2026_final_File_Guide.pdf`: every file, what it is and
  who uses it, with the build check.

**On the show Mac:** download `INSTALL_TLM_nov_2026_final.command` and run it
(`bash ~/Downloads/INSTALL_TLM_nov_2026_final.command`). It fetches the build files from
GitHub and the three media zips from Drive, builds `TLM_nov_2026_final` (show) and
`Plantagenet_Players_Base_2026_r1` (venue base), checks everything and puts both on the
Desktop.

Start with `package/READ_ME_FIRST.txt` and `package/TLM_nov_2026_final_REVIEW_NOTES.txt`.
