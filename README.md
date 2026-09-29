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
- `tools/check_mantra_base.py` — checks that the venue base `BASE_SHOW_2026.mtr`
  still matches the R13.1 Mantra show file (patch, fixtures, network, rig view,
  P1 looks, memories 100–109).

Start with `package/READ_ME_FIRST.txt` and `package/R13_1_REVIEW_NOTES.txt`.
