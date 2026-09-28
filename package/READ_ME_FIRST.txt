THE LITTLE MERMAID - R13.1 SHOW PACKAGE  (Plantagenet Hall, 28 Sep 2026)
========================================================================

This package is the one download for R13.1. It holds the EDITED show
control files (QLab 5 workspace, Mantra show, maps, manifest, fix list,
review PDF, the new Q19.2 rain burst) already in the correct folder layout,
plus a script that drops the media in around them.

The media is not inside this zip; it's too large to send this way. The
script pulls it from the three zips in your Drive folder TLM_R13.

STEPS (on the show Mac)
 1. Unzip this package anywhere, e.g. Downloads/TLM_R13_1_Package.
 2. From Drive > TLM_R13, download into that same folder:
        TLM_R13_1.zip   TLM_R13_1_SFX.zip   TLM_Backdrops_R10.zip
    (links in SOURCE_ZIPS.csv). Do NOT let Safari unzip them.
 3. Double-click ASSEMBLE_R13_1.command.
    If macOS blocks it: right-click > Open, or in Terminal run
        bash ~/Downloads/TLM_R13_1_Package/ASSEMBLE_R13_1.command
 4. It builds OUTPUT/TLM_R13_REBUILT_Show_Files and checks:
      - all 80 media files QLab uses are at the exact paths it expects
      - the QLab and Mantra files match the checked R13.1 checksums
      - whether an old TLM_R11_FLASHY_Show_Files folder is still around
    Results go in OUTPUT/ASSEMBLY_REPORT.txt.
 5. Move OUTPUT/TLM_R13_REBUILT_Show_Files to the Desktop (keep that exact
    name), open TLM_Show_R13_1.qlab5 and carry on from step 3 of
    00_START_HERE.txt inside it.

FINAL FOLDER LAYOUT
 TLM_R13_REBUILT_Show_Files/
   00_START_HERE.txt
   TLM_Show_R13_1.qlab5                       <- open this
   TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr   <- import on Mantra
   BUILD_METADATA.json
   R13_MEDIA_MANIFEST.csv   R13_MANTRA_SECTION_MAP.csv/.txt
   R13_1_SFX_RETARGET_MAP.csv   R13_1_QLAB_AND_DESK_FIX_LIST.csv
   docs/            review PDF, R13 guide & book, R9 book, archive_R13_original
   media/
     audio/
       00_SFX_Pack_2026-09-28_originals/   (untouched pack sources, reference)
       01_Music_Songs/                     S01-S10
       02_House_and_Interval_Music/        Q1 Q2 Q37 Q38 Q65
       03_Underscore/
       04_Ambience_Beds/
       05_Storm/
       06_Magic/
       07_Stings_and_Comedy/
       08_Voice_Recordings/                Q42.5
     stills/
     video/

See R13_1_REVIEW_NOTES.txt for what was checked and what is still to do.
