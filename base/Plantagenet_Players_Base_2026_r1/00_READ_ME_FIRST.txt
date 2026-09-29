PLANTAGENET HALL - VENUE BASE  (Plantagenet_Players_Base_2026_r1, 28 September 2026)
=======================================================

The venue's lighting rig on its own, separate from The Little Mermaid show.

  Plantagenet_Players_Base_2026_r1.mtr     Mantra venue base: patch, fixtures, network, rig
                         view, venue looks P1 and memories 100-109.
                         No show cues. Import it to put the desk back to
                         the venue, or to run the rig check.
  Plantagenet_Players_Base_2026_r1.qlab5   QLab base that fires it: V1-V10 venue looks,
                         I1-I5 rig ID (one type at a time), T1-T41 rig test
                         (one fixture per GO), E1-E3 emergency.
                         Only use it with Plantagenet_Players_Base_2026_r1.mtr on the desk.
  BASE_METADATA.json     checksums of the two files
  docs/                  Venue Base Guide (start here), link map, desk
                         labels, rig ID test, base lighting preview

FIRST
  1. Read docs/Plantagenet_Players_Base_2026_r1_Guide.pdf.
  2. Mantra: export the current show to USB, then Home > Tools > Import
     Show > Plantagenet_Players_Base_2026_r1.mtr.
  3. QLab: open Plantagenet_Players_Base_2026_r1.qlab5, Workspace Settings > Network >
     MANTRA -> wired Ethernet. Mantra remote trigger: OSC, Play Memory,
     port 8000.
  4. Rig day: print docs/Plantagenet_Players_Base_2026_r1_Rig_ID_Test.pdf and run I1-I4,
     then T1-T40.

The 12 Lightsky C42s (FOH bar) and the 3 PixBars on the pelmet front are
fixed and cannot be moved. FOH dimmer channels feeding the C42s: NON-DIM.

Checksums (SHA-256)
  Plantagenet_Players_Base_2026_r1.mtr    e273d54b71abb69bc9e2c6d5b431ebb5ceb09e22673f6b67d082fbfc66c63076
  Plantagenet_Players_Base_2026_r1.qlab5  35cf343d1870a12dd1218a6e0a8a85fa60b1b60d760c7f60a96014bf45d3e4ba

This base is separate from the show package (TLM_nov_2026_final.zip) and is
not included in it. The show file is built on this base: its patch,
fixtures, network, rig view, venue looks and memories 100-109 are checked
to be identical (tools/check_mantra_base.py).
