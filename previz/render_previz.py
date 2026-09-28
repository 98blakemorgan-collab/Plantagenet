"""Render the TLM R13.1 previz video from score.json (built by score_data.py).

  python3 render_previz.py --still 322.7 --out frame.png      one frame
  python3 render_previz.py --start 0 --end 20 --out test.mp4  a short sample
  python3 render_previz.py --parts 4 --out previz.mp4         the full show

Stage view: the Mantra rig drawn from its RigView positions, each fixture's
beam and floor pool in the colour/level the running memories give it
(additive, crossfaded with the OSC fade times QLab sends). The backdrop panel
stands in for the QLab video/still (the media itself is not in the repo).
Right panel: current GO, lighting memory, audio running, next cues.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1280, 720
SW, SH = 880, 560          # stage view
PANEL_X = SW
STRIP_Y = SH               # timeline strip below the stage
FLOOR_Y = 470
BG = (10, 12, 18)
INK = (230, 232, 240)
DIM = (130, 136, 150)
ACCENT = (255, 190, 90)


def font(size, bold=False):
    names = (['DejaVuSans-Bold.ttf'] if bold else ['DejaVuSans.ttf'])
    for d in ('/usr/share/fonts/truetype/dejavu', '/usr/share/fonts/dejavu', ''):
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_BIG = font(54, True)
F_MED = font(20, True)
F_TXT = font(16)
F_SM = font(13)
F_XS = font(11)


# ---------------------------------------------------------------- engine ---
class Lighting:
    """Evaluates every Mantra memory's contribution at any time t."""

    def __init__(self, score):
        self.nfix = len(score['fixtures'])
        self.mem = {}
        for mid, m in score['memories'].items():
            looks = []
            for c in m['cues']:
                arr = np.zeros((self.nfix, 3), np.float32)
                for ch, (rgb, lvl) in c['look'].items():
                    ch = int(ch)
                    if ch < self.nfix:
                        arr[ch] = np.array(rgb, np.float32) / 255.0 * lvl
                looks.append(arr)
            self.mem[int(mid)] = {'chase': m['chase'], 'bpm': m['bpm'], 'looks': looks,
                                  'names': [c['name'] for c in m['cues']], 'ev': []}
        events = []
        for s in score['steps']:
            for a in s['actions']:
                if a['type'] == 'mantra':
                    events.append((s['t'] + a['at'], a))
        events.sort(key=lambda e: e[0])
        for te, a in events:
            m = self.mem[a['mem']]
            prev_lvl = self._level(m, te)
            from_look = self._look(m, te) if prev_lvl > 0.01 else None
            if a['level'] > 0:
                cue = min(a['cue'], len(m['looks']) - 1)
                m['ev'].append({'t': te, 'fade': a['fade'], 'l0': prev_lvl, 'l1': a['level'],
                                'cue': cue, 'from': from_look})
            else:
                m['ev'].append({'t': te, 'fade': a['fade'], 'l0': prev_lvl, 'l1': 0.0,
                                'cue': None, 'from': None})
        self.active_mems = [mid for mid, m in self.mem.items() if m['ev']]

    @staticmethod
    def _last(m, t):
        last = None
        for e in m['ev']:
            if e['t'] <= t:
                last = e
            else:
                break
        return last

    def _level(self, m, t):
        e = self._last(m, t)
        if e is None:
            return 0.0
        k = 1.0 if e['fade'] <= 0 else min(1.0, (t - e['t']) / e['fade'])
        return e['l0'] + (e['l1'] - e['l0']) * k

    def _cue_at(self, m, t):
        """(cue index, event start) of the cue the memory is showing."""
        cue, start = None, None
        for e in m['ev']:
            if e['t'] > t:
                break
            if e['cue'] is not None:
                cue, start = e['cue'], e['t']
        return cue, start

    def _look(self, m, t):
        cue, start = self._cue_at(m, t)
        if cue is None:
            return np.zeros((self.nfix, 3), np.float32)
        if m['chase']:
            step = int((t - start) * m['bpm'] / 60.0) % len(m['looks'])
            return m['looks'][step]
        e = [x for x in m['ev'] if x['t'] <= t and x['cue'] is not None][-1]
        to = m['looks'][cue]
        if e['from'] is None or e['fade'] <= 0 or t >= e['t'] + e['fade']:
            return to
        k = (t - e['t']) / e['fade']
        return e['from'] + (to - e['from']) * k

    def at(self, t):
        total = np.zeros((self.nfix, 3), np.float32)
        live = []
        for mid in self.active_mems:
            m = self.mem[mid]
            lvl = self._level(m, t)
            if lvl <= 0.002:
                continue
            total = np.maximum(total, self._look(m, t) * lvl)  # HTP per colour
            cue, _ = self._cue_at(m, t)
            live.append((mid, lvl, m['names'][cue] if cue is not None else ''))
        return total, live


class Media:
    """Which audio and backdrop cues are running at time t."""

    def __init__(self, score):
        self.audio, self.video = [], []
        stops = {}
        for s in score['steps']:
            for a in s['actions']:
                if a['type'] == 'stop':
                    stops.setdefault(a['id'], []).append(s['t'] + a['at'] + a['fade'])
        for s in score['steps']:
            for a in s['actions']:
                t0 = s['t'] + a['at']
                end = min([x for x in stops.get(a.get('id'), []) if x > t0] or [1e9])
                if a['type'] == 'audio':
                    if not a['loop'] and a['len'] > 0:
                        end = min(end, t0 + a['len'])
                    self.audio.append((t0, end, a))
                elif a['type'] == 'video':
                    self.video.append((t0, end, a))

    def audio_at(self, t):
        return [(t0, e, a) for t0, e, a in self.audio if t0 <= t < e]

    def video_at(self, t):
        cur = [(t0, e, a) for t0, e, a in self.video if t0 <= t < e + 2.0]
        return cur[-2:]


# ---------------------------------------------------------------- canvas ---
def fixture_layout(fixtures):
    """Screen positions for each fixture: rig-view x, one truss row per type."""
    xs = [f['pos'][0] for f in fixtures if 'HAZER' not in f['model']]
    x0, x1 = min(xs), max(xs)
    rows = {'PIXBAR 6CH': 402, 'TOURCOB PAR': 56, 'ZOOM 12 CHANNEL': 88, 'CX 42 NEW': 120}
    out = []
    for f in fixtures:
        x = 70 + (f['pos'][0] - x0) / max(1, x1 - x0) * (SW - 140)
        y = rows.get(f['model'], 30)
        kind = 'bar' if 'PIXBAR' in f['model'] else 'haze' if 'HAZER' in f['model'] else 'spot'
        out.append((x, y, kind))
    return out


def beam_masks(layout):
    """Per-fixture light masks (beam + floor pool + cyc wash) at stage size."""
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    masks = []
    for i, (fx, fy, kind) in enumerate(layout):
        if kind == 'haze':
            masks.append(np.zeros((SH, SW), np.float32))
            continue
        if kind == 'bar':
            # LED bar at the foot of the cyc: uplight wash on the backdrop.
            d = np.clip((fy - yy) / 260.0, 0, 1)
            spread = np.exp(-((xx - fx) / 95.0) ** 2)
            m = spread * (1 - d) ** 1.6 * (yy < fy + 6) * 0.9
            masks.append(m.astype(np.float32))
            continue
        # Spot/wash: aim spreads across the stage from the rig position.
        aim_x = SW / 2 + (fx - SW / 2) * (0.75 if kind == 'spot' else 1.0)
        aim_x += ((i * 37) % 7 - 3) * 12
        pool_w = {56: 95, 88: 70, 120: 80}.get(int(fy), 80)
        k = np.clip((yy - fy) / (FLOOR_Y - fy), 0, 1)
        cx = fx + (aim_x - fx) * k
        half = 6 + pool_w * k
        cone = np.exp(-((xx - cx) / half) ** 2 * 1.6) * (yy >= fy) * (yy <= FLOOR_Y)
        cone *= 0.10 * (0.4 + 0.6 * k)
        pool = np.exp(-(((xx - aim_x) / (pool_w * 1.15)) ** 2 + ((yy - FLOOR_Y) / 26.0) ** 2))
        m = cone + 0.32 * pool * (yy >= FLOOR_Y - 40)
        masks.append(m.astype(np.float32))
    return np.stack(masks).reshape(len(masks), -1)


PALETTES = [
    (('house', 'preshow', 'curtain', 'interval', 'exit'), ((90, 10, 20), (30, 4, 10))),
    (('beach', 'party', 'lobster', 'sun'), ((250, 170, 80), (40, 150, 200))),
    (('storm', 'ship', 'wreck'), ((60, 70, 90), (10, 14, 24))),
    (('lair', 'octavia', 'cave', 'dark'), ((90, 30, 120), (10, 40, 30))),
    (('palace', 'throne', 'court'), ((220, 180, 90), (20, 90, 110))),
    (('wedding', 'dry', 'land', 'shore'), ((250, 200, 210), (120, 170, 220))),
    (('jelly',), ((200, 80, 200), (20, 20, 70))),
    (('bar',), ((40, 160, 170), (40, 20, 70))),
]


def backdrop_image(name, w, h):
    low = name.lower()
    top, bot = (30, 110, 170), (5, 20, 50)
    for keys, pal in PALETTES:
        if any(k in low for k in keys):
            top, bot = pal
            break
    if not name:
        top, bot = (0, 0, 0), (0, 0, 0)
    g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    img = (np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g)
    img = np.repeat(img, w, axis=1)
    seed = int(hashlib.md5(name.encode()).hexdigest()[:6], 16)
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for _ in range(5):  # soft shapes so each backdrop reads as its own picture
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(30, 110)
        col = rng.uniform(0.6, 1.3)
        img *= 1 + 0.18 * (col - 1) * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / r ** 2))[..., None]
    return np.clip(img / 255.0, 0, 1)


class Renderer:
    def __init__(self, score):
        self.s = score
        self.light = Lighting(score)
        self.media = Media(score)
        self.layout = fixture_layout(score['fixtures'])
        self.masks = beam_masks(self.layout)
        self.haze_ch = next((i for i, (_, _, k) in enumerate(self.layout) if k == 'haze'), None)
        self.bd_box = (150, 150, 730, 402)
        self.bd_cache = {}
        self.steps = score['steps']
        self.strip = self._strip()
        self.stage_base = self._stage_base()

    # static layers -------------------------------------------------------
    def _stage_base(self):
        img = np.zeros((SH, SW, 3), np.float32)
        img[:] = np.array([6, 7, 11], np.float32) / 255
        img[FLOOR_Y - 40:, :] = np.array([16, 14, 14], np.float32) / 255  # deck
        return img

    def _strip(self):
        im = Image.new('RGB', (W, H - STRIP_Y), BG)
        d = ImageDraw.Draw(im)
        dur = self.s['duration']
        x0, x1, y = 20, W - 20, 50
        self.strip_geom = (x0, x1, y)
        d.rectangle([x0, y, x1, y + 22], fill=(28, 30, 40))
        for st in self.steps:
            xa = x0 + st['t'] / dur * (x1 - x0)
            xb = x0 + (st['t'] + st['slot']) / dur * (x1 - x0)
            if st['song']:
                d.rectangle([xa, y + 2, xb, y + 20], fill=(70, 55, 120))
            d.line([xa, y + 16, xa, y + 22], fill=(90, 95, 110))
        for j, a in enumerate(self.s['acts']):
            xa = x0 + a['t'] / dur * (x1 - x0)
            ly = y - 18 if j % 2 else y - 32
            d.line([xa, ly + 2, xa, y + 22], fill=ACCENT)
            d.text((xa + 4, ly), a['label'], fill=ACCENT, font=F_XS)
        d.text((x0 + 300, 8), 'SHOW TIMELINE', fill=DIM, font=F_XS)
        d.rectangle([x0 + 420, 8, x0 + 432, 20], fill=(70, 55, 120))
        d.text((x0 + 438, 8), 'song (S cues)', fill=DIM, font=F_XS)
        return im

    def backdrop(self, name):
        if name not in self.bd_cache:
            x0, y0, x1, y1 = self.bd_box
            self.bd_cache[name] = backdrop_image(name, x1 - x0, y1 - y0)
        return self.bd_cache[name]

    # per frame -------------------------------------------------------------
    def step_at(self, t):
        cur = None
        for i, st in enumerate(self.steps):
            if st['t'] <= t:
                cur = i
            else:
                break
        return cur

    def frame(self, t):
        rgb, live = self.light.at(t)
        haze = float(rgb[self.haze_ch].max()) if self.haze_ch is not None else 0.0

        stage = self.stage_base.copy()
        # backdrop (projection) with a slow drift for video loops
        x0, y0, x1, y1 = self.bd_box
        vids = self.media.video_at(t)
        for vt0, vend, v in vids:
            bd = self.backdrop(v['file'])
            a = min(1.0, (t - vt0) / 2.0) * (1.0 if t < vend else max(0.0, 1 - (t - vend) / 2.0))
            if not v['still']:
                bd = np.roll(bd, int((t * 6) % bd.shape[1]), axis=1)
            stage[y0:y1, x0:x1] = stage[y0:y1, x0:x1] * (1 - a * 0.55) + bd * a * 0.55
        # beams (additive light), haze makes the air visible
        light = (rgb.T @ self.masks).T.reshape(SH, SW, 3)
        stage = stage + light * (1.0 + 0.8 * haze)
        if haze > 0.01:
            stage += haze * 0.05 * np.clip(light.mean(axis=2, keepdims=True), 0, 1)
        stage = 1 - np.exp(-stage * 1.35)  # soft tone map
        img = Image.new('RGB', (W, H), BG)
        img.paste(Image.fromarray((np.clip(stage, 0, 1) * 255).astype(np.uint8)), (0, 0))
        d = ImageDraw.Draw(img)

        # truss + fixture bodies lit in their colour
        for y in (56, 88, 120):
            d.line([40, y - 9, SW - 40, y - 9], fill=(70, 72, 80), width=3)
        for i, (fx, fy, kind) in enumerate(self.layout):
            c = tuple(int(min(255, 40 + v * 255)) for v in rgb[i])
            if kind == 'bar':
                d.rectangle([fx - 18, fy, fx + 18, fy + 6], fill=c, outline=(60, 60, 70))
            elif kind == 'spot':
                d.rounded_rectangle([fx - 7, fy - 7, fx + 7, fy + 7], 3, fill=(30, 30, 36), outline=(80, 80, 90))
                d.ellipse([fx - 4, fy - 1, fx + 4, fy + 7], fill=c)
        x0, y0, x1, y1 = self.bd_box
        d.rectangle([x0 - 1, y0 - 1, x1, y1], outline=(45, 48, 60))
        if vids:
            v = vids[-1][2]
            label = ('STILL  ' if v['still'] else 'VIDEO  ') + os.path.splitext(v['file'])[0]
            d.text((x0 + 8, y0 + 6), label, fill=(210, 215, 225), font=F_XS)
        if haze > 0.01:
            d.text((SW - 110, FLOOR_Y - 32), f'HAZE {haze * 100:.0f}%', fill=(170, 180, 200), font=F_XS)
        d.text((16, SH - 24), 'DOWNSTAGE / AUDIENCE', fill=(80, 84, 96), font=F_XS)

        self._panel(d, t, live)
        img.paste(self.strip, (0, STRIP_Y))
        x0s, x1s, ys = self.strip_geom
        px = x0s + t / self.s['duration'] * (x1s - x0s)
        d.polygon([(px - 6, STRIP_Y + ys - 10), (px + 6, STRIP_Y + ys - 10), (px, STRIP_Y + ys)], fill=INK)
        d.line([px, STRIP_Y + ys, px, STRIP_Y + ys + 22], fill=INK, width=2)
        mm, ss = divmod(int(t), 60)
        d.text((W - 110, STRIP_Y + 82), f'previz {mm:02d}:{ss:02d}', fill=DIM, font=F_SM)
        return img

    def _panel(self, d, t, live):
        x = PANEL_X + 22
        d.rectangle([PANEL_X, 0, W, SH], fill=(16, 18, 26))
        d.text((x, 14), 'THE LITTLE MERMAID', fill=INK, font=F_MED)
        d.text((x, 40), 'R13.1 PREVIZ  -  Plantagenet Hall', fill=DIM, font=F_SM)
        i = self.step_at(t)
        if i is None:
            d.text((x, 90), 'STANDBY', fill=DIM, font=F_BIG)
            return
        st = self.steps[i]
        age = t - st['t']
        go_col = ACCENT if age < 0.6 else INK
        d.text((x, 70), 'GO', fill=(90, 220, 140) if age < 0.6 else DIM, font=F_SM)
        num = st['num'] if st['num'].startswith('S') else 'Q' + st['num']
        d.text((x, 84), num, fill=go_col, font=F_BIG)
        name = st['name']
        d.text((x, 146), name[:40], fill=INK, font=F_TXT)
        if any(a['type'] == 'mantra' and a['at'] > 0 for a in st['actions']):
            d.text((x, 168), 'FLASH  -  timed return by QLab', fill=(255, 120, 120), font=F_SM)

        y = 196
        d.text((x, y), 'LIGHTING (Mantra memories up)', fill=DIM, font=F_XS)
        y += 16
        for mid, lvl, cname in sorted(live, key=lambda l: -l[1])[:4]:
            page, mem = mid // 10 + 1, mid % 10 + 1
            d.rectangle([x, y + 3, x + 50, y + 11], outline=(70, 74, 90))
            d.rectangle([x, y + 3, x + 50 * lvl, y + 11], fill=(110, 170, 255))
            d.text((x + 58, y), f'P{page} M{mem}  {cname}'[:34], fill=INK, font=F_SM)
            y += 18

        y = max(y + 8, 300)
        d.text((x, y), 'AUDIO RUNNING', fill=DIM, font=F_XS)
        y += 16
        aud = self.media.audio_at(t)
        if not aud:
            d.text((x, y), '-', fill=DIM, font=F_SM)
            y += 18
        for a0, aend, a in aud[-4:]:
            nm = a['name'].replace('SFX ', '')
            d.text((x, y), nm[:38], fill=INK, font=F_SM)
            if a['len'] > 0:
                p = ((t - a0) % a['len']) / a['len'] if a['loop'] else min(1, (t - a0) / a['len'])
                d.rectangle([x, y + 16, x + 330, y + 18], fill=(40, 42, 55))
                d.rectangle([x, y + 16, x + 330 * p, y + 18], fill=(90, 220, 140))
            y += 24

        y = max(y + 8, 440)
        d.text((x, y), 'NEXT', fill=DIM, font=F_XS)
        y += 16
        for nx in self.steps[i + 1:i + 5]:
            n = nx['num'] if nx['num'].startswith('S') else 'Q' + nx['num']
            d.text((x, y), f'{n:<6} {nx["name"]}'[:40], fill=(170, 175, 190), font=F_SM)
            y += 17


# ---------------------------------------------------------------- output ---
def encode(renderer, t0, t1, fps, out):
    n = int(round((t1 - t0) * fps))
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
           '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(renderer.frame(t0 + k / fps).tobytes())
        if k % (fps * 30) == 0:
            print(f'  {os.path.basename(out)}: {k}/{n} frames', flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(f'ffmpeg failed for {out}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--score', default=os.path.join(HERE, 'score.json'))
    ap.add_argument('--out', default=os.path.join(HERE, 'TLM_R13_1_previz.mp4'))
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--end', type=float, default=None)
    ap.add_argument('--fps', type=int, default=25)
    ap.add_argument('--parts', type=int, default=1, help='render in N parallel parts, then join')
    ap.add_argument('--still', type=float, default=None, help='write one PNG at this time')
    args = ap.parse_args()

    score = json.load(open(args.score))
    end = args.end if args.end is not None else score['duration']

    if args.still is not None:
        Renderer(score).frame(args.still).save(args.out)
        print('wrote', args.out)
        return

    if args.parts <= 1:
        encode(Renderer(score), args.start, end, args.fps, args.out)
        print('wrote', args.out)
        return

    # Split on whole frames so the parts join without a gap.
    frames = int(round((end - args.start) * args.fps))
    cuts = [args.start + round(frames * i / args.parts) / args.fps for i in range(args.parts + 1)]
    tmp = tempfile.mkdtemp(prefix='previz_')
    procs, parts = [], []
    for i in range(args.parts):
        part = os.path.join(tmp, f'part{i}.mp4')
        parts.append(part)
        procs.append(subprocess.Popen([sys.executable, __file__, '--score', args.score, '--out', part,
                                       '--start', str(cuts[i]), '--end', str(cuts[i + 1]),
                                       '--fps', str(args.fps)]))
    if any(p.wait() for p in procs):
        sys.exit('a render part failed')
    lst = os.path.join(tmp, 'parts.txt')
    with open(lst, 'w') as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    subprocess.check_call([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                           '-i', lst, '-c', 'copy', '-movflags', '+faststart', args.out])
    print('wrote', args.out)


if __name__ == '__main__':
    main()
