"""Build the previz score for The Little Mermaid R13.1.

Reads the QLab 5 workspace and the Mantra show file from the show package and
writes score.json: a compressed timeline of every GO in running order, with
the lighting looks (per-fixture colour + level) each Mantra memory cue sets,
the audio and backdrop cues each GO starts, and when things fade or stop.

Show time is compressed: every manual GO gets a fixed slot (longer if its
fades or timed flash returns need it) so the whole show reads in minutes.
"""
import json
import os
import re
import sys
from collections import defaultdict

import qlab_read

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, '..', 'package', 'TLM_R13_REBUILT_Show_Files')
QLAB = os.path.join(PKG, 'TLM_Show_R13_1.qlab5')
MANTRA = os.path.join(PKG, 'TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr')
OUT = os.path.join(HERE, 'score.json')

SLOT_SCENE = 4.5      # seconds on screen for each scene GO
SLOT_SONG_STEP = 3.0  # seconds for each GO inside a song
SLOT_MIN_TAIL = 1.5   # seconds of hold after the longest fade in a GO
SKIP = {'E1', 'E2', 'E3'}  # emergency cues are not part of the running order

OSC_RE = re.compile(r'/PlayMemory/Page=(\d+)/Memory=(\d+)/Cue=(\d+)/Level=(\d+)(?:/Fade=(\d+))?')


# --------------------------------------------------------------- Mantra ---
def read_mantra(path):
    text = open(path, encoding='latin1').read()
    sections = {}
    for m in re.finditer(r'^\[([^\]]+)\]\n(.*?)(?=^\[|\Z)', text, re.S | re.M):
        body = {}
        for line in m.group(2).splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                body[k] = v
        sections[m.group(1)] = body

    fixtures = []
    patch = sections['Patch']
    rig = {int(k[4:-4]): tuple(int(n) for n in re.findall(r'-?\d+', v))
           for k, v in sections['RigView'].items() if k.startswith('Live') and k.endswith('_Pos')}
    n = 0
    while f'Item{n}_Channel' in patch:
        ch = int(patch[f'Item{n}_Channel'])
        fixtures.append({
            'ch': ch,  # memories use ch + 1
            'make': patch[f'Item{n}_Make'],
            'model': patch[f'Item{n}_Model'],
            'pos': rig.get(ch, (0, 0)),
        })
        n += 1

    memories = {}
    for name, body in sections.items():
        m = re.fullmatch(r'Memory(\d+)', name)
        if not m:
            continue
        mid = int(m.group(1))
        cues = []
        for c in range(int(body.get('NumScenes', 0))):
            cb = sections.get(f'Memory{mid}-Cue{c}', {})
            look = {}
            for k, v in cb.items():
                km = re.fullmatch(r'Channel(\d+)_Level', k)
                if km:
                    ch = int(km.group(1)) - 1
                    argb = int(cb.get(f'Channel{ch + 1}_Colour', '4294967295'))
                    rgb = [(argb >> 16) & 255, (argb >> 8) & 255, argb & 255]
                    look[ch] = [rgb, int(v) / 65535.0]
            cues.append({
                'name': cb.get('Name', ''),
                'fade_in': int(cb.get('FadeIn', 0)) / 1000.0,
                'look': look,
            })
        memories[mid] = {
            'chase': body.get('IsChase') == 'true',
            'bpm': int(body.get('ChaseBpm', 60)),
            'cues': cues,
        }
    return fixtures, memories


def memory_id(page, mem):
    return (page - 1) * 10 + (mem - 1)


# ----------------------------------------------------------------- QLab ---
def target_path(cue):
    ft = cue.get('fileTarget')
    return ft.get('relativePath') if isinstance(ft, dict) else None


def audio_len(cue):
    for k in ('lastSeenFileDuration', 'endTime'):
        v = cue.get(k)
        if v:
            return float(v)
    return 0.0


def actions_for(cue, index):
    """Turn one QLab child cue into zero or more score actions."""
    cls = cue['__class__']
    out = []
    if cls == 'OSCCue':
        s = cue.get('oscString') or cue.get('name', '')
        m = OSC_RE.search(s)
        if m:
            p, mem, c, lvl, fade = (int(x) if x else 0 for x in m.groups())
            out.append({'type': 'mantra', 'mem': memory_id(p, mem), 'page': p, 'pm': mem,
                        'cue': c - 1, 'level': lvl / 100.0, 'fade': fade / 1000.0})
    elif cls == 'AudioCue':
        path = target_path(cue)
        out.append({'type': 'audio', 'id': cue['uniqueID'], 'name': cue['name'],
                    'file': os.path.basename(path) if path else '',
                    'len': audio_len(cue), 'loop': bool(cue.get('infiniteLoop'))})
    elif cls == 'VideoCue':
        path = target_path(cue) or ''
        out.append({'type': 'video', 'id': cue['uniqueID'], 'file': os.path.basename(path),
                    'still': '/stills/' in path or path.startswith('media/stills')})
    elif cls == 'FadeCue':
        tgt = cue.get('cueTargetUniqueID')
        if tgt and cue.get('stopTargetWhenDone'):
            out.append({'type': 'stop', 'id': tgt, 'fade': float(cue.get('duration') or 0)})
    elif cls == 'ScriptCue':
        out.append({'type': 'panic'})
    return out


def build(qlab_path=QLAB, mantra_path=MANTRA):
    fixtures, memories = read_mantra(mantra_path)
    root = qlab_read.load(qlab_path)
    main = root['cueLists']['cues'][0]

    steps = []  # one per manual GO
    for top in main['cues']:
        num = str(top.get('number') or '')
        if num in SKIP or top['__class__'] != 'GroupCue':
            continue
        kids = top.get('cues') or []
        if top.get('groupMode') == 1:
            # Song group: first child starts, then continues (auto-continue),
            # each numbered child after that is a manual GO inside the song.
            cur = {'num': num, 'name': top['name'], 'song': True, 'actions': []}
            follow = True  # the group GO itself starts the first child
            for kid in kids:
                if not follow:
                    steps.append(cur)
                    cur = {'num': kid['number'], 'name': top['name'], 'song': True,
                           'actions': []}
                for a in actions_for(kid, 0):
                    a['at'] = float(kid.get('preWait') or 0)
                    cur['actions'].append(a)
                follow = bool(kid.get('continueMode'))
            steps.append(cur)
        else:
            # Timeline group: every child fires at its own pre-wait.
            acts = []
            for kid in kids:
                for a in actions_for(kid, 0):
                    a['at'] = float(kid.get('preWait') or 0)
                    acts.append(a)
            steps.append({'num': num, 'name': top['name'], 'song': False, 'actions': acts})

    # Lay the GOs out on the compressed clock.
    t = 2.0  # short black lead-in
    for s in steps:
        s['t'] = round(t, 3)
        need = max([a['at'] + a.get('fade', 0) for a in s['actions']] + [0]) + SLOT_MIN_TAIL
        slot = max(SLOT_SONG_STEP if s['song'] and s['num'] != s['num'].split('.')[0] else SLOT_SCENE, need)
        s['slot'] = round(slot, 3)
        t += slot
    total = t + 3.0

    # Acts for the timeline strip.
    acts = []
    for s in steps:
        if s['num'] == '1':
            acts.append({'t': s['t'], 'label': 'PRESHOW'})
        elif s['num'] == '4':
            acts.append({'t': s['t'], 'label': 'ACT ONE'})
        elif s['num'] == '38':
            acts.append({'t': s['t'], 'label': 'INTERVAL'})
        elif s['num'] == '39':
            acts.append({'t': s['t'], 'label': 'ACT TWO'})
        elif s['num'] == '64':
            acts.append({'t': s['t'], 'label': 'BOWS'})

    used = sorted({a['mem'] for s in steps for a in s['actions'] if a['type'] == 'mantra'})
    missing = [m for m in used if m not in memories]
    if missing:
        sys.exit(f'Memories used by QLab but not in the Mantra file: {missing}')

    score = {
        'show': 'The Little Mermaid - R13.1 previz',
        'duration': round(total, 3),
        'fixtures': fixtures,
        'memories': {str(k): memories[k] for k in used},
        'steps': steps,
        'acts': acts,
    }
    with open(OUT, 'w') as f:
        json.dump(score, f)
    n_light = sum(1 for s in steps for a in s['actions'] if a['type'] == 'mantra')
    print(f'{len(steps)} GOs, {n_light} Mantra actions, {len(used)} memories, '
          f'{len(fixtures)} fixtures, running time {total / 60:.1f} min -> {OUT}')
    return score


if __name__ == '__main__':
    build()
