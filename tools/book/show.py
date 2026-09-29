"""R13.1 show data, read straight from the show files in the package.

Everything the book states about cues, Mantra positions, songs and media comes
from here, so the book always matches TLM_Show_R13_1.qlab5 and
TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import make_printouts as mp  # noqa: E402

SHOW = mp.SHOW
QLAB_NAME = os.path.basename(mp.QLAB)
MTR_NAME = os.path.basename(mp.MTR)
FOLDER = os.path.basename(SHOW)

_groups = [mp.parse_group(g) for g in mp.load_qlab()]
MEMS = mp.load_mtr()
MAP_ROWS, BY_PMC = mp.load_map()

SHOWGROUPS = [g for g in _groups if g["num"] and not g["num"].startswith("E") and g["num"] != "66"]
EMERGENCY = [g for g in _groups if g["num"].startswith("E")]


def _page(trigger):
    m = re.search(r"\(p(\d+)\)", trigger)
    return m.group(1) if m else ""


def _lx_targets(g):
    return [x for x in g["mantra"] if x["p"] in (2, 3, 4)]


CUES = []      # master cues (numbered groups, not songs)
SONGS = []     # song groups S1..S10
_prev = None
for g in SHOWGROUPS:
    f = g["f"]
    if g["num"].startswith("S"):
        secs = mp.song_sections(g["notes"])
        at = re.search(r"At show cue Q(\S+)", g["notes"])
        mus = re.search(r"\((MUS-[A-Z0-9-]+)\)", g["notes"])
        track_kind = re.search(r"Track: ([^|]+)", g["notes"])
        artist = g["notes"].split(" | ")[0]
        track_title, track_file = g["track"] if g["track"] else ("", "")
        status = "supplied"
        if "swap for backing" in track_file:
            status = "vocal version - swap for backing" if "if vocal" not in track_file else "check for vocals"
        if "TBA" in track_file or "to be decided" in track_title.lower():
            status = "song still to choose (silent placeholder)"
        sections = []
        for x in g["mantra"]:
            r = BY_PMC.get((x["p"], x["m"], x["c"]), {})
            sections.append({"num": x["num"], "name": secs.get(x["num"], ""), "p": x["p"], "m": x["m"],
                             "c": x["c"], "fade": x["fade"], "pos": r.get("Backup Position", ""),
                             "desk": r.get("Cue Name", "")})
        SONGS.append({"num": g["num"], "title": mp.song_title(g), "credit": artist,
                      "at": at.group(1).lstrip("0") if at else "", "mus": mus.group(1) if mus else "",
                      "track_kind": track_kind.group(1).strip() if track_kind else "",
                      "file": track_file, "status": status, "mem": sections[0]["m"] if sections else 0,
                      "sections": sections, "release": g["release"]})
        if _prev is not None:
            _prev["song"] = g["num"]
        continue
    lx = []
    for x in _lx_targets(g):
        r = BY_PMC.get((x["p"], x["m"], x["c"]), {})
        lx.append(dict(x, pos=r.get("Backup Position", ""), desk=r.get("Cue Name", "")))
    fx5 = [x for x in g["mantra"] if x["p"] == 5]
    c = {"num": g["num"], "name": g["name"], "trigger": f.get("Trigger", ""), "look": f.get("LX", ""),
         "sound": f.get("Sound", ""), "fx": f.get("FX", ""), "page": _page(f.get("Trigger", "")),
         "video": [v for v in g["video"] if v], "audio": g["audio"], "lx": lx, "fx5": fx5,
         "release": g["release"], "fades": g["fades"], "song": None,
         "critical": mp.is_critical(g), "haze": mp.haze_mark(f.get("FX", "")),
         "water": mp.water_mark(f.get("FX", ""))}
    CUES.append(c)
    _prev = c

CUE = {c["num"]: c for c in CUES}
SONG = {s["num"]: s for s in SONGS}
FLASHES = [(c["num"], x) for c in CUES for x in c["lx"] if x["pre"]]

# Page 2 / Page 3 scene sections from the section map
SECTIONS = []
for (p, m) in sorted({(int(r["Performance Page"]), int(r["Playback Memory"])) for r in MAP_ROWS}):
    rows = [r for r in MAP_ROWS if int(r["Performance Page"]) == p and int(r["Playback Memory"]) == m]
    SECTIONS.append({"p": p, "m": m, "first": rows[0]["Cue Name"], "last": rows[-1]["Cue Name"],
                     "count": len(rows), "pos": (rows[0]["Backup Position"], rows[-1]["Backup Position"]),
                     "mem_id": int(rows[0]["Internal Memory ID"])})

# Page/memory -> internal memory id (from the section map layout)
PAGE_LAYOUT = {1: {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 9: 8, 10: 9},
               2: {1: 10, 2: 11, 3: 12, 4: 13, 5: 14, 6: 15, 9: 18, 10: 19},
               3: {k: 19 + k for k in range(1, 7)},
               4: {k: 29 + k for k in range(1, 11)},
               5: {k: 39 + k for k in range(1, 7)},
               6: {k: 49 + k for k in range(1, 11)},
               7: {k: 59 + k for k in range(1, 8)},
               8: {1: 70}}


def mem(page, m):
    return MEMS.get(PAGE_LAYOUT.get(page, {}).get(m), {})


MANIFEST = list(csv.DictReader(open(os.path.join(SHOW, "R13_MEDIA_MANIFEST.csv"), newline="")))
SFX_MAP = list(csv.DictReader(open(os.path.join(SHOW, "R13_1_SFX_RETARGET_MAP.csv"), newline="")))
FIXLIST = list(csv.DictReader(open(os.path.join(SHOW, "R13_1_QLAB_AND_DESK_FIX_LIST.csv"), newline="")))
PLACEHOLDER_CUES = ["S7", "Q1", "Q2", "Q11", "Q37", "Q38", "Q42.5", "Q43", "Q59", "Q65"]

# Backgrounds actually used, in show order: code -> (file, first cue)
BACKGROUNDS = {}
for c in CUES:
    for v in c["video"]:
        BACKGROUNDS.setdefault(v, c["num"])

TOTAL_QLAB_CUES = 479
N_MASTER = len(CUES)
N_POINT = len([c for c in CUES if "." in c["num"] or c["num"].endswith("b")])
N_SONG_SECTIONS = sum(len(s["sections"]) for s in SONGS)
N_POSITIONS = len(MAP_ROWS)
N_RELEASES = sum(len(c["release"]) for c in CUES) + sum(len(s["release"]) for s in SONGS)


# --------------------------------------------------------------------------
# Programmed colour and level for every look and cue, read from the .mtr
# --------------------------------------------------------------------------
import colorsys  # noqa: E402

_t = open(mp.MTR, encoding="latin-1").read()
_secs = re.split(r"^\[([^\]]+)\]\s*$", _t, flags=re.M)
_D = {_secs[i]: _secs[i + 1] for i in range(1, len(_secs), 2)}

GROUPS = [("FOH", "Face (FOH C42 #1, 4, 5, 8, 9, 12)", [1, 4, 5, 8, 9, 12]),
          ("LX1", "Colour top (LX1 Zoom #13–18)", list(range(13, 19))),
          ("SIDE", "Side booms (#21–22, 29–32)", [21, 22, 29, 30, 31, 32]),
          ("BACK", "Backlight (LX2 COB #23–28, 39)", [23, 24, 25, 26, 27, 28, 39]),
          ("PIX", "PixBars (#33–38)", list(range(33, 39))),
          ("SPC", "Specials (#2, 3, 6, 7, 10, 11, 19, 20)", [2, 3, 6, 7, 10, 11, 19, 20])]


def mtr_cue(mem_id, k):
    """Fixture -> (level %, 'RRGGBB') for one recorded cue."""
    sec = _D.get("Memory%d-Cue%d" % (mem_id, k))
    if sec is None:
        return None, {}
    kv = dict(l.split("=", 1) for l in sec.splitlines() if "=" in l)
    fx = {}
    for key, v in kv.items():
        m = re.match(r"Channel(\d+)_(Level|Colour)$", key)
        if m:
            fx.setdefault(int(m.group(1)), {})[m.group(2)] = int(v)
    out = {i: (round(v.get("Level", 0) * 100 / 65535), "%06X" % (v.get("Colour", 0) & 0xFFFFFF))
           for i, v in fx.items()}
    return kv.get("Name", ""), out


def colour_name(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    if s < 0.12:
        return "cool white" if b > r + 0.03 else ("white" if abs(r - b) < 0.03 else "warm white")
    if s < 0.35:
        if 15 <= h < 60:
            return "warm white" if h < 40 else "straw"
        if 180 <= h < 260:
            return "cool white" if s < 0.25 else "steel blue"
        if 260 <= h < 300:
            return "lavender"
    names = [(10, "red"), (22, "coral"), (38, "orange"), (52, "gold"), (70, "yellow"), (95, "lime"),
             (150, "green"), (172, "teal"), (195, "cyan"), (215, "sky blue"), (240, "blue"),
             (262, "deep blue"), (285, "violet"), (305, "purple"), (325, "magenta"), (345, "hot pink"),
             (361, "red")]
    for lim, n in names:
        if h < lim:
            return n
    return "red"


def group_summary(fx):
    """{group: (max level, [(hex, name) distinct, most common first])}"""
    out = {}
    for key, _, ids in GROUPS:
        lit = [fx[i] for i in ids if i in fx and fx[i][0] > 0]
        if not lit:
            out[key] = (0, [])
            continue
        counts = {}
        for lv, hx in lit:
            counts[hx] = counts.get(hx, 0) + 1
        cols = sorted(counts, key=lambda h: -counts[h])
        out[key] = (max(lv for lv, _ in lit), [(h, colour_name(h)) for h in cols])
    return out


LOOKS = []  # look library M01–M17 as programmed
for mid in range(50, 67):
    name, fx = mtr_cue(mid, 0)
    LOOKS.append({"id": name.split(" ")[0], "name": name, "page": 6 if mid < 60 else 7,
                  "mem": (mid - 49) if mid < 60 else (mid - 59), "summary": group_summary(fx), "fx": fx})


def position_summary(p, m, c):
    mid = PAGE_LAYOUT[p][m]
    name, fx = mtr_cue(mid, c - 1)
    return name, group_summary(fx), fx
