#!/usr/bin/env python3
"""Build the R13.1 printouts (operator cue sheets + Mantra desk labels).

Everything is read from the show files in the package, so the printouts
always match what QLab and the Mantra actually do:
  - TLM_Show_R13_1.qlab5                       cue order, triggers, media, OSC
  - TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr   memory names, chases, patch
  - R13_MANTRA_SECTION_MAP.csv                 P8 backup positions, cue names

Usage:  python3 tools/make_printouts.py            (needs reportlab)
Output: package/TLM_R13_REBUILT_Show_Files/docs/TLM_R13_1_Operator_Cue_Sheets.pdf
        package/TLM_R13_REBUILT_Show_Files/docs/TLM_R13_1_Mantra_Labels.pdf
"""
import csv
import os
import plistlib
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(ROOT, "package", "TLM_R13_REBUILT_Show_Files")
QLAB = os.path.join(SHOW, "TLM_Show_R13_1.qlab5")
MTR = os.path.join(SHOW, "TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr")
MAP = os.path.join(SHOW, "R13_MANTRA_SECTION_MAP.csv")
OUT = os.path.join(SHOW, "docs")

REV = "R13.1"
DATE = "28 Sep 2026"
SHOWNAME = "THE LITTLE MERMAID · Plantagenet Hall"

for name, f in (("Sans", "DejaVuSans.ttf"), ("Sans-Bold", "DejaVuSans-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(name, "/usr/share/fonts/truetype/dejavu/" + f))

INK = colors.black
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#b9c2cc")
HEAD = colors.HexColor("#123a5a")
TINT = colors.HexColor("#fdf1ea")   # critical rows (pale: printer-friendly)
SONG = colors.HexColor("#f0f6fc")   # song rows
AUTO = colors.HexColor("#f4f9f0")   # auto-follow rows

# --------------------------------------------------------------------------
# QLab workspace
# --------------------------------------------------------------------------

def _unarchive(data):
    """Resolve an NSKeyedArchiver plist into plain dicts/lists (no cycles)."""
    objs = data["$objects"]

    def res(x, stack=()):
        if isinstance(x, plistlib.UID):
            if x.data in stack:
                return None
            stack = stack + (x.data,)
            x = objs[x.data]
        if isinstance(x, dict):
            if "NS.keys" in x:
                return {str(res(k, stack)): res(v, stack)
                        for k, v in zip(x["NS.keys"], x["NS.objects"])}
            if "NS.objects" in x:
                return [res(v, stack) for v in x["NS.objects"]]
            if "NS.string" in x:
                return x["NS.string"]
            if "NS.data" in x:
                return x["NS.data"]
            return {k: res(v, stack) for k, v in x.items() if k != "$class"}
        if isinstance(x, list):
            return [res(v, stack) for v in x]
        if x == "$null":
            return None
        return x

    return res(data["$top"]["root"])


def load_qlab():
    ws = _unarchive(plistlib.load(open(QLAB, "rb")))
    lists = _unarchive(plistlib.loads(ws["cueLists"]))
    main = lists["cues"][0]
    assert main.get("name") == "Main Cue List", main.get("name")
    return main["cues"]


def note_text(c):
    n = c.get("notes")
    return (n.get("NSString", "") if isinstance(n, dict) else n or "").strip()


def note_fields(text):
    out = {}
    for part in text.split(" | "):
        if ": " in part:
            k, v = part.split(": ", 1)
            out[k.strip()] = v.strip()
    return out


OSC = re.compile(r"Page=(\d+)/Memory=(\d+)/Cue=(\d+)/Level=(\d+)/Fade=(\d+)")


def file_of(c):
    ft = c.get("fileTarget")
    return ft.get("relativePath") if isinstance(ft, dict) else None


def bg_code(path):
    m = re.search(r"(BG-\d+|VID-\d+)", path or "")
    return m.group(1) if m else ""


# The untouched R13 placeholder sounds are the ones bundled in the package
# media folder, minus the new files R13.1 added (listed in the retarget map).
NEW_FILES = {os.path.basename(r["New_file"]) for r in
             csv.DictReader(open(os.path.join(SHOW, "R13_1_SFX_RETARGET_MAP.csv"), newline=""))}
PLACEHOLDERS = set()
for dp, _, fs in os.walk(os.path.join(SHOW, "media")):
    PLACEHOLDERS.update(f for f in fs if f not in NEW_FILES)


def audio_label(c):
    path = file_of(c) or ""
    base = os.path.basename(path)
    label = re.sub(r"^SFX\s+", "", c.get("name", ""))
    if base in PLACEHOLDERS:
        label += " [silent placeholder]"
    elif "swap for backing" in base:
        label += " [vocal - swap for backing]"
    return label


def parse_group(g):
    d = {"num": g.get("number", ""), "name": g.get("name", ""),
         "notes": note_text(g), "video": [], "audio": [], "mantra": [],
         "release": [], "fades": [], "other": [], "track": None}
    d["f"] = note_fields(d["notes"])
    for c in g.get("cues") or []:
        nm = c.get("name", "")
        pre = c.get("preWait") or 0
        m = OSC.search(nm)
        if nm.startswith("MANTRA RELEASE") and m:
            d["release"].append(tuple(int(x) for x in m.groups()))
        elif nm.startswith("MANTRA") and m:
            p, mem, cue, lvl, fade = (int(x) for x in m.groups())
            d["mantra"].append({"p": p, "m": mem, "c": cue, "lvl": lvl,
                                "fade": fade / 1000, "pre": pre,
                                "num": c.get("number", ""),
                                "cont": c.get("continueMode", 0)})
        elif nm.startswith("VIDEO"):
            d["video"].append(bg_code(file_of(c)) or bg_code(nm))
        elif nm.startswith("SFX"):
            d["audio"].append((audio_label(c), pre))
        elif " TRACK " in nm:
            d["track"] = (nm.split(" TRACK ", 1)[1], os.path.basename(file_of(c) or ""))
        elif nm.startswith(("FADE OUT Q", "FADE TO")):
            d["fades"].append(nm)
        elif nm.startswith(("FADE IN VIDEO", "FADE OUT VIDEO")):
            pass
        else:
            d["other"].append(nm)
    return d


# --------------------------------------------------------------------------
# Mantra file and section map
# --------------------------------------------------------------------------

def load_mtr():
    t = open(MTR, encoding="latin-1").read()
    secs = re.split(r"^\[([^\]]+)\]\s*$", t, flags=re.M)
    d = {secs[i]: secs[i + 1] for i in range(1, len(secs), 2)}

    def kv(sec):
        return dict(l.split("=", 1) for l in d.get(sec, "").splitlines() if "=" in l)

    mems = {}
    for k in d:
        m = re.fullmatch(r"Memory(\d+)", k)
        if m:
            i = int(m.group(1))
            head, c0 = kv(k), kv(k + "-Cue0")
            mems[i] = {"name": c0.get("Name", ""), "chase": head.get("IsChase") == "true",
                       "bpm": head.get("ChaseBpm"), "steps": int(head.get("NumScenes", 1))}
    return mems


def load_map():
    rows = list(csv.DictReader(open(MAP, newline="")))
    by_pmc = {}
    for r in rows:
        key = (int(r["Performance Page"]), int(r["Playback Memory"]), int(r["Cue In Section"]))
        by_pmc[key] = r
    return rows, by_pmc


# --------------------------------------------------------------------------
# PDF helpers
# --------------------------------------------------------------------------

def styles(size=7.2):
    base = ParagraphStyle("b", fontName="Sans", fontSize=size, leading=size * 1.22, textColor=INK)
    return {
        "b": base,
        "bb": ParagraphStyle("bb", parent=base, fontName="Sans-Bold"),
        "h": ParagraphStyle("h", parent=base, fontName="Sans-Bold", textColor=INK),
        "m": ParagraphStyle("m", parent=base, textColor=MUTED, fontSize=size - 0.6),
        "title": ParagraphStyle("t", parent=base, fontName="Sans-Bold", fontSize=13, leading=16, textColor=INK),
        "sub": ParagraphStyle("s", parent=base, fontSize=8, leading=10, textColor=MUTED),
        "note": ParagraphStyle("n", parent=base, fontSize=7.4, leading=9.4),
    }


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def P(text, st):
    return Paragraph(text if isinstance(text, str) else esc(text), st)


def make_table(header, rows, widths, st, row_styles=(), interval_after=None):
    data = [[P("<b>%s</b>" % esc(h), st["h"]) for h in header]]
    for r in rows:
        data.append([c if not isinstance(c, str) else P(c, st["b"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    cmds = [
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
    ]
    for i, kind in row_styles:
        colour = {"crit": TINT, "song": SONG, "auto": AUTO}[kind]
        cmds.append(("BACKGROUND", (0, i + 1), (-1, i + 1), colour))
    if interval_after is not None:
        cmds.append(("LINEBELOW", (0, interval_after + 1), (-1, interval_after + 1), 2.2, INK))
    t.setStyle(TableStyle(cmds))
    return t


class Doc:
    def __init__(self, path, title, footer, pagesize):
        self.footer, self.title = footer, title
        self.doc = SimpleDocTemplate(path, pagesize=pagesize, title=title,
                                     author="TLM production", leftMargin=10 * mm,
                                     rightMargin=10 * mm, topMargin=10 * mm,
                                     bottomMargin=12 * mm)

    def _decorate(self, canv, doc):
        canv.saveState()
        w, _ = doc.pagesize
        canv.setFont("Sans", 6.5)
        canv.setFillColor(MUTED)
        canv.drawString(10 * mm, 6 * mm, self.footer)
        canv.drawRightString(w - 10 * mm, 6 * mm, "page %d" % doc.page)
        canv.restoreState()

    def build(self, story):
        self.doc.build(story, onFirstPage=self._decorate, onLaterPages=self._decorate)


def sheet_head(title, sub, st):
    return [P(esc(SHOWNAME) + " · " + esc(title), st["title"]), P(sub, st["sub"]), Spacer(0, 2.5 * mm)]


def strip(text, st):
    t = Table([[P(text, st["note"])]], colWidths=[277 * mm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, HEAD),
                           ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f6f9")),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return [Spacer(0, 2 * mm), t]


# --------------------------------------------------------------------------
# Cue sheets
# --------------------------------------------------------------------------

def song_sections(notes):
    m = re.search(r"Sections: (.*?)(?: \| |$)", notes)
    out = {}
    if m:
        for part in m.group(1).split(" / "):
            k, _, v = part.partition(" ")
            out[k] = v
    return out


def song_title(g):
    return re.sub(r"\s*\(S\d+\) - at Q\d+$", "", g["name"])


# Optional {cue number: script page} from the production book's calling script; when set, it replaces the
# old production-copy "(pNN)" page references carried in the QLab cue notes.
PAGE_OVERRIDE = {}


def page_ref(trigger, num=None):
    if num in PAGE_OVERRIDE:
        return "p%s" % PAGE_OVERRIDE[num]
    m = re.search(r"\(p(\d+)\)", trigger)
    return "p" + m.group(1) if m else ""


def trigger_text(trigger):
    return re.sub(r"\s*\(p\d+\)", "", trigger) if PAGE_OVERRIDE else trigger


def haze_mark(fx):
    f = fx.lower()
    m = re.search(r"HZ-\d+", fx)
    if "haze off" in f or "clear haze" in f or re.search(r"hz-\d+ off", f) or "reduce/off" in f:
        return (m.group(0) + " " if m else "") + "OFF"
    if "optional" in f and "haze" in f:
        return "opt"
    if "haze" in f or m or "burst" in f:
        return (m.group(0) + " " if m else "") + "ON"
    return ""


def water_mark(fx):
    f = fx.lower()
    return "WATER" if re.search(r"\b(water|pistols?|wet)\b", f) else ""


def is_critical(g):
    fx = g["f"].get("FX", "").lower()
    return (any(x["pre"] for x in g["mantra"]) or g["num"] in ("57", "57b")
            or bool(water_mark(fx)))


def build_cue_sheets(groups, by_pmc, mems):
    st = styles()
    footer = ("Cue sheets %s · %s · built from TLM_Show_R13_1.qlab5 + %s · "
              "tinted = critical (flash / water) · blue = song · heavy rule = interval · "
              "write final page/line in pencil" % (REV, DATE, os.path.basename(MTR)))
    path = os.path.join(OUT, "TLM_R13_1_Operator_Cue_Sheets.pdf")
    doc = Doc(path, "TLM R13.1 Operator Cue Sheets", footer, landscape(A4))
    story = []

    show = [g for g in groups if g["num"] and not g["num"].startswith("E") and g["num"] != "66"]
    emerg = [g for g in groups if g["num"].startswith("E")]
    songs = {g["num"]: g for g in show if g["num"].startswith("S")}

    # ---------------- SM master calls ----------------
    story += sheet_head("STAGE MANAGER — MASTER CALLS",
                        "Every QLab GO in the show. Song sections (S#.2 onward) are further GOs "
                        "inside the song — the SM calls them to the music, or delegates them to the QLab op.", st)
    rows, rs, interval = [], [], None
    for g in show:
        f = g["f"]
        if g["num"].startswith("S"):
            secs = list(song_sections(g["notes"]).items())
            at = re.search(r"At show cue Q(\S+)", g["notes"])
            rest = " · ".join("%s %s" % kv for kv in secs[1:])
            rows.append(["<b>%s</b>" % g["num"],
                         "<b>%s</b>" % esc(song_title(g)),
                         "Straight after Q%s — song starts" % at.group(1) if at else "",
                         "P4 M%d song look" % g["mantra"][0]["m"] if g["mantra"] else "",
                         "●", "", "",
                         "%d GOs — then %s" % (len(secs), esc(rest))])
            rs.append((len(rows) - 1, "song"))
            continue
        trig = f.get("Trigger", "")
        vid = " ".join(v for v in g["video"] if v)
        fx = f.get("FX", "")
        fxm = " ".join(x for x in (haze_mark(fx), water_mark(fx)) if x)
        rows.append(["<b>%s</b>" % esc(g["num"]), esc(g["name"]), esc(trigger_text(trig)), esc(f.get("LX", "")),
                     "●" if (g["audio"] or g["track"]) else "", esc(vid), esc(fxm), page_ref(trig, g["num"])])
        if is_critical(g):
            rs.append((len(rows) - 1, "crit"))
        if g["num"] == "38":
            interval = len(rows) - 1
    story.append(make_table(["Q", "Moment", "Call on (trigger)", "LX look", "SND", "VID", "FX", "Page"],
                            rows, [12 * mm, 40 * mm, 62 * mm, 55 * mm, 9 * mm, 16 * mm, 20 * mm, 63 * mm],
                            st, rs, interval))
    story += strip("<b>Calls:</b> STANDBY · GO · HOLD · GO LX ONLY · GO SOUND ONLY · STOP PLAYBACK &nbsp;&nbsp; "
                   "<b>Recovery:</b> SAFE LIGHT = Mantra P2 M10 (QLab E3) · QLab E1 STOP ALL · E2 VID-99 BLACK &nbsp;&nbsp; "
                   "<b>Flash returns are automatic</b> (Q21, Q23, Q25, Q35, Q47, Q57b) — call one GO per flash.", st)
    story.append(PageBreak())

    # ---------------- QLab operator ----------------
    story += sheet_head("QLAB OPERATOR — GO LIST",
                        "One row per GO. Green rows fire automatically inside the cue. Mantra targets are "
                        "P/M/cue on the split pages; 'rel' = the memory QLab releases (Level 0) as it moves on.", st)
    rows, rs, interval = [], [], None
    for g in show:
        f = g["f"]
        if g["num"].startswith("S"):
            secs = song_sections(g["notes"])
            track = g["track"][0] if g["track"] else ""
            fn = g["track"][1] if g["track"] else ""
            flag = ""
            if "swap for backing" in fn:
                flag = " <b>[vocal — swap for backing]</b>"
            if "TBA" in fn or "to be decided" in track.lower():
                flag = " <b>[song still to choose]</b>"
            for k, x in enumerate(x for x in g["mantra"]):
                sec = secs.get(x["num"], "")
                if k == 0:
                    what = "<b>TRACK</b> %s%s + P4 M%d cue %d %s" % (esc(track), flag, x["m"], x["c"], esc(sec))
                    rel = " · rel " + ", ".join("P%d M%d" % (p, m) for p, m, *_ in g["release"]) if g["release"] else ""
                    rows.append(["<b>%s</b>" % g["num"], "<b>%s</b>" % esc(song_title(g)), what + rel,
                                 "%.2g s" % x["fade"], "at Q" + g["notes"].split("At show cue Q")[1].split(" ")[0]
                                 if "At show cue Q" in g["notes"] else ""])
                else:
                    rows.append([x["num"], esc(sec), "P4 M%d cue %d" % (x["m"], x["c"]),
                                 "%.2g s" % x["fade"], "on the music"])
                rs.append((len(rows) - 1, "song"))
            continue
        parts = []
        if g["video"]:
            parts.append("<b>VID</b> " + esc(" ".join(g["video"])))
        for a, pre in g["audio"]:
            parts.append("<b>SFX</b> " + esc(a) + (" (+%gs)" % pre if pre else ""))
        main = [x for x in g["mantra"] if not x["pre"]]
        for x in main:
            if x["p"] == 5:
                parts.append("<b>LX</b> P5 M%d %s %s" % (x["m"], mems.get(40 + x["m"] - 1, {}).get("name", "").split(" ")[0],
                                                         "ON" if x["lvl"] else "OFF"))
            else:
                parts.append("<b>LX</b> P%d M%d cue %d" % (x["p"], x["m"], x["c"]))
        if g["release"]:
            parts.append("rel " + ", ".join("P%d M%d" % (p, m) for p, m, *_ in g["release"]))
        stops = [re.sub(r"^FADE (OUT|TO (-?\d+ dB)) (Q\S+).*", lambda m: (m.group(3) + (" to " + m.group(2) if m.group(2) else " out")), s)
                 for s in g["fades"]]
        if stops:
            parts.append("fades: " + esc(", ".join(stops)))
        fade = "%.2g s" % main[0]["fade"] if main else ""
        rows.append(["<b>%s</b>" % esc(g["num"]), esc(g["name"]), " · ".join(parts), fade, esc(f.get("FX", ""))])
        if is_critical(g):
            rs.append((len(rows) - 1, "crit"))
        for x in g["mantra"]:
            if x["pre"]:
                rows.append(["", "↳ auto +%gs" % x["pre"], "<b>LX</b> P%d M%d cue %d (flash return — no GO)" % (x["p"], x["m"], x["c"]),
                             "%.2g s" % x["fade"], ""])
                rs.append((len(rows) - 1, "auto"))
        if g["num"] == "38":
            interval = len(rows) - 1
    story.append(make_table(["GO", "Cue", "What fires", "LX fade", "Note / mic / FX"],
                            rows, [13 * mm, 44 * mm, 150 * mm, 14 * mm, 56 * mm], st, rs, interval))
    em = " · ".join("<b>%s</b> %s" % (esc(g["num"]), esc(g["name"])) for g in emerg)
    story += strip("<b>Emergency cues (below Q66):</b> %s &nbsp;&nbsp; Esc = Panic (all QLab). Live mics never depend on QLab; "
                   "QLab return = StudioLive ch 11-12. <b>Swapping audio:</b> always save under a NEW filename and drag it onto the cue." % em, st)
    story.append(PageBreak())

    # ---------------- Lighting ----------------
    story += sheet_head("LIGHTING — MANTRA LITE (backup to QLab)",
                        "QLab fires every lighting cue. If QLab or the network fails, run from the split page/memory "
                        "below with Next Cue. P8 position = same cue on the full 153-step backup list.", st)
    rows, rs, interval = [], [], None
    order = []
    for g in show:
        for x in g["mantra"]:
            if x["p"] in (2, 3, 4):
                order.append((g, x))
    for g, x in order:
        r = by_pmc.get((x["p"], x["m"], x["c"]), {})
        q = g["num"] if not g["num"].startswith("S") else x["num"]
        if x["pre"]:  # auto flash return: use the desk cue's own label (21b, 57c...)
            q = r.get("Cue Name", q).split(" ")[0]
        auto = "auto +%gs" % x["pre"] if x["pre"] else ""
        lx = g["f"].get("LX", "") if not g["num"].startswith("S") else ""
        if g["num"].startswith("S"):
            lx = song_sections(g["notes"]).get(x["num"], "")
        extra = ""
        if g["num"] == "57" and x["c"] == 8:
            extra = " + P5 M5 HAYWIRE chase ON"
        if g["num"] == "57b" and x["c"] == 9:
            extra = " + HAYWIRE chase OFF"
        rows.append(["<b>%s</b>" % esc(q), "P%d M%d · %d" % (x["p"], x["m"], x["c"]), r.get("Backup Position", ""),
                     esc(r.get("Cue Name", "")), "%.2g" % x["fade"], auto, esc(lx) + extra])
        if x["pre"] or g["num"] in ("57", "57b") or (x["fade"] == 0 and x["p"] != 4 and x["c"] != 1):
            rs.append((len(rows) - 1, "crit" if not x["pre"] else "auto"))
        elif g["num"].startswith("S"):
            rs.append((len(rows) - 1, "song"))
        if g["num"] == "38":
            interval = len(rows) - 1
    story += strip("<b>Run P2 (Act One), P3 (Act Two), P4 (songs).</b> Flash returns are fired by QLab — manually, press Next Cue again after each flash. "
                   "<b>P5:</b> M1 Warm chase · M2 Cool chase · M3 Party chase · M4 HAZE · M5 HAYWIRE (Q57 → Q57b) · M6 Jelly pulse. "
                   "<b>SAFE LIGHT = P2 M10.</b> O = All Cues Off · A then L = Clear All · T then S = Save. "
                   "Lost? SAFE LIGHT, confirm the scene with SM, pick the matching P2/P3 memory. Don't replay a missed flash.", st)
    story.append(Spacer(0, 2 * mm))
    story.append(make_table(["Q", "Page · Mem · cue", "P8 pos", "Mantra cue name", "Fade s", "Auto", "Look / note"],
                            rows, [15 * mm, 28 * mm, 13 * mm, 44 * mm, 13 * mm, 18 * mm, 146 * mm], st, rs, interval))
    story.append(PageBreak())

    # ---------------- Haze / FX / deck ----------------
    story += sheet_head("HAZE / FX + DECK",
                        "Haze = hazer #40, Mantra P5 M4 (or local on the hazer). Bursts go 20–40 s before the look that needs them.", st)
    rows, rs, interval = [], [], None
    skip = {"-", "", "no effect", "no extra effect"}
    for g in show:
        if g["num"].startswith("S"):
            continue
        fx = g["f"].get("FX", "")
        if fx.lower() in skip or re.search(r"\b(mix|mic|mics)\b", fx.lower()) and not haze_mark(fx):
            if g["num"] == "38":
                interval = len(rows) - 1
            continue
        rows.append(["<b>%s</b>" % esc(g["num"]), esc(g["name"]), haze_mark(fx), water_mark(fx), esc(fx), ""])
        if water_mark(fx) or "flash" in fx.lower():
            rs.append((len(rows) - 1, "crit"))
        if g["num"] == "38":
            interval = len(rows) - 1
    story.append(make_table(["Q", "Moment", "Haze", "Water", "Action / preset", "Done"],
                            rows, [13 * mm, 55 * mm, 22 * mm, 16 * mm, 156 * mm, 15 * mm], st, rs, interval))
    story += strip("Stop haze or water immediately if visibility, slip or electrical safety is compromised — tell SM on Ch B. "
                   "No strobe is stored in the show; white flash hits in the storm (Q21/23/25), transformation (Q35) and restore (Q57b). "
                   "Flashing-lights / haze notice for the doors: docs/FOH_Flashing_Lights_and_Haze_Notice.pdf.", st)
    doc.build(story)
    return path


# --------------------------------------------------------------------------
# Mantra labels
# --------------------------------------------------------------------------

FIXTURES = [
    ("C42", "FOH", "FACE 1 DSR·HL"), ("C42", "FOH", "FACE 1 DSR·HR"), ("C42", "FOH", "FACE 2 DSC·HL"),
    ("C42", "FOH", "FACE 2 DSC·HR"), ("C42", "FOH", "FACE 3 DSL·HL"), ("C42", "FOH", "FACE 3 DSL·HR"),
    ("C42", "FOH", "SP1 ARIEL"), ("C42", "FOH", "SP2 SPIRIT"), ("C42", "LX1", "SP3 OCTAVIA"),
    ("C42", "LX1", "SP4 SHELL"), ("C42", "LX1", "V1 DAME"), ("C42", "LX1", "V2 FLANDERS"),
    ("ZOOM", "LX1", "WASH DSR"), ("ZOOM", "LX1", "WASH DSC"), ("ZOOM", "LX1", "WASH DSL"),
    ("ZOOM", "LX1", "WASH CSR"), ("ZOOM", "LX1", "WASH CSC"), ("ZOOM", "LX1", "WASH CSL"),
    ("ZOOM", "LX2", "V3 THEODORE"), ("ZOOM", "LX2", "V4 MARINA"), ("ZOOM", "SR BOOM", "HIGH SIDE"),
    ("ZOOM", "SL BOOM", "HIGH SIDE"), ("COB", "LX2", "BACK DSR"), ("COB", "LX2", "BACK DSC"),
    ("COB", "LX2", "BACK DSL"), ("COB", "LX2", "BACK CSR"), ("COB", "LX2", "BACK CSC"),
    ("COB", "LX2", "BACK CSL"), ("COB", "SR BOOM", "MID SIDE"), ("COB", "SR BOOM", "SHIN"),
    ("COB", "SL BOOM", "MID SIDE"), ("COB", "SL BOOM", "SHIN"), ("PIX", "LX2", "PIXBAR 1"),
    ("PIX", "LX2", "PIXBAR 2"), ("PIX", "LX2", "PIXBAR 3"), ("PIX", "LX2", "PIXBAR 4"),
    ("PIX", "LX2", "PIXBAR 5"), ("PIX", "LX2", "PIXBAR 6"), ("COB", "LX2", "BACK CENTRE"),
    ("HAZE", "FLOOR US", "HAZER"), ("PIN", "FOH SR", "PINSPOT (opt)"), ("PIN", "FOH SL", "PINSPOT (opt)"),
] + [("", "", "spare")] * 6

TYPE_COL = {"C42": "#f2c14e", "ZOOM": "#5fa8d3", "COB": "#e07a5f", "PIX": "#9b72cf",
            "HAZE": "#8d99ae", "PIN": "#8d99ae", "": "#ffffff"}


def label_row(cells, st, height=15 * mm, first_col=None):
    widths = [27.7 * mm] * 10
    t = Table([cells], colWidths=widths, rowHeights=[height])
    cmds = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.5), ("RIGHTPADDING", (0, 0), (-1, -1), 1.5)]
    t.setStyle(TableStyle(cmds))
    return t


def build_labels(mems):
    st = styles(7.5)
    cst = ParagraphStyle("c", fontName="Sans-Bold", fontSize=7.6, leading=9, alignment=1, textColor=INK)
    small = ParagraphStyle("cs", fontName="Sans", fontSize=5.8, leading=7, alignment=1, textColor=MUTED)
    footer = ("%s · LSC Mantra Lite + 2 wings · %s · labels %s · %s"
              % (SHOWNAME, os.path.basename(MTR), REV, DATE))
    path = os.path.join(OUT, "TLM_R13_1_Mantra_Labels.pdf")
    doc = Doc(path, "TLM R13.1 Mantra Labels", footer, landscape(A4))
    story = []

    # fixture faders: 4 rows of 12 → two rows of 12 per table, cut lines
    story += [P("Fixture fader labels — Mantra Lite 1–24 · Wing 1 25–36 · Wing 2 37–48", st["title"]),
              P("The venue patch. Cut on the lines and stick one label above each "
                "fixture fader. Numbers = Mantra fixture numbers. Colour bar = fixture type.", st["sub"]),
              Spacer(0, 3 * mm)]
    titles = ["CONSOLE · 1–12", "CONSOLE · 13–24", "WING 1 · 25–36", "WING 2 · 37–48"]
    for blk in range(4):
        cells, cmds = [], []
        for i in range(12):
            n = blk * 12 + i + 1
            typ, pos, role = FIXTURES[n - 1]
            cells.append([P("%d%s" % (n, (" · " + pos) if pos else ""), small),
                          P(esc(role), cst), P(typ, small)])
            cmds.append(("LINEABOVE", (i, 0), (i, 0), 3, colors.HexColor(TYPE_COL[typ])))
        t = Table([cells], colWidths=[23.08 * mm] * 12, rowHeights=[15 * mm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a0")),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1)] + cmds))
        story += [P("<b>%s</b>" % titles[blk], st["m"]), t, Spacer(0, 3 * mm)]
    story.append(P("Lightsky C42 (U2) = yellow · Tour Pro Zoom = blue · TourCOB PAR = orange · PixBar = violet · "
                   "hazer / pinspots = grey. HL/HR = focused from house left / right. SP = character special, "
                   "V = voice-transfer special. #41–42 pinspots only if the mirror ball is used; 43–48 spare. "
                   "Confirm #38 PixBar 6 and #39 TourCOB back centre exist on the rig.", st["note"]))
    story.append(PageBreak())

    # playback rows
    def mem_name(i):
        return mems.get(i, {}).get("name", "")

    def cue_range(i):
        n = mems.get(i, {}).get("steps", 1)
        return n

    pages = []
    pages.append(("PAGE 1 – VENUE / RIG BASE", [
        (0, "STAGE WORK"), (1, "FULL WHITE"), (2, "WARM STAGE"), (3, "COOL STAGE"), (4, "BLUE STAGE"),
        (5, "RED STAGE"), (None, ""), (None, ""), (8, "PIXBAR WASH"), (9, "CURTAIN CALL")]))
    act1 = [(10, "Q1–11 PRESHOW → ARIEL UPSET"), (11, "Q12–17 SINGING LESSON → BLACKOUT"),
            (12, "Q18–27.5 SHIP · STORM"), (13, "Q28–30.5 SHORE · DUET"),
            (14, "Q31–37 BAR · TRANSFORM · ACT 1 END"), (15, "Q38 INTERVAL"), (None, ""), (None, ""),
            (18, "WORK / FOCUS"), (19, "SAFE LIGHT")]
    pages.append(("PAGE 2 – ACT ONE · performance", act1))
    act2 = [(20, "Q39–44 PALACE"), (21, "Q45–49 JELLYFISH"), (22, "Q50–58.5 LAIR · VOICE · HAYWIRE"),
            (23, "Q59–59.7 DRY LAND"), (24, "Q60–63.5 WEDDING"), (25, "Q64–65 BOWS · END"),
            (None, ""), (None, ""), (None, ""), (None, "")]
    pages.append(("PAGE 3 – ACT TWO · performance", act2))
    songs = ["S1 ROCK LOBSTER", "S2 FEELING GOOD", "S3 PART OF YOUR WORLD", "S4 WELLERMAN",
             "S5 TIME OF MY LIFE", "S6 CRAB RAVE", "S7 JELLYFISH CHORUS", "S8 POOR UNFORTUNATE SOULS",
             "S9 ABSOLUTELY EVERYBODY", "S10 HE'S A PIRATE"]
    pages.append(("PAGE 4 – SONGS · performance", [(30 + i, s) for i, s in enumerate(songs)]))
    fx = []
    for i, lab in zip(range(40, 46), ["WARM CHASE", "COOL CHASE", "PARTY CHASE", "HAZE #40", "HAYWIRE chase", "JELLY PULSE"]):
        m = mems.get(i, {})
        sub = ("%d steps @%s BPM" % (m["steps"], m["bpm"])) if m.get("chase") else ""
        fx.append((i, lab + ("|" + sub if sub else "")))
    fx += [(None, "")] * 4
    pages.append(("PAGE 5 – FX / CHASES", fx))
    pages.append(("PAGE 6 – LOOK LIBRARY", [(50 + i, mem_name(50 + i)) for i in range(10)]))
    pages.append(("PAGE 7 – LOOK LIBRARY", [(60 + i, mem_name(60 + i)) for i in range(7)] + [(None, "")] * 3))

    story += [P("Playback labels — 10 playback faders, one row per page", st["title"]),
              P("The show is split: <b>P2 Act One, P3 Act Two, P4 songs</b>. QLab picks the right memory; keep the "
                "P2 row on the desk in Act One, swap to P3 at the interval, and keep P4 handy for song recovery. "
                "Blank cells are empty memories.", st["sub"]), Spacer(0, 2 * mm)]
    perf = ("PAGE 2", "PAGE 3", "PAGE 4")
    p8 = ("PAGE 8 – FULL 153-STEP BACKUP · reference only",
          [(70, "BACKUP SHOW|%d steps" % cue_range(70))] + [(None, "")] * 9)
    for title, cells in pages + [p8]:
        if title is p8[0]:
            story.append(PageBreak())
        pn = int(re.search(r"PAGE (\d)", title).group(1))
        row = []
        for k, (mid, text) in enumerate(cells):
            main, _, sub = text.partition("|")
            if mid is not None and pn in (2, 3, 4) and mid not in (18, 19):
                sub = sub or "%d cues" % cue_range(mid)
            if mid is None:
                row.append([P("P%d · M%d" % (pn, k + 1), small)])
            else:
                row.append([P("P%d · M%d" % (pn, k + 1), small), P(esc(main), cst)] + ([P(esc(sub), small)] if sub else []))
        t = Table([row], colWidths=[27.7 * mm] * 10, rowHeights=[16 * mm])
        cmds = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a0")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1)]
        if title.startswith(perf):
            cmds.append(("BOX", (0, 0), (-1, -1), 1.6, HEAD))
        if pn == 2:
            cmds.append(("BACKGROUND", (9, 0), (9, 0), colors.HexColor("#d9f2d9")))
        if pn == 5:
            cmds.append(("BACKGROUND", (4, 0), (4, 0), TINT))
        t.setStyle(TableStyle(cmds))
        story.append(KeepTogether([P("<b>%s</b>" % esc(title), st["m"]), t, Spacer(0, 2.2 * mm)]))

    # reminder strips, page tabs, wing blanks, spares (same page as the P8 row)
    story += [Spacer(0, 2 * mm), P("Desk reminder strips, page tabs and spares", st["title"]),
              P("Stick a strip along the top of the Mantra, above the screen or playbacks.", st["sub"]), Spacer(0, 3 * mm)]
    rem1 = ("<b>QLab fires every cue · this desk is the backup</b> &nbsp;·&nbsp; <b>SAFE LIGHT = P2 · M10</b> &nbsp;·&nbsp; "
            "P2 Act One · P3 Act Two · P4 songs · P5 FX &nbsp;·&nbsp; flash returns are automatic from QLab")
    rem2 = ("If QLab fails: pick the scene memory on P2/P3 (song → P4) › Next Cue &nbsp;·&nbsp; press Next Cue again after each flash "
            "&nbsp;·&nbsp; Q57 HAYWIRE = P5 M5 on, off at Q57b &nbsp;·&nbsp; O = All Cues Off · A L = Clear All · T S = Save")
    for txt in (rem1, rem2, rem1, rem2):
        t = Table([[P(txt, st["note"])]], colWidths=[277 * mm], rowHeights=[11 * mm])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, HEAD), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f6f9"))]))
        story += [t, Spacer(0, 2.5 * mm)]
    story += [Spacer(0, 2 * mm), P("<b>PAGE TABS – stick beside the Page button</b>", st["m"])]
    tabs = ["P1 VENUE", "P2 ACT ONE", "P3 ACT TWO", "P4 SONGS", "P5 FX / CHASE", "P6 LOOKS M01–M10",
            "P7 LOOKS M11–M17", "P8 BACKUP 153", "P9–10 FREE"]
    t = Table([[P(esc(x), cst) for x in tabs]], colWidths=[30.7 * mm] * 9, rowHeights=[11 * mm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a0")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story += [t, Spacer(0, 4 * mm)]
    for w in ("WING 1 PLAYBACKS – write-in (unused in this show)", "WING 2 PLAYBACKS – write-in (unused in this show)",
              "SPARE BLANK LABELS – write in by hand"):
        cells = [[P("M%d" % (i + 1), small)] if "WING" in w else "" for i in range(10)]
        t = Table([cells], colWidths=[27.7 * mm] * 10, rowHeights=[14 * mm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a0")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story += [P("<b>%s</b>" % w, st["m"]), t, Spacer(0, 3 * mm)]
    doc.build(story)
    return path


def main():
    groups = [parse_group(g) for g in load_qlab()]
    mems = load_mtr()
    _, by_pmc = load_map()
    # sanity: every performance Mantra target exists in the section map
    missing = [(g["num"], x["p"], x["m"], x["c"]) for g in groups for x in g["mantra"]
               if x["p"] in (2, 3, 4) and (x["p"], x["m"], x["c"]) not in by_pmc and not (x["p"] == 2 and x["m"] == 10)]
    if missing:
        sys.exit("Mantra targets missing from section map: %s" % missing)
    os.makedirs(OUT, exist_ok=True)
    print(build_cue_sheets(groups, by_pmc, mems))
    print(build_labels(mems))


if __name__ == "__main__":
    main()
