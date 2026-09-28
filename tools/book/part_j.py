"""Part J — Prompt Copy (PRIVATE).

Built from the licensed script (production/private/, gitignored): each script page is reduced onto an A4 page with a
cue margin (amber standbys, green GOs, blue song starts) taken from the calling script. The output contains the
licensed text, so it is written to production/private only and must never be committed to this public repo.
"""
import os

import pymupdf

import calls
import show as S_
from core import REV, DATE

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "..", "production", "private", "TLM_Script_Revised_April_2026.pdf")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
AMBER, GREEN, BLUE, NAVY, GREY = (0.93, 0.55, 0.05), (0.1, 0.55, 0.3), (0.15, 0.4, 0.75), (0.07, 0.16, 0.29), (0.45, 0.45, 0.5)


def margin_notes():
    notes = {}
    songs_after = {str(s["at"]): s for s in S_.SONGS}
    for title, _pages, cues in calls.SCENES:
        for q, sp, sl, gp, gl, depts, what, note in cues:
            if sp.isdigit():
                notes.setdefault(int(sp), []).append(("SB", q, depts, sl, ""))
            if gp.isdigit():
                notes.setdefault(int(gp), []).append(("GO", q, depts, gl, what + (" · " + note if note else "")))
                if q in songs_after:
                    s = songs_after[q]
                    notes[int(gp)].append(("SONG", s["num"], "QLab · P4 M%d" % s["mem"],
                                           s["title"], "%d section GOs to the music" % len(s["sections"])))
    return notes


def build(path):
    src = pymupdf.open(SCRIPT)
    out = pymupdf.open()
    notes = margin_notes()
    W, H = pymupdf.paper_size("a4")

    # cover
    pg = out.new_page(width=W, height=H)
    pg.insert_font("dj", fontfile=FONT)
    pg.insert_font("djb", fontfile=FONTB)
    pg.draw_rect(pymupdf.Rect(0, 0, W, 190), color=None, fill=NAVY)
    pg.insert_text((50, 90), "PART J", fontname="djb", fontsize=14, color=(1, 1, 1))
    pg.insert_text((50, 130), "Prompt Copy — Licensed Script", fontname="djb", fontsize=24, color=(1, 1, 1))
    pg.insert_text((50, 160), "The Little Mermaid · %s · %s" % (REV, DATE), fontname="dj", fontsize=11, color=(1, 1, 1))
    body = ("The licensed script (Nick Lawrence Pantomimes, revised April 2026), %d pages, with every R13.1 cue in the margin.\n\n"
            "AMBER  SB = standby, on the line shown.\n"
            "GREEN  GO = the QLab GO; departments and what happens.\n"
            "BLUE   SONG = the song group fires straight after the GO; its section GOs follow the music.\n\n"
            "Page numbers match the script's own numbering and the calling script (Part G).\n"
            "Write blocking in pencil in the space left of the cue margin.\n\n"
            "Script gaps to raise with the director:\n"
            "  • The contents page lists Scene Eleven: On the Shore (p 55) but there is no text for it.\n"
            "  • The Scene Five song listed on the contents page is not in the text.\n"
            "  • The character page names the sisters Persil, Lenor, Daz and Own Brand; the casting sheet has\n"
            "    Scarlotte, Paulette, Charlotte and Kandy.\n\n"
            "LICENSED MATERIAL — for this production's prompt desk only. Do not copy, share or upload publicly.") % src.page_count
    pg.insert_textbox(pymupdf.Rect(50, 220, W - 50, H - 60), body, fontname="dj", fontsize=10.5, color=NAVY, lineheight=1.35)

    sx = 0.70
    for i in range(src.page_count):
        n = i + 1
        pg = out.new_page(width=W, height=H)
        pg.insert_font("dj", fontfile=FONT)
        pg.insert_font("djb", fontfile=FONTB)
        sw, sh = src[i].rect.width * sx, src[i].rect.height * sx
        r = pymupdf.Rect(18, (H - sh) / 2, 18 + sw, (H + sh) / 2)
        pg.draw_rect(r, color=(0.8, 0.8, 0.85), width=0.5)
        pg.show_pdf_page(r, src, i)
        x0 = r.x1 + 8
        pg.draw_line((x0 - 4, 30), (x0 - 4, H - 30), color=(0.8, 0.8, 0.85), width=0.5)
        pg.insert_text((x0, 30), "CUES · p %d" % n, fontname="djb", fontsize=8, color=NAVY)
        y = 42
        for kind, q, depts, line, what in notes.get(n, []):
            col = {"SB": AMBER, "GO": GREEN, "SONG": BLUE}[kind]
            head = "%s %s%s" % (kind, "Q" if kind != "SONG" else "", q)
            pg.draw_rect(pymupdf.Rect(x0, y, W - 12, y + 11), color=None, fill=col)
            pg.insert_text((x0 + 3, y + 8.3), head, fontname="djb", fontsize=7.5, color=(1, 1, 1))
            pg.insert_text((x0 + 58, y + 8.3), depts[:22], fontname="dj", fontsize=6, color=(1, 1, 1))
            y += 13
            txt = line + ("\n" + what if what else "")
            box = pymupdf.Rect(x0, y, W - 12, y + 80)
            rc = pg.insert_textbox(box, txt, fontname="dj", fontsize=6.4, color=(0.15, 0.15, 0.2), lineheight=1.2)
            used = 80 - rc if rc >= 0 else 80
            y += used + 5
            if y > H - 40:
                break
        pg.insert_text((x0, H - 18), "Part J · %s · licensed — do not share" % REV, fontname="dj", fontsize=5.5, color=GREY)
    out.save(path, garbage=3, deflate=True)
    return path
