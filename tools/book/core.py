"""Shared layout for the R13.1 production book.

Every part is an A4 document with the same header, footer and building blocks
(section headings, tables, coloured note boxes), so the parts read as one book.
Fonts are the PDF base-14 set (Helvetica, Symbol, ZapfDingbats): nothing is
embedded, which keeps the files small enough to upload to Drive.
"""
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

REV = "R13.1"
DATE = "28 September 2026"
SHORTDATE = "28 Sep 2026"
BOOK = "THE LITTLE MERMAID · PRODUCTION BOOK " + REV

INK = colors.black  # all text prints from black ink only
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#b9c2cc")
NAVY = colors.HexColor("#123a5a")
TEAL = colors.HexColor("#0f6e68")
CORAL = colors.HexColor("#b4441c")
# print-friendly: row tints are pale enough to cost little ink; headers, boxes and tiles are rules, not fills
TINT = colors.HexColor("#fdf1ea")
SONG = colors.HexColor("#f0f6fc")
AUTO = colors.HexColor("#f4f9f0")
PALE = colors.HexColor("#f7f9fb")
BOXFILL = {"rec": colors.HexColor("#e7f4f2"), "verify": colors.HexColor("#fbece5"),
           "rule": colors.HexColor("#e9eef4"), "new": colors.HexColor("#fffbea")}
BOXLINE = {"rec": TEAL, "verify": CORAL, "rule": NAVY, "new": colors.HexColor("#b08900")}

# --------------------------------------------------------------------------
# Text: escape, then swap characters Helvetica can't draw for Symbol/Dingbats
# --------------------------------------------------------------------------
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TT
_pm.registerFont(_TT("Glyph", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
_SYM = {c: ("Glyph", c) for c in "→←↑↓≤≥☐●★✓▶■"}
_PLAIN = {"−": "-", "‑": "-", " ": " ", " ": " ", "≈": "~", "Δ": "delta"}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def glyphs(s):
    for k, v in _PLAIN.items():
        s = s.replace(k, v)
    for k, (font, ch) in _SYM.items():
        s = s.replace(k, '<font name="%s">%s</font>' % (font, ch))
    return s


def md(s):
    """Tiny inline markup: **bold**, `mono`, and escaping. Returns Paragraph XML."""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r'<font name="Courier">\1</font>', s)
    s = s.replace("&lt;br/&gt;", "<br/>").replace("\n", "<br/>")
    return glyphs(s)


# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
def _ps(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9, leading=12, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {
    "body": _ps("body", spaceAfter=4),
    "small": _ps("small", fontSize=7.6, leading=9.6),
    "cell": _ps("cell", fontSize=7.8, leading=9.8),
    "cellb": _ps("cellb", fontSize=7.8, leading=9.8, fontName="Helvetica-Bold"),
    "head": _ps("head", fontSize=7.8, leading=9.8, fontName="Helvetica-Bold", textColor=INK),
    "muted": _ps("muted", fontSize=8, leading=10.5, textColor=MUTED),
    "h1": _ps("h1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=INK,
              spaceBefore=4, spaceAfter=6),
    "h2": _ps("h2", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK,
              spaceBefore=8, spaceAfter=4),
    "h3": _ps("h3", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=INK,
              spaceBefore=6, spaceAfter=2),
    "title": _ps("title", fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=INK),
    "sub": _ps("sub", fontSize=11, leading=15, textColor=MUTED),
    "boxt": _ps("boxt", fontName="Helvetica-Bold", fontSize=8.4, leading=11),
    "boxb": _ps("boxb", fontSize=8.4, leading=11),
    "divletter": _ps("divletter", fontName="Helvetica-Bold", fontSize=120, leading=130,
                     textColor=colors.HexColor("#c9d3de"), alignment=TA_CENTER),
    "divtitle": _ps("divtitle", fontName="Helvetica-Bold", fontSize=22, leading=28,
                    textColor=INK, alignment=TA_CENTER),
    "divsub": _ps("divsub", fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER),
}


def P(text, style="body"):
    return Paragraph(md(text), S[style] if isinstance(style, str) else style)


def H1(text):
    return [CondPageBreak(60 * mm), P(text, "h1")]


def H2(text):
    return [CondPageBreak(35 * mm), P(text, "h2")]


def H3(text):
    return P(text, "h3")


def bullets(items, style="body"):
    return [Paragraph("•&nbsp;&nbsp;" + md(i), ParagraphStyle(
        "bl", parent=S[style], leftIndent=10, firstLineIndent=-8, spaceAfter=1.5)) for i in items]


def steps(items, style="body"):
    return [Paragraph("<b>%d.</b>&nbsp;&nbsp;%s" % (n, md(i)), ParagraphStyle(
        "st", parent=S[style], leftIndent=13, firstLineIndent=-12, spaceAfter=2))
        for n, i in enumerate(items, 1)]


def checklist(items, cols=1):
    rows = [["☐ " + i for i in items[k:k + cols]] for k in range(0, len(items), cols)]
    for r in rows:
        r += [""] * (cols - len(r))
    t = Table([[Paragraph(md(c), S["cell"]) for c in r] for r in rows],
              colWidths=[(170 * mm) / cols] * cols)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
    return t


def table(header, rows, widths, tints=(), bold_first=False, total=170 * mm, repeat=True):
    """rows: list of lists of str (markup) or flowables. tints: [(row_index, kind)]."""
    if widths and sum(widths) < 5:  # fractions
        widths = [w * total for w in widths]
    data = []
    if header:
        data.append([Paragraph(md(h), S["head"]) for h in header])
    for r in rows:
        data.append([c if not isinstance(c, str) else
                     Paragraph(md(c), S["cellb"] if (bold_first and k == 0) else S["cell"])
                     for k, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1 if (header and repeat) else 0)
    off = 1 if header else 0
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 1.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
            ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header:
        cmds += [("LINEABOVE", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 0), (-1, 0), 1.0, INK)]
    for i, kind in tints:
        c = {"crit": TINT, "song": SONG, "auto": AUTO, "pale": PALE, "new": BOXFILL["new"]}[kind]
        cmds.append(("BACKGROUND", (0, i + off), (-1, i + off), c))
    t.setStyle(TableStyle(cmds))
    return t


def box(kind, title, text, width=170 * mm):
    """kind: rec (teal recommendation), verify (coral safety/verify), rule (navy
    operating rule), new (yellow: action needed)."""
    body = [Paragraph(md(title), ParagraphStyle("bt", parent=S["boxt"], textColor=INK))]
    for para in (text if isinstance(text, list) else [text]):
        body.append(Paragraph(md(para), S["boxb"]))
    t = Table([[body]], colWidths=[width])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.4, BOXLINE[kind]),
                           ("LINEBEFORE", (0, 0), (0, -1), 2.5, BOXLINE[kind]),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return KeepTogether([Spacer(0, 2), t, Spacer(0, 4)])


def notes_area(title, lines=6, width=170 * mm):
    rows = [[Paragraph(md(title), S["muted"])]] + [[""] for _ in range(lines)]
    t = Table(rows, colWidths=[width], rowHeights=[12] + [16] * lines)
    t.setStyle(TableStyle([("LINEBELOW", (0, 1), (-1, -1), 0.4, RULE),
                           ("BOX", (0, 0), (-1, -1), 0.5, RULE)]))
    return KeepTogether([Spacer(0, 6), t])


def stats(items, width=170 * mm):
    """Row of big-number tiles: [(value, label), ...]."""
    n = len(items)
    cells = [[Paragraph('<font size="17"><b>%s</b></font>' % esc(v), ParagraphStyle(
        "sv", parent=S["body"], textColor=INK, leading=20)),
        Paragraph(md(l), S["small"])] for v, l in items]
    t = Table([cells], colWidths=[width / n] * n)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1.2, NAVY),
                           ("LINEAFTER", (0, 0), (-2, -1), 0.4, RULE),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return KeepTogether([t, Spacer(0, 6)])


# --------------------------------------------------------------------------
# Document
# --------------------------------------------------------------------------
class PartDoc:
    """One book part. letter: 'A'..'L' or '' for stand-alone documents."""

    def __init__(self, path, letter, title, desc="", pagesize=A4, divider=True,
                 header_left=BOOK):
        self.path, self.letter, self.title, self.desc = path, letter, title, desc
        self.header_left = header_left
        self.divider = divider
        self.pagesize = pagesize
        w, h = pagesize
        self.doc = BaseDocTemplate(path, pagesize=pagesize, title=self.full_title(),
                                   author="TLM production team", subject="The Little Mermaid · " + REV,
                                   leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                                   bottomMargin=16 * mm)
        frame = Frame(20 * mm, 16 * mm, w - 40 * mm, h - 34 * mm, id="f",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=self._decorate)])
        self.story = []
        if divider and letter:
            self._divider()

    def full_title(self):
        return ("TLM %s Part %s — %s" % (REV, self.letter, self.title)) if self.letter else \
            "TLM %s — %s" % (REV, self.title)

    def _divider(self):
        self.story += [Spacer(0, 45 * mm), Paragraph(self.letter, S["divletter"]), Spacer(0, 8 * mm),
                       Paragraph(md("PART %s  %s" % (self.letter, self.title)), S["divtitle"]),
                       Spacer(0, 5 * mm), Paragraph(md(self.desc), S["divsub"]), Spacer(0, 5 * mm),
                       Paragraph(md("Revision %s · %s" % (REV, DATE)), S["divsub"]), PageBreak()]

    def _decorate(self, canv, doc):
        w, h = doc.pagesize
        canv.saveState()
        canv.setStrokeColor(NAVY)
        canv.setLineWidth(0.6)
        canv.line(20 * mm, h - 13 * mm, w - 20 * mm, h - 13 * mm)
        canv.setFont("Helvetica-Bold", 7)
        canv.setFillColor(INK)
        canv.drawString(20 * mm, h - 11.5 * mm, self.header_left)
        canv.setFont("Helvetica", 7)
        right = ("PART %s · %s" % (self.letter, self.title)) if self.letter else self.title
        canv.drawRightString(w - 20 * mm, h - 11.5 * mm, right)
        canv.setFillColor(MUTED)
        canv.setFont("Helvetica", 6.8)
        foot = ("Part %s · %s" % (self.letter, self.title)) if self.letter else self.title
        canv.drawString(20 * mm, 9 * mm, "%s · %s · working production document — verify on site" % (foot, REV))
        canv.drawRightString(w - 20 * mm, 9 * mm, "%d" % doc.page)
        canv.restoreState()

    def add(self, *items):
        for it in items:
            if isinstance(it, (list, tuple)):
                self.story.extend(it)
            else:
                self.story.append(it)

    def build(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.doc.build(self.story)
        return self.path


def title_block(kicker, title, sub):
    return [Paragraph(md(kicker), ParagraphStyle("k", parent=S["muted"], textColor=INK,
                                                   fontName="Helvetica-Bold")),
            Spacer(0, 2), Paragraph(md(title), S["title"]), Spacer(0, 3),
            Paragraph(md(sub), S["sub"]), Spacer(0, 8)]





# --------------------------------------------------------------------------
# Colour swatches and pictures
# --------------------------------------------------------------------------
from reportlab.graphics.shapes import Drawing, Rect, String  # noqa: E402
from reportlab.platypus import Image as RLImage  # noqa: E402

GROUP_ORDER = ["FOH", "LX1", "SIDE", "BACK", "PIX", "SPC"]
GROUP_SHORT = {"FOH": "Face", "LX1": "Top", "SIDE": "Side", "BACK": "Back", "PIX": "Pix", "SPC": "Spec"}


def _hexcol(h, level):
    """Colour shown at its level, printer-friendly: paler for lower intensity (blank = off)."""
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    k = 0.3 + 0.55 * level / 100
    return colors.Color(1 - k + r * k, 1 - k + g * k, 1 - k + b * k)


def swatch_strip(summary, cell=9 * mm, h=5.2 * mm, labels=False):
    """One small block per layer: colour at its level; outlined blank = off."""
    n = len(GROUP_ORDER)
    d = Drawing(cell * n, h + (7 if labels else 0))
    for i, g in enumerate(GROUP_ORDER):
        lv, cols = summary.get(g, (0, []))
        x = i * cell
        if lv and cols:
            parts = cols[:2]
            w = (cell - 1) / len(parts)
            for j, (hx, _) in enumerate(parts):
                d.add(Rect(x + j * w, 0, w, h, fillColor=_hexcol(hx, lv), strokeColor=None))
        else:
            d.add(Rect(x + 0.3, 0.3, cell - 1.6, h - 0.6, fillColor=None, strokeColor=RULE, strokeWidth=0.5))
        if labels:
            d.add(String(x + (cell - 1) / 2, h + 1.5, GROUP_SHORT[g], fontName="Helvetica",
                         fontSize=5.5, fillColor=MUTED, textAnchor="middle"))
    return d


def swatch_legend():
    return P("Swatch order: **Face** (FOH #1, 4, 5, 8, 9, 12) · **Top** (LX1 #13–18) · **Side** (booms) · **Back** "
             "(LX2 COB) · **Pix** (PixBars) · **Spec** (specials). Colour as programmed in the show "
             "file, paler = lower level, blank outline = off.", "muted")


def picture(path, width, height=None):
    from PIL import Image as PILImage
    w, h = PILImage.open(path).size
    height = height or width * h / w
    return RLImage(path, width=width, height=height)


def describe(summary, keys=("FOH", "LX1", "SIDE", "BACK", "PIX")):
    """'Face 55% cool white · Top 55% cyan …' for a group summary."""
    out = []
    for g in keys:
        lv, cols = summary.get(g, (0, []))
        if lv:
            out.append("%s %d%% %s" % (GROUP_SHORT[g], lv, " + ".join(n for _, n in cols[:2])))
    return " · ".join(out) if out else "all out"


def section_strip(summaries, width, h=4.2 * mm):
    """Several cues side by side (one 6-layer block each) in a fixed width."""
    n = max(len(summaries), 1)
    gap = 1.2 * mm
    cell = (width - gap * (n - 1)) / (n * len(GROUP_ORDER))
    d = Drawing(width, h)
    x = 0
    for summ in summaries:
        for g in GROUP_ORDER:
            lv, cols = summ.get(g, (0, []))
            if lv and cols:
                d.add(Rect(x, 0, cell, h, fillColor=_hexcol(cols[0][0], lv), strokeColor=None))
            else:
                d.add(Rect(x + 0.2, 0.2, cell - 0.4, h - 0.4, fillColor=None, strokeColor=RULE, strokeWidth=0.3))
            x += cell
        x += gap
    return d
