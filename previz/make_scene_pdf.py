"""Scene-by-scene PDF of the TLM R13.1 show, built from score.json.

Every GO is grouped into its scene (by the Mantra scene memory it runs under)
and listed with a rendered thumbnail of the stage look, the desk cues it
fires, the sound and backdrop cues, and flags for anything still to supply.

    python3 score_data.py && python3 make_scene_pdf.py   # -> TLM_R13_1_Scene_by_Scene.pdf
"""
import io
import json
import os
from datetime import date

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image as RLImage, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

import render_previz as rp

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'TLM_R13_1_Scene_by_Scene.pdf')

FONT_DIR = '/usr/share/fonts/truetype/dejavu'
pdfmetrics.registerFont(TTFont('Sans', os.path.join(FONT_DIR, 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('Sans-Bold', os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-Bold')

# Scene memory (Mantra internal ID) -> act and scene title.
SCENES = {
    10: ('ACT ONE', 'Preshow & Scene One', 'Beneath the waves - opening, Queen Marina, Ariel upset'),
    11: ('ACT ONE', 'Scene Two', 'Singing lesson, Ariel solo, the ship above, Octavia conjures the storm'),
    12: ('ACT ONE', 'Scene Three', 'The ship, the weather gag and the storm - Evan overboard'),
    13: ('ACT ONE', 'Scene Four', 'The shore - Spirit, Evan wakes, Ariel/Evan duet'),
    14: ('ACT ONE', 'Scene Five', 'Underwater bar - the bargain, transformation, voice into shell'),
    15: ('INTERVAL', 'Interval', ''),
    20: ('ACT TWO', 'Scene Six', 'The palace - opening song, Evan memory, cue-card routine'),
    21: ('ACT TWO', 'Scene Seven', 'Jellyfish search and chorus'),
    22: ('ACT TWO', 'Scene Eight', "Octavia's lair - voice transfers, haywire, Ariel restored"),
    23: ('ACT TWO', 'Scene Nine', 'Dry land - Spirit appears to Evan'),
    24: ('ACT TWO', 'Scene Ten', 'The wedding - stop the wedding, reveal, full-cast song'),
    25: ('ACT TWO', 'Bows & End', 'Bows, He\'s a Pirate, exit'),
}

# Open items from R13_1_QLAB_AND_DESK_FIX_LIST.csv, by cue.
TODO = {
    '1': 'House music still a silent placeholder',
    '2': 'Preshow music still a silent placeholder',
    '37': 'End of Act One music still a silent placeholder',
    '38': 'Interval music still a silent placeholder',
    '65': 'Exit music still a silent placeholder',
    '42.5': "Ariel's recorded line still a silent placeholder",
    'S2': 'Vocal version - swap for backing track',
    'S3': 'Vocal version - swap for backing track',
    'S4': 'Swap for backing if the file has vocals',
    'S5': 'Vocal version - swap for backing track',
    'S7': 'Jellyfish chorus song still to be chosen',
}

INK = colors.HexColor('#1b1e2b')
DIM = colors.HexColor('#6b7085')
RULE = colors.HexColor('#d9dbe3')
ACT = colors.HexColor('#b8741a')
FLASH = colors.HexColor('#c0392b')
TODO_C = colors.HexColor('#a05a00')

ST = {
    'title': ParagraphStyle('title', fontName='Sans-Bold', fontSize=30, leading=36, textColor=INK),
    'sub': ParagraphStyle('sub', fontName='Sans', fontSize=13, leading=18, textColor=DIM),
    'act': ParagraphStyle('act', fontName='Sans-Bold', fontSize=10, leading=12, textColor=ACT),
    'h1': ParagraphStyle('h1', fontName='Sans-Bold', fontSize=22, leading=26, textColor=INK),
    'h1sub': ParagraphStyle('h1sub', fontName='Sans', fontSize=11, leading=15, textColor=DIM),
    'cell': ParagraphStyle('cell', fontName='Sans', fontSize=7.6, leading=9.6, textColor=INK, alignment=TA_LEFT),
    'cellb': ParagraphStyle('cellb', fontName='Sans-Bold', fontSize=11, leading=13, textColor=INK),
    'head': ParagraphStyle('head', fontName='Sans-Bold', fontSize=7.5, leading=9, textColor=DIM),
    'sum': ParagraphStyle('sum', fontName='Sans', fontSize=8.8, leading=12.5, textColor=INK),
    'toc': ParagraphStyle('toc', fontName='Sans', fontSize=10, leading=13, textColor=INK),
}


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def cue_label(num):
    return num if num.startswith('S') else 'Q' + num


def pil_to_rl(img, width_mm):
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=86)
    buf.seek(0)
    w = width_mm * mm
    return RLImage(buf, width=w, height=w * img.height / img.width)


class Book:
    def __init__(self, score):
        self.s = score
        self.r = rp.Renderer(score)
        self.names = {}
        for st in score['steps']:
            for a in st['actions']:
                if a['type'] in ('audio', 'video'):
                    self.names[a['id']] = (a['type'], a.get('name') or a['file'])
        self.mem_names = {int(k): [c['name'] for c in v['cues']] for k, v in score['memories'].items()}

    # ------------------------------------------------------------ grouping
    def scenes(self):
        groups, cur = [], None
        for st in self.s['steps']:
            ups = [a['mem'] for a in st['actions']
                   if a['type'] == 'mantra' and a['level'] > 0 and a['mem'] in SCENES]
            if ups and (cur is None or ups[0] != cur['mem']):
                cur = {'mem': ups[0], 'steps': []}
                groups.append(cur)
            cur['steps'].append(st)
        return groups

    # ------------------------------------------------------------ images
    def stage(self, t, size):
        return self.r.frame(t).crop((0, 0, rp.SW, rp.SH)).resize(size, Image.LANCZOS)

    def settled(self, st):
        return st['t'] + st['slot'] - 0.15

    # ------------------------------------------------------------ cells
    def lighting(self, st):
        out = []
        for a in st['actions']:
            if a['type'] != 'mantra':
                continue
            where = f"P{a['page']} M{a['pm']}"
            if a['level'] <= 0:
                label = 'chase OFF' if a['mem'] == 44 else 'release'
                out.append(f'<font color="#6b7085">{where} {label}</font>')
                continue
            name = self.mem_names.get(a['mem'], [''])[min(a['cue'], len(self.mem_names[a['mem']]) - 1)]
            if a['mem'] == 44:
                name = 'HAYWIRE chase ON (5 steps @120 BPM)'
            bits = f'<b>{esc(name)}</b> <font color="#6b7085">{where} c{a["cue"] + 1}'
            bits += f', {a["fade"]:g}s' if a['fade'] else ', snap'
            if a['at'] > 0:
                bits += f', +{a["at"]:g}s'
            out.append(bits + '</font>')
        return '<br/>'.join(out) or '<font color="#6b7085">-</font>'

    def sound(self, st):
        out = []
        for a in st['actions']:
            if a['type'] == 'audio':
                extra = ' (loop)' if a['loop'] else (f' ({a["len"]:.0f}s)' if a['len'] else '')
                out.append(f'<b>{esc(a["name"].replace("SFX ", ""))}</b>'
                           f'<font color="#6b7085">{extra}</font>')
            elif a['type'] == 'stop' and self.names.get(a['id'], ('',))[0] == 'audio':
                out.append(f'<font color="#6b7085">fade out {esc(self.names[a["id"]][1].replace("SFX ", ""))}'
                           f' {a["fade"]:g}s</font>')
        return '<br/>'.join(out) or '<font color="#6b7085">-</font>'

    def backdrop(self, st):
        out = []
        for a in st['actions']:
            if a['type'] == 'video':
                out.append(('Still: ' if a['still'] else 'Video: ') + esc(os.path.splitext(a['file'])[0]))
        return '<br/>'.join(out)

    def notes(self, st):
        out = []
        if any(a['type'] == 'mantra' and a['at'] > 0 for a in st['actions']):
            out.append('<font color="#c0392b"><b>FLASH</b> - QLab fires the return</font>')
        if any(a['type'] == 'mantra' and a['mem'] == 43 for a in st['actions']):
            out.append('Haze')
        bd = self.backdrop(st)
        if bd:
            out.append(bd)
        top = st['num'].split('.')[0] if st['num'].startswith('S') else st['num']
        if top in TODO and (st['num'] == top):
            out.append(f'<font color="#a05a00"><b>TO DO</b> {esc(TODO[top])}</font>')
        return '<br/>'.join(out)

    # ------------------------------------------------------------ pages
    def cover(self, groups):
        story = [Spacer(1, 6 * mm),
                 Paragraph('The Little Mermaid', ST['title']),
                 Paragraph('R13.1 show - scene by scene  |  Plantagenet Hall  |  '
                           f'{date(2026, 9, 28).strftime("%d %b %Y")}', ST['sub']),
                 Spacer(1, 6 * mm)]
        hero_step = next(st for st in self.s['steps'] if st['num'] == 'S1.3')
        hero = self.r.frame(self.settled(hero_step)).resize((720, 405), Image.LANCZOS)
        rows = [[Paragraph('<b>Scene</b>', ST['head']), Paragraph('<b>Cues</b>', ST['head']),
                 Paragraph('<b>Songs</b>', ST['head'])]]
        for g in groups:
            act, title, _ = SCENES[g['mem']]
            nums = [st['num'] for st in g['steps'] if not st['num'].startswith('S')]
            songs = sorted({st['num'].split('.')[0] for st in g['steps'] if st['num'].startswith('S')},
                           key=lambda s: int(s[1:]))
            rows.append([Paragraph(f'<font color="#b8741a" size="7">{act}</font><br/>{esc(title)}', ST['toc']),
                         Paragraph(f'Q{nums[0]} - Q{nums[-1]}' if nums else '', ST['toc']),
                         Paragraph(', '.join(songs), ST['toc'])])
        toc = Table(rows, colWidths=[62 * mm, 30 * mm, 30 * mm])
        toc.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)]))
        total_go = len(self.s['steps'])
        n_light = sum(1 for st in self.s['steps'] for a in st['actions'] if a['type'] == 'mantra')
        intro = Paragraph(
            f'{total_go} GOs across {len(groups)} scenes, firing {n_light} Mantra cues. Each row below '
            'shows the stage look once that GO has settled, drawn from the Mantra file (fixture colour and '
            'level for every memory cue) and the QLab cue list (fades, timed flash returns, releases, '
            'audio and backdrop cues). Backdrop media is shown by name only. '
            '<font color="#c0392b"><b>FLASH</b></font> rows carry a QLab timed return; '
            '<font color="#a05a00"><b>TO DO</b></font> marks audio still to supply; '
            '<font color="#6a4fb3"><b>SONG</b></font> marks GOs inside a song.', ST['sum'])
        left = [pil_to_rl(hero, 150), Spacer(1, 4 * mm), intro]
        story.append(Table([[left, toc]], colWidths=[156 * mm, 124 * mm],
                           style=[('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                  ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
        return story

    def scene(self, g):
        act, title, blurb = SCENES[g['mem']]
        steps = g['steps']
        mid = steps[len(steps) // 2]
        hero = self.stage(self.settled(mid), (440, 280))

        backdrops, audio, songs = [], [], []
        for st in steps:
            for a in st['actions']:
                if a['type'] == 'video':
                    n = os.path.splitext(a['file'])[0]
                    if n not in backdrops:
                        backdrops.append(n)
                if a['type'] == 'audio' and a['name'] not in audio:
                    audio.append(a['name'].replace('SFX ', ''))
            if st['num'].startswith('S') and '.' not in st['num']:
                songs.append(f"{st['num']} {st['name'].split(' (')[0]}")
        flashes = sum(1 for st in steps if any(a['type'] == 'mantra' and a['at'] > 0 for a in st['actions']))
        nums = [cue_label(st['num']) for st in steps]
        summary = [
            f'<b>Cues</b>  {nums[0]} - {nums[-1]}  ({len(steps)} GOs)',
            f'<b>Desk</b>  Page {g["mem"] // 10 + 1} Memory {g["mem"] % 10 + 1} '
            f'({len(self.mem_names[g["mem"]])} cues)',
        ]
        if songs:
            summary.append('<b>Songs</b>  ' + esc(', '.join(songs)))
        if backdrops:
            summary.append('<b>Backdrops</b>  ' + esc(', '.join(backdrops)))
        if flashes:
            summary.append(f'<b>Flashes</b>  <font color="#c0392b">{flashes} timed flash return(s)</font>')
        todos = [f'{cue_label(n)}: {t}' for n, t in TODO.items() if cue_label(n) in nums]
        if todos:
            summary.append('<b>To do</b>  <font color="#a05a00">' + esc('; '.join(todos)) + '</font>')
        summary.append('<b>Sound</b>  ' + esc(', '.join(audio[:14]) + (' ...' if len(audio) > 14 else '')))

        head = [Paragraph(act, ST['act']), Paragraph(esc(title), ST['h1'])]
        if blurb:
            head.append(Paragraph(esc(blurb), ST['h1sub']))
        head += [Spacer(1, 3 * mm), Paragraph('<br/>'.join(summary), ST['sum'])]
        top = Table([[head, pil_to_rl(hero, 110)]], colWidths=[168 * mm, 112 * mm],
                    style=[('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0)])

        rows = [[Paragraph(h, ST['head']) for h in
                 ('STAGE LOOK', 'GO', 'WHAT HAPPENS', 'LIGHTING (Mantra)', 'SOUND (QLab)', 'NOTES / BACKDROP')]]
        style = [('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                 ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3)]
        for st in steps:
            thumb = pil_to_rl(self.stage(self.settled(st), (264, 168)), 30)
            what = esc(st['name'])
            if st['num'].startswith('S') and '.' in st['num']:
                what = esc(st['name'].split(' (')[0]) + ' - next section'
            go = cue_label(st['num'])
            if st['song']:
                go = f'<font color="#6a4fb3">{go}</font><br/><font size="6.5" color="#6a4fb3">SONG</font>'
            rows.append([thumb, Paragraph(go, ST['cellb']), Paragraph(what, ST['cell']),
                         Paragraph(self.lighting(st), ST['cell']), Paragraph(self.sound(st), ST['cell']),
                         Paragraph(self.notes(st), ST['cell'])])
        table = Table(rows, colWidths=[32 * mm, 17 * mm, 47 * mm, 72 * mm, 58 * mm, 54 * mm],
                      repeatRows=1, style=style)
        return [KeepTogether(top), Spacer(1, 4 * mm), table]

    def mem_names_for(self, st):
        for a in st['actions']:
            if a['type'] == 'mantra' and a['level'] > 0:
                names = self.mem_names[a['mem']]
                return names[min(a['cue'], len(names) - 1)]
        return ''

    def build(self, out=OUT):
        groups = self.scenes()
        story = self.cover(groups)
        for g in groups:
            story.append(PageBreak())
            story += self.scene(g)

        def footer(c, doc):
            c.saveState()
            c.setFont('Sans', 7.5)
            c.setFillColor(DIM)
            c.drawString(12 * mm, 7 * mm, 'The Little Mermaid - R13.1 scene by scene')
            c.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f'Page {doc.page}')
            c.restoreState()

        doc = SimpleDocTemplate(out, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                                topMargin=11 * mm, bottomMargin=13 * mm,
                                title='The Little Mermaid - R13.1 Scene by Scene', author='TLM previz')
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        print(f'wrote {out}: {len(groups)} scenes, {len(self.s["steps"])} GOs')


if __name__ == '__main__':
    Book(json.load(open(os.path.join(HERE, 'score.json')))).build()
