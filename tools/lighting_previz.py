#!/usr/bin/env python3
"""Lighting previz: the R13.1 lighting drawn onto photos of the Plantagenet Hall stage.

Relights two photos taken from the house (tabs open, tabs closed) with every fixture's pool, wall
wash and haze beam, using the positions and focus in Part B / the layout plan (B2) and the colour
and level of every fixture in each look and cue of the Mantra show file. It is a sketch of where
the light lands, not a photometric simulation.

Writes one JPEG per render to OUT (default: scratchpad-style folder given on the command line) and
production/TLM_Show_R13_1/03_Lighting_Mantra/TLM_Lighting_Previz_R13_1.pdf:
  - the whole rig at full, and each look M01-M17
  - each fixture on its own, in open white, with where it hangs marked
  - every show cue as programmed (tabs open or closed as called), with its backdrop on the wall
  - every song section

Usage: python3 tools/lighting_previz.py [image_dir]      (needs numpy, pillow, reportlab)
"""
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "book"))
import make_printouts as mp  # noqa: E402
import show as S_  # noqa: E402
import part_b  # noqa: E402

PHOTOS = os.path.join(ROOT, "production", "assets", "venue_photos")
THUMBS = os.path.join(ROOT, "production", "assets", "thumbs")
OPEN_PHOTO = os.path.join(PHOTOS, "15_Stage_tabs_open_from_house.jpg")
CLOSED_PHOTO = os.path.join(PHOTOS, "16_Stage_tabs_closed_from_house.jpg")
PDF = os.path.join(ROOT, "production", "TLM_Show_R13_1", "03_Lighting_Mantra", "TLM_Lighting_Previz_R13_1.pdf")

W, H = 1288, 966            # output size (the photos are 2576 x 1932: every coordinate below is full-size / 2)
LW, LH = 644, 483           # light maps are built at half the output size and scaled up
SC = 0.5                    # full-size photo px -> output px
HAZE = 0.32                 # light haze for beam visibility
AMBIENT = 0.035
U_M, V_M = 4.5, 5.0         # metres per stage unit across (u: -1 SR .. +1 SL) and deep (v: 0 DS edge .. 1 back wall)

# Pelmet PixBar numbers are not known until the rig ID test: assume one per venue side group
PELMET_PIX = (33, 35, 37)
LX2_PIX = (34, 36, 38)

# Tabs closed for these cues (calls: Scene Two, Scene Four and Scene Nine play in front; preshow, interval, end)
CLOSED = {"1", "2", "3", "12", "13", "14", "15", "15.5", "16", "16.5", "17", "27.5", "28", "28.5", "29", "30",
          "30.5", "37", "38", "45", "58.5", "59", "59.5", "59.7", "63.5", "65", "S2", "S3", "S5"}


# --------------------------------------------------------------------------
# Geometry (full-size photo coordinates)
# --------------------------------------------------------------------------

class OpenStage:
    """Tabs open: floor trapezoid, painted back wall, red pelmet above."""
    yF, yB = 1455.0, 1318.0
    wall_px_per_m = 175.0

    def cx(self, v):
        return 1370.0 - 40.0 * v

    def hw(self, v):
        return 830.0 - 60.0 * v

    def floor_xy(self, u, v):
        return self.cx(v) + u * self.hw(v), self.yF + (self.yB - self.yF) * v

    def wall_xy(self, u, h):
        return self.cx(1) + u * self.hw(1), self.yB - h * self.wall_px_per_m

    def coords(self, xs, ys):
        """Per pixel: floor (u, v), wall (u, h) and region masks."""
        v = (self.yF - ys) / (self.yF - self.yB)
        u = (xs - self.cx(v)) / self.hw(v)
        people = (xs > 1985) & (ys > 1160)          # house floor in front of stage left (people in the photo)
        floor = (ys >= self.yB - 4) & (ys <= self.yF + 40) & (np.abs(u) <= 1.12) & ~people
        uw = (xs - self.cx(1)) / self.hw(1)
        hw_ = (self.yB - ys) / self.wall_px_per_m
        wall = (ys < self.yB + 4) & (ys > 690) & (np.abs(uw) <= 1.05) & ~people
        valance = (ys > 405) & (ys <= 700) & (xs > 525) & (xs < 2170) & REDNESS_FULL(xs, ys)
        return {"u": u, "v": np.clip(v, -0.4, 1.02), "floor": floor, "uw": uw, "h": hw_, "wall": wall,
                "valance": valance}


class ClosedStage:
    """Tabs closed: the house tabs and valance as one plane, the apron strip in front."""

    def s_of(self, xs):
        return (xs - 335.0) / 1555.0

    def ytop(self, s):
        return 445.0 + 150.0 * s

    def ybot(self, s):
        return 1525.0 - 130.0 * s

    def yfront(self, s):
        return 1550.0 - 110.0 * s

    def curtain_xy(self, u, h):
        s = (u + 1) / 2
        ppm = (self.ybot(s) - self.ytop(s)) / 4.3
        return 335.0 + 1555.0 * s, self.ybot(s) - h * ppm

    def apron_xy(self, u, w):
        s = (u + 1) / 2
        return 335.0 + 1555.0 * s, self.ybot(s) + w * (self.yfront(s) - self.ybot(s))

    def coords(self, xs, ys):
        s = self.s_of(xs)
        u = 2 * s - 1
        ppm = (self.ybot(s) - self.ytop(s)) / 4.3
        h = (self.ybot(s) - ys) / ppm
        curtain = (s >= 0) & (s <= 1) & (ys >= self.ytop(s)) & (ys <= self.ybot(s))
        w = (ys - self.ybot(s)) / (self.yfront(s) - self.ybot(s))
        apron = (s >= 0) & (s <= 1.07) & (w >= 0) & (w <= 1.15)
        return {"u": u, "h": h, "curtain": curtain, "w": w, "apron": apron}


OPEN, CLOSEDG = OpenStage(), ClosedStage()


def _redness():
    """Red velvet in the tabs-open photo (the pelmet), looked up by full-size photo coordinates."""
    im = np.asarray(Image.open(OPEN_PHOTO).convert("RGB"), np.float32)
    red = (im[..., 0] > 1.6 * im[..., 1] + 12)

    def look(xs, ys):
        xi = np.clip(xs.astype(int), 0, red.shape[1] - 1)
        yi = np.clip(ys.astype(int), 0, red.shape[0] - 1)
        return red[yi, xi]
    return look


REDNESS_FULL = _redness()


# --------------------------------------------------------------------------
# Fixtures: focus from Part B, drawn as pools, wall washes and beams
# --------------------------------------------------------------------------

ZONE = {"DSR": (-0.62, 0.2), "DSC": (0.0, 0.2), "DSL": (0.62, 0.2),
        "CSR": (-0.62, 0.55), "CSC": (0.0, 0.55), "CSL": (0.62, 0.55)}
# performer marks from the layout plan (u across, v deep)
MARK = {2: (-0.66, 0.2), 3: (-0.7, 0.32), 6: (0.0, 0.2), 7: (-0.36, 0.32), 10: (0.0, 0.5), 11: (0.66, 0.55),
        19: (0.36, 0.41), 20: (0.7, 0.41)}
FACE = {1: ("DSR", +1), 4: ("DSR", -1), 5: ("DSC", +1), 8: ("DSC", -1), 9: ("DSL", +1), 12: ("DSL", -1)}


def foh_src(n):
    return 260 + (n - 1) * 186.0, -260.0          # FOH bar is in the house ceiling, above the camera


def fixture_parts(n):
    """[(kind, params)] for fixture n. Kinds: floor, wall, valance, beam, curtain, apron."""
    parts = []
    t = part_b.FOCUS[[f[0] for f in part_b.FOCUS].index(n)][1] if n in [f[0] for f in part_b.FOCUS] else ""
    if n in FACE:
        z, side = FACE[n]
        u, v = ZONE[z]
        parts += [("floor", (u, v, 1.9, 1.5, "hard", 0.95)),
                  ("wall", (u + 0.14 * side, 1.5, 1.4, 1.3, 0.45)),
                  ("valance", (u, 0.10)),
                  ("beam", (foh_src(n), ("floor", u, v), 30, 170, 0.35)),
                  ("curtain", (u + 0.12 * side, 1.5, 1.7, 1.4, 0.85)),
                  ("apron", (u, 0.5, 1.9, 0.60))]
    elif n in MARK and t == "C42":
        u, v = MARK[n]
        tall = 3.2 if n == 11 else 1.4
        parts += [("floor", (u, v, 0.8, 0.8, "hard", 1.0)),
                  ("wall", (u, 1.2, 0.5, 0.6, 0.10)),
                  ("beam", (foh_src(n), ("floor", u, v), 14, 60, 0.30)),
                  ("curtain", (u, 1.3, 0.75, 1.0, 0.75)),
                  ("apron", (u, 0.45, 0.8, 0.7))]
    elif 13 <= n <= 18:
        u, v = ZONE[["DSR", "DSC", "DSL", "CSR", "CSC", "CSL"][n - 13]]
        sx, sy = OPEN.floor_xy(u, 0.12)
        parts += [("floor", (u, v, 2.3, 1.9, "soft", 0.75)),
                  ("wall", (u, 0.7 if v < 0.4 else 0.4, 1.8, 1.0, 0.25 if v < 0.4 else 0.45)),
                  ("beam", ((sx, 700.0), ("floor", u, v), 40, 230, 0.45))]
    elif n in (19, 20):
        u, v = MARK[n]
        sx, _ = OPEN.floor_xy(u, 0.8)
        parts += [("floor", (u, v, 0.9, 0.8, "hard", 0.85)),
                  ("beam", ((sx, 745.0), ("floor", u, v), 10, 70, 0.75))]
    elif 23 <= n <= 28:
        u, v = ZONE[["DSR", "DSC", "DSL", "CSR", "CSC", "CSL"][n - 23]]
        sx, _ = OPEN.floor_xy(u, 0.85)
        parts += [("floor", (u, v - 0.1, 2.1, 1.9, "soft", 0.5)),
                  ("wall", (u, 0.15, 1.6, 0.35, 0.18)),
                  ("beam", ((sx, 745.0), ("floor", u, v - 0.1), 26, 230, 1.0))]
    elif n in (21, 22, 29, 30, 31, 32):
        side = -1 if n in (21, 29, 30) else 1
        height = {21: 2.8, 22: 2.8, 29: 1.2, 31: 1.2, 30: 0.4, 32: 0.4}[n]
        gain = {2.8: 0.34, 1.2: 0.42, 0.4: 0.55}[height]
        fx, fy = OPEN.floor_xy(1.03 * side, 0.45)
        sy = fy - height * 175.0
        tx, ty = OPEN.floor_xy(-0.6 * side, 0.45)
        parts += [("sidefloor", (side, 0.45, 1.0, gain)),
                  ("wall", (-0.85 * side, height + 0.3, 1.0, 0.9, 0.10)),
                  ("beam", ((fx, sy), (tx, ty - (height * 120 if height > 1 else 30)), 18, 170, 0.9))]
    elif n in LX2_PIX:
        u = {34: -0.6, 36: 0.0, 38: 0.6}[n]
        sx, _ = OPEN.floor_xy(u, 0.9)
        parts += [("floor", (u, 0.78, 2.2, 1.1, "soft", 0.32)),
                  ("wall", (u, 0.2, 2.2, 0.45, 0.25)),
                  ("beam", ((sx, 752.0), ("floor", u, 0.6), 60, 260, 0.55))]
    elif n in PELMET_PIX:
        u = {33: -0.6, 35: 0.0, 37: 0.6}[n]
        parts += [("floor", (u, 0.02, 2.4, 0.9, "soft", 0.45)),
                  ("valance", (u, 0.35)),
                  ("curtain", (u, 3.2, 1.5, 2.1, 0.75)),
                  ("apron", (u, 0.4, 2.2, 0.35))]
    elif n == 39:
        parts += [("floor", (0.72, 0.55, 1.6, 1.4, "soft", 0.35)),
                  ("beam", ((1990.0, 760.0), ("floor", 0.72, 0.55), 20, 160, 0.8))]
    return parts


def gauss_d2(d2, hard):
    if hard == "hard":
        return np.clip((1.0 - d2) / 0.28, 0, 1) ** 1.5 * 0.92 + np.exp(-2.2 * d2) * 0.08
    return np.exp(-1.7 * d2)


class Masks:
    """Per-fixture light maps at LW x LH for one stage view, cached."""

    def __init__(self, geom, closed):
        ys, xs = np.mgrid[0:LH, 0:LW].astype(np.float32)
        full = 1.0 / (SC * LW / W)      # light-map px -> full-size photo px
        self.fx, self.fy = xs * full, ys * full
        self.geom, self.closed = geom, closed
        self.c = geom.coords(self.fx, self.fy)
        self.cache = {}

    def beam(self, src, tgt, w0, w1):
        (sx, sy), (tx, ty) = src, tgt
        dx, dy = tx - sx, ty - sy
        L2 = dx * dx + dy * dy
        t = np.clip(((self.fx - sx) * dx + (self.fy - sy) * dy) / L2, 0, 1)
        px, py = sx + t * dx, sy + t * dy
        dist = np.hypot(self.fx - px, self.fy - py)
        width = w0 + (w1 - w0) * t
        return np.exp(-(dist / width) ** 2 * 2.0) * (0.35 + 0.65 * t)

    def get(self, n):
        if n in self.cache:
            return self.cache[n]
        light = np.zeros((LH, LW), np.float32)
        beam = np.zeros((LH, LW), np.float32)
        c = self.c
        for kind, p in fixture_parts(n):
            if not self.closed:
                if kind == "floor":
                    u0, v0, ru, rv, hard, g = p
                    d2 = ((c["u"] - u0) * U_M / ru) ** 2 + ((c["v"] - v0) * V_M / rv) ** 2
                    light += np.where(c["floor"], gauss_d2(d2, hard) * g, 0)
                elif kind == "sidefloor":
                    side, v0, rv, g = p
                    across = np.clip(1.0 - 0.45 * (c["u"] * side + 1), 0.2, 1)   # brighter near the boom
                    d2 = ((c["v"] - v0) * V_M / rv) ** 2
                    light += np.where(c["floor"], np.exp(-1.4 * d2) * across * g, 0)
                elif kind == "wall":
                    u0, h0, ru, rh, g = p
                    d2 = ((c["uw"] - u0) * U_M / ru) ** 2 + ((c["h"] - h0) / rh) ** 2
                    light += np.where(c["wall"], np.exp(-1.6 * d2) * g, 0)
                elif kind == "valance":
                    u0, g = p
                    light += np.where(c["valance"], np.exp(-((c["uw"] - u0) * 1.2) ** 2) * g, 0)
                elif kind == "beam":
                    src, tgt, w0, w1, g = p
                    if tgt[0] == "floor":
                        tgt = OPEN.floor_xy(tgt[1], tgt[2])
                    beam += self.beam(src, tgt, w0, w1) * g
            else:
                if kind == "curtain":
                    u0, h0, ru, rh, g = p
                    d2 = ((c["u"] - u0) * U_M / ru) ** 2 + ((c["h"] - h0) / rh) ** 2
                    light += np.where(c["curtain"], np.exp(-1.5 * d2) * g, 0)
                elif kind == "apron":
                    u0, w0, ru, g = p
                    d2 = ((c["u"] - u0) * U_M / ru) ** 2
                    light += np.where(c["apron"], np.exp(-1.6 * d2) * g, 0)
                elif kind == "beam" and n <= 12:
                    src, tgt, w0, w1, g = p
                    u = tgt[1] if tgt[0] == "floor" else 0
                    beam += self.beam(src, CLOSEDG.curtain_xy(u, 1.5), w0, w1) * g * 0.6
        self.cache[n] = (light, beam)
        return light, beam


# --------------------------------------------------------------------------
# Programmed colour and level for every fixture in a look or cue
# --------------------------------------------------------------------------

_t = open(mp.MTR, encoding="latin-1").read()
_secs = re.split(r"^\[([^\]]+)\]\s*$", _t, flags=re.M)
MTR = {_secs[i]: _secs[i + 1] for i in range(1, len(_secs), 2)}


def state_of(mem_id, k):
    """{fixture: (level 0-1, (r, g, b) 0-1)} for Memory mem_id cue k."""
    sec = MTR.get("Memory%d-Cue%d" % (mem_id, k), "")
    kv = dict(l.split("=", 1) for l in sec.splitlines() if "=" in l)
    out = {}
    for key, v in kv.items():
        m = re.match(r"Channel(\d+)_Level$", key)
        if not m:
            continue
        n, lvl = int(m.group(1)), int(v) / 65535
        if lvl <= 0:
            continue
        col = int(kv.get("Channel%d_Colour" % n, "4294967295")) & 0xFFFFFF
        rgb = np.array([(col >> 16) & 255, (col >> 8) & 255, col & 255], np.float32) / 255
        white = int(kv.get("Channel%d_attr_val_WHITE" % n, "0")) / 65535
        amber = int(kv.get("Channel%d_attr_val_AMBER" % n, "0")) / 65535
        rgb = rgb + white * np.array([1.0, 0.96, 0.9]) + amber * np.array([1.0, 0.62, 0.1]) * 0.7
        peak = float(rgb.max()) or 1.0
        out[n] = (lvl * min(1.0 + 0.35 * white, 1.35), rgb / peak)
    return out, kv.get("Name", "")


def mem_id(p, m):
    return S_.PAGE_LAYOUT[p][m]


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def load_photo(path):
    im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


ALB_OPEN, ALB_CLOSED = load_photo(OPEN_PHOTO), load_photo(CLOSED_PHOTO)
# the painted back wall: where the tabs-open photo is bright inside the opening
_lum = ALB_OPEN.mean(axis=2)
_ys, _xs = np.mgrid[0:H, 0:W]
WALLMASK = ((_lum > 0.16) & (_xs > 540 * SC) & (_xs < 1548 * SC) & (_ys > 700 * SC) & (_ys < 1322 * SC)).astype(np.float32)
M_OPEN, M_CLOSED = Masks(OPEN, False), Masks(CLOSEDG, True)


def up(a):
    return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize((W, H), Image.BILINEAR))


def projection(bg):
    if not bg:
        return None
    f = next((x for x in os.listdir(THUMBS) if x.startswith(bg + "_")), None)
    if not f:
        return None
    img = Image.open(os.path.join(THUMBS, f)).convert("RGB")
    pw, ph = int(1400 * SC), int(788 * SC)
    img = img.resize((pw, ph), Image.LANCZOS)
    canvas = np.zeros((H, W, 3), np.float32)
    x0, y0 = int((1320 - 700) * SC), int((1318 - 788) * SC)
    a = np.asarray(img, np.float32) / 255
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    canvas[y0:y0 + ph, x0:x0 + pw] = a
    return canvas * WALLMASK[..., None]


def render(state, closed=False, bg=None, haze=HAZE, mark=None):
    """state: {fixture: (level, rgb)}. Returns a PIL image."""
    masks = M_CLOSED if closed else M_OPEN
    alb = ALB_CLOSED if closed else ALB_OPEN
    light = np.zeros((3, LH, LW), np.float32)
    beams = np.zeros((3, LH, LW), np.float32)
    for n, (lvl, rgb) in state.items():
        parts = masks.get(n)
        if parts is None:
            continue
        L, B = parts
        for k in range(3):
            light[k] += L * lvl * rgb[k]
            beams[k] += B * lvl * rgb[k]
    lit = np.stack([up(light[k]) for k in range(3)], axis=-1) + AMBIENT
    out = alb * lit
    if bg and not closed:
        pr = projection(bg)
        if pr is not None:
            out += pr * 0.55
    out += np.stack([up(beams[k]) for k in range(3)], axis=-1) * haze * 0.16
    out = np.clip(out, 0, 1)
    srgb = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
    im = Image.fromarray((srgb * 255 + 0.5).astype(np.uint8), "RGB")
    if mark:
        d = ImageDraw.Draw(im)
        for (x, y, label) in mark:
            x, y = x * SC, y * SC
            inside = 0 <= y <= H
            yy = min(max(y, 14), H - 14)
            d.ellipse([x - 9, yy - 9, x + 9, yy + 9], outline=(255, 214, 90), width=3)
            d.text((x + 13, yy - 7), label + ("" if inside else " (above)"), fill=(255, 214, 90), font=FONT)
    return im


try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
except OSError:
    FONT = ImageFont.load_default()


def source_marker(n):
    t = part_b.FOCUS[[f[0] for f in part_b.FOCUS].index(n)][1]
    if n <= 12:
        x, _ = foh_src(n)
        return [(x, 40, "#%d FOH bar" % n)]
    for kind, p in fixture_parts(n):
        if kind == "beam":
            (sx, sy) = p[0]
            return [(sx, sy, "#%d" % n)]
    if n in PELMET_PIX:
        u = {33: -0.6, 35: 0.0, 37: 0.6}[n]
        return [(OPEN.floor_xy(u, 0)[0], 420, "#%d pelmet" % n)]
    return None


# --------------------------------------------------------------------------
# What to render
# --------------------------------------------------------------------------

POSITION = {n: pos for n, _t, pos, _a, _r in part_b.FOCUS}
ROLE = {n: r for n, _t, _p, _a, r in part_b.FOCUS}
TYPE = {n: t for n, t, _p, _a, _r in part_b.FOCUS}
TYPENAME = {"C42": "Lightsky C42", "ZM": "Tour Pro Zoom", "COB": "TourCOB PAR", "PIX": "PixBar", "HAZE": "Hazer"}
WHITE = np.array([1.0, 1.0, 1.0], np.float32)


def jobs():
    out = []
    rig = [n for n in range(1, 40)]
    out.append(("whole", "full", "Whole rig at full", "Every fixture at 100 % open white, tabs open",
                {n: (1.0, WHITE) for n in rig}, False, None, None))
    out.append(("whole", "full-closed", "Tabs closed, rig at full", "Only the FOH bar and the pelmet PixBars reach the tabs",
                {n: (1.0, WHITE) for n in rig}, True, None, None))
    for mid in range(50, 67):
        st, name = state_of(mid, 0)
        out.append(("look", "look-%s" % name.split()[0], name, "Look library P%d M%d" % (6 if mid < 60 else 7,
                    (mid - 49) if mid < 60 else (mid - 59)), st, False, None, None))
    for n in range(1, 41):
        if n == 40:
            st = {k: (0.6, WHITE) for k in (1, 4, 5, 8, 9, 12, 23, 24, 25, 26, 27, 28)}
            out.append(("fixture", "fx-40", "#40 Hazer", "Hazer on the upstage floor: the same backlight with no haze "
                        "and with haze", st, False, None, None))
            continue
        where = POSITION[n] + (" (assumed #%s on the pelmet)" % n if n in PELMET_PIX else
                               " (assumed on LX2)" if n in LX2_PIX else "")
        out.append(("fixture", "fx-%02d" % n, "#%d %s" % (n, TYPENAME.get(TYPE[n], TYPE[n])),
                    "%s · %s" % (where, ROLE[n]), {n: (1.0, WHITE)}, n <= 12 and False, None, source_marker(n)))
    for c in S_.CUES:
        if not c["lx"]:
            continue
        bg = (c["video"] or [None])[-1] or last_bg(c["num"])
        for i, x in enumerate(c["lx"]):
            st, name = state_of(mem_id(x["p"], x["m"]), x["c"] - 1)
            flash = len(c["lx"]) > 1 and i == 0 and c["lx"][1].get("pre")
            key = "q-%s%s" % (c["num"], "-flash" if flash else "")
            title = "Q%s %s%s" % (c["num"], c["name"], " — flash" if flash else "")
            out.append(("cue", key, title, "%s · P%d M%d cue %d · %s" % (name, x["p"], x["m"], x["c"],
                        "tabs closed" if c["num"] in CLOSED else "tabs open" + (" · %s" % bg if bg else "")),
                        st, c["num"] in CLOSED, None if c["num"] in CLOSED else bg, None))
    for s in S_.SONGS:
        bg = last_bg(s["at"])
        for x in s["sections"]:
            st, name = state_of(mem_id(x["p"], x["m"]), x["c"] - 1)
            out.append(("song", "s-%s" % x["num"], "%s %s" % (x["num"], x["name"] or ""),
                        "%s · %s · P4 M%d cue %d" % (s["title"], name, x["m"], x["c"]), st, s["num"] in CLOSED,
                        None if s["num"] in CLOSED else bg, None))
    return out


def last_bg(num):
    """Backdrop on the wall at cue num (the last VIDEO fired at or before it)."""
    bg = None
    for c in S_.CUES:
        if c["video"]:
            bg = c["video"][-1]
        if c["num"] == num:
            break
    return bg


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    index = []
    for group, key, title, sub, st, closed, bg, mark in jobs():
        if key == "fx-40":
            a = render(st, haze=0.0)
            b = render(st, haze=1.1)
            im = Image.new("RGB", (W, H))
            im.paste(a.crop((0, 0, W // 2, H)), (0, 0))
            im.paste(b.crop((W // 2, 0, W, H)), (W // 2, 0))
            ImageDraw.Draw(im).line([(W // 2, 0), (W // 2, H)], fill=(255, 214, 90), width=2)
        else:
            im = render(st, closed=closed, bg=bg, mark=mark)
        f = key.replace(".", "_") + ".jpg"
        im.save(os.path.join(outdir, f), quality=80, optimize=True)
        index.append({"group": group, "key": key, "file": f, "title": title, "sub": sub, "closed": closed,
                      "bg": bg or ""})
    json.dump(index, open(os.path.join(outdir, "index.json"), "w"), indent=1)
    build_pdf(outdir, index)
    print("%d renders -> %s\n%s" % (len(index), outdir, PDF))


def build_pdf(outdir, index):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for name, f in (("Sans", "DejaVuSans.ttf"), ("Sans-Bold", "DejaVuSans-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(name, "/usr/share/fonts/truetype/dejavu/" + f))
    pw, ph = landscape(A4)
    small = os.path.join(outdir, "pdf")
    os.makedirs(small, exist_ok=True)

    def thumb(it, width):
        f = os.path.join(small, "%d_%s" % (width, it["file"]))
        if not os.path.exists(f):
            im = Image.open(os.path.join(outdir, it["file"]))
            im.resize((width, width * H // W), Image.LANCZOS).save(f, quality=70, optimize=True)
        return f

    c = canvas.Canvas(PDF, pagesize=(pw, ph))
    c.setTitle("TLM R13.1 Lighting Previz")
    heads = {"whole": "The whole rig and the look library", "look": "The whole rig and the look library",
             "fixture": "Each fixture on its own (open white, 100 %)", "cue": "Every cue as programmed",
             "song": "Song sections"}

    def page_head(title, n):
        c.setFont("Sans-Bold", 13)
        c.drawString(14 * mm, ph - 13 * mm, title)
        c.setFont("Sans", 7.5)
        c.drawString(14 * mm, ph - 18 * mm, "The Little Mermaid · Plantagenet Hall · R13.1 lighting previz — a sketch of where "
                     "the light lands, drawn on photos of the stage; check every look in the venue.")
        c.drawRightString(pw - 14 * mm, 8 * mm, "Lighting Previz · page %d" % n)

    # cover
    page = 1
    c.setFont("Sans-Bold", 26)
    c.drawString(14 * mm, ph - 30 * mm, "Lighting Previz")
    c.setFont("Sans", 11)
    c.drawString(14 * mm, ph - 38 * mm, "The Little Mermaid · Plantagenet Hall · R13.1 · the lighting drawn on the stage")
    full = next(i for i in index if i["key"] == "full")
    c.drawImage(thumb(full, 1000), 14 * mm, 30 * mm, width=168 * mm, height=126 * mm)
    c.setFont("Sans", 8.5)
    y = ph - 52 * mm
    for line in ["How to read it", "",
                 "Each picture relights a photo of the stage", "taken from the house. Pools on the floor and",
                 "the back wall show where each fixture lands;", "faint beams show it in light haze.", "",
                 "Colours and levels are read from the show file", "for every look, cue and song section.", "",
                 "Tabs closed (preshow, Scenes Two, Four and", "Nine, interval, end): only the FOH bar and the",
                 "pelmet PixBars reach the tabs; the rest of the", "rig and the projection are behind them.", "",
                 "Assumed until the rig ID test: pelmet PixBars", "#33, #35, #37 and LX2 PixBars #34, #36, #38.", "",
                 "Nobody is on stage in the photos, so face", "light shows as pools, not on faces."]:
        c.setFont("Sans-Bold" if line == "How to read it" else "Sans", 9 if line == "How to read it" else 8.5)
        c.drawString(190 * mm, y, line)
        y -= 4.6 * mm
    c.drawRightString(pw - 14 * mm, 8 * mm, "Lighting Previz · page 1")
    c.showPage()

    groups = [("whole", 4), ("look", 4), ("fixture", 4), ("cue", 4), ("song", 9)]
    for g, per in groups:
        items = [i for i in index if i["group"] == g]
        cols = 2 if per == 4 else 3
        rows = per // cols
        gw = (pw - 28 * mm - (cols - 1) * 6 * mm) / cols
        gh = gw * H / W
        for k in range(0, len(items), per):
            page += 1
            page_head(heads[g], page)
            for j, it in enumerate(items[k:k + per]):
                col, row = j % cols, j // cols
                x = 14 * mm + col * (gw + 6 * mm)
                ytop = ph - 24 * mm - row * (gh + (13 if per == 4 else 10) * mm)
                c.drawImage(thumb(it, 760 if per == 4 else 480), x, ytop - gh, width=gw, height=gh)
                c.setFont("Sans-Bold", 8.5 if per == 4 else 7)
                c.drawString(x, ytop - gh - 4 * mm, it["title"][:80])
                c.setFont("Sans", 7 if per == 4 else 5.8)
                c.drawString(x, ytop - gh - 7.6 * mm, it["sub"][:118 if per == 4 else 80])
            c.showPage()
    c.save()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "production", "TLM_Show_R13_1", "03_Lighting_Mantra",
                                                             "Previz"))
