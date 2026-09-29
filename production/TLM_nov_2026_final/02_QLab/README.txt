THE LITTLE MERMAID - Plantagenet Hall - QLab (R13.1, 28 September 2026)

THE SHOW FOLDER: package/TLM_nov_2026_final  (copy it to the show Mac's Desktop with that exact name)
  TLM_nov_2026_final.qlab5   479 cues: 83 master cue groups, songs S1-S10 (66 section GOs), E1-E3 emergency
  media/audio, media/video, media/stills   80 files listed in TLM_nov_2026_final_MEDIA_MANIFEST.csv
  TLM_nov_2026_final_MANTRA_SECTION_MAP.csv              every Mantra target QLab fires
  TLM_nov_2026_final_QLAB_AND_DESK_FIX_LIST.csv        show-control fixes, what is still to do

STEPS (Part E and the Quick Guide, card 6)
1. Run package/ASSEMBLE_TLM_nov_2026_final.command on the Mac - it unpacks the Drive zips into the show folder.
2. Open TLM_nov_2026_final.qlab5. Workspace Settings:
     Audio  - Patch 1 -> StudioLive USB (outs 1-2 -> desk ch 11-12)
     Video  - Stage 1 -> projector
     Network - MANTRA patch (OSC, 2.0.0.1 port 8000) -> the wired Ethernet interface
3. Give E1 STOP ALL F15, E2 VID-99 BLACK F13, E3 SAFE LIGHT F14 (Triggers > Hotkey). Save.
4. On the Mantra add the OSC remote trigger: Play Memory, port 8000.
5. Supply the placeholder sounds (To Find and Confirm list) - save under NEW file names, drag onto the cue.

TLM_QLab_cue_list.csv   the 83 master cues and 10 songs as a spreadsheet, with script pages (April 2026 script)

The workspace is already built - no scripts are needed. See Part L for the tech test run.
