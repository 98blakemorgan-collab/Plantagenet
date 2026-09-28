# TLM R13.1 previz

A video walk-through of the show: every QLab GO in running order, with the
Mantra lighting looks, backdrop cues and running audio for each one.

    pip install numpy pillow imageio-ffmpeg
    python3 score_data.py                                   # -> score.json
    python3 render_previz.py --still 204.7 --out frame.png  # check a frame
    python3 render_previz.py --start 200 --end 215 --out sample.mp4
    python3 render_previz.py --parts 4                      # -> TLM_R13_1_previz.mp4

- `qlab_read.py` decodes the QLab 5 workspace (a nested NSKeyedArchiver plist).
- `score_data.py` reads `package/TLM_R13_REBUILT_Show_Files`: the QLab cue list
  (groups, pre-waits, auto-continues, OSC to Mantra, audio/video/fade cues) and
  the Mantra `.mtr` (patch, rig view positions, every memory cue's per-fixture
  colour and level, chases). Each GO gets a fixed slot (4.5 s scenes, 3 s song
  steps, longer when a fade or flash return needs it), about 10 minutes in all.
- `render_previz.py` draws the rig from the Mantra rig view, lights each fixture
  with the memories QLab has up (HTP, crossfaded with the OSC fade times, chases
  stepped at their BPM, haze from the hazer channel), and shows the current GO,
  memories, audio and next cues. The backdrop panel is a stand-in labelled with
  the QLab video/still name, as that media is not in the repo. The video is silent.
