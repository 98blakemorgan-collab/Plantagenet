# The Little Mermaid — R13.1 show package (Plantagenet Hall)

Source for the single R13.1 download package.

- `package/` — contents of the package: the edited R13.1 show control files
  in the correct `TLM_R13_REBUILT_Show_Files` layout, the
  `ASSEMBLE_R13_1.command` script that merges in the media from the three
  Drive zips, and the read-me / review notes.
- `tools/build_package.sh` — builds `dist/TLM_R13_1_Package.zip`.
- `tools/make_printouts.py` — rebuilds the R13.1 operator cue sheets and Mantra
  labels in `docs/` from the QLab workspace, Mantra file and section map
  (`pip install reportlab`).
- `tools/make_qlab_base.py` — builds `BASE_SHOW_2026.qlab5`, the QLab base for the
  Mantra venue base, from `BASE_SHOW_2026.mtr` and the R13.1 workspace settings.
- `tools/make_base_printouts.py` — builds the base show link map (QLab cue → Mantra
  page/memory → fixture → fader/DMX) and base label sheet in `docs/`.
- `tools/check_mantra_base.py` — checks that the venue base `BASE_SHOW_2026.mtr`
  still matches the R13.1 Mantra show file (patch, fixtures, network, rig view,
  P1 looks, memories 100–109), and that `BASE_SHOW_2026.qlab5` fires exactly its
  P1–P5 memories.

Start with `package/READ_ME_FIRST.txt` and `package/R13_1_REVIEW_NOTES.txt`.
