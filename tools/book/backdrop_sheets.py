"""Part I2 — Backdrop Sheets: one A4 landscape page per backdrop, full-width image, where it plays, and a notes area."""
import io
import os
import re

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from core import NAVY, TEAL, CORAL, REV, DATE, colors
import part_i
import show as S_

W, H = landscape(A4)
HERE = os.path.dirname(os.path.abspath(__file__))
STILLS = os.path.join(HERE, "..", "..", "production", "assets", "stills")
INK = colors.black
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#c9d2dc")


def still(bg):
    f = next((x for x in sorted(os.listdir(STILLS)) if x.startswith(bg + "_")), None)
    if not f:
        return None
    im = Image.open(os.path.join(STILLS, f)).convert("RGB")
    im.thumbnail((1800, 1800))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    buf.seek(0)
    return ImageReader(buf)


def usage():
    """{BG-xx: [(cue, 'loop'|'still', moment, look)]} from the workspace's video cues."""
    out = {}
    for n, kind, f in part_i.cue_plan():
        if kind != "in" or not f:
            continue
        bg = os.path.basename(f).split("_")[0]
        c = S_.CUE.get(n, {})
        out.setdefault(bg, []).append((n, "still" if f.startswith("stills") else "loop", c.get("name", ""), c.get("look", "")))
    return out


def wrap(c, text, x, y, width, size, lead, color=INK, font="Helvetica", max_lines=99):
    c.setFont(font, size)
    c.setFillColor(color)
    words, line, n = text.split(), "", 0
    for w in words:
        t = (line + " " + w).strip()
        if c.stringWidth(t, font, size) > width and line:
            c.drawString(x, y, line)
            y -= lead
            n += 1
            line = w
            if n >= max_lines:
                return y
        else:
            line = t
    if line:
        c.drawString(x, y, line)
        y -= lead
    return y


def page(c, bg, info, used, idx, total):
    title, prompt, motion, note = info
    m = 10 * mm
    # header
    c.setFillColor(NAVY)
    c.rect(0, H - 16 * mm, W, 16 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(m, H - 10.5 * mm, bg)
    c.setFont("Helvetica", 13)
    c.drawString(m + 26 * mm, H - 10.5 * mm, title)
    tag = "IN THE SHOW" if used else "SPARE"
    c.setFillColor(TEAL if used else CORAL)
    tw = c.stringWidth(tag, "Helvetica-Bold", 8) + 8 * mm
    c.roundRect(W - m - tw, H - 12 * mm, tw, 7 * mm, 3.5 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W - m - tw / 2, H - 9.6 * mm, tag)

    # image, full width 16:9
    iw = 238 * mm
    ih = iw * 9 / 16
    ix = (W - iw) / 2
    iy = H - 19 * mm - ih
    img = still(bg)
    if img:
        c.drawImage(img, ix, iy, iw, ih)
    else:
        c.setFillColor(colors.HexColor("#e8edf2"))
        c.rect(ix, iy, iw, ih, fill=1, stroke=0)
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.rect(ix, iy, iw, ih, fill=0, stroke=1)

    # bottom band: where it plays + motion (left), notes (right)
    top = iy - 4 * mm
    lw = 105 * mm
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(m, top, "WHERE IT PLAYS")
    y = top - 4 * mm
    if used:
        for n, kind, moment, look in used[:3]:
            c.setFont("Helvetica-Bold", 7.2)
            c.setFillColor(INK)
            c.drawString(m, y, "Q%s" % n)
            c.setFont("Helvetica", 7.2)
            s = "%s (%s) · %s" % (moment, kind, re.sub(r"\s+", " ", look))
            wrap(c, s, m + 12 * mm, y, lw - 12 * mm, 7.2, 3.3 * mm, max_lines=1)
            y -= 3.6 * mm
        if len(used) > 3:
            c.setFont("Helvetica", 6.8)
            c.setFillColor(MUTED)
            c.drawString(m, y, "also " + ", ".join("Q" + u[0] for u in used[3:]))
            y -= 3.6 * mm
    else:
        c.setFont("Helvetica", 7.2)
        c.setFillColor(INK)
        c.drawString(m, y, "Not in the cue plan — spare.")
        y -= 3.6 * mm
    y -= 1.5 * mm
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(m, y, "MOTION")
    y = wrap(c, motion or "Still image.", m, y - 3.6 * mm, lw, 6.8, 3.1 * mm, INK, max_lines=2) - 1.5 * mm
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(m, y, "NOTE")
    wrap(c, note, m, y - 3.6 * mm, lw, 6.8, 3.1 * mm, INK, max_lines=3)

    nx = m + lw + 6 * mm
    nw = W - m - nx
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(nx, top, "NOTES")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.5)
    c.drawRightString(W - m, top, "focus · brightness on the wall · lighting washout · timing · changes")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    ly = top - 7 * mm
    while ly > 10 * mm:
        c.line(nx, ly, W - m, ly)
        ly -= 6.5 * mm

    # footer
    c.setFont("Helvetica", 6)
    c.setFillColor(MUTED)
    c.drawString(m, 5 * mm, "Part I2 · Backdrop Sheets · %s · %s · The Little Mermaid · Plantagenet Hall" % (REV, DATE))
    c.drawRightString(W - m, 5 * mm, "%d / %d" % (idx, total))


def build(path):
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Backdrop Sheets")
    use = usage()
    items = sorted(part_i.BACKDROPS.items())
    for i, (bg, info) in enumerate(items, 1):
        page(c, bg, info, use.get(bg, []), i, len(items))
        c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else "Backdrop_Sheets.pdf"))
