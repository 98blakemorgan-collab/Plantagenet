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

# Short names, one per fader: big enough to read on the desk in show light.
# (type, label). Fixture numbers are the Mantra fixture numbers.
FIXTURES = [
    ("C42", "FACE 1L"), ("C42", "FACE 1R"), ("C42", "FACE 2L"), ("C42", "FACE 2R"),
    ("C42", "FACE 3L"), ("C42", "FACE 3R"), ("C42", "ARIEL"), ("C42", "SPIRIT"),
    ("C42", "OCTAVIA"), ("C42", "SHELL"), ("C42", "DAME"), ("C42", "FLANDERS"),
    ("ZOOM", "WASH DSR"), ("ZOOM", "WASH DSC"), ("ZOOM", "WASH DSL"),
    ("ZOOM", "WASH CSR"), ("ZOOM", "WASH CSC"), ("ZOOM", "WASH CSL"),
    ("ZOOM", "THEODORE"), ("ZOOM", "MARINA"), ("ZOOM", "SIDE SR"), ("ZOOM", "SIDE SL"),
    ("COB", "BACK DSR"), ("COB", "BACK DSC"), ("COB", "BACK DSL"),
    ("COB", "BACK CSR"), ("COB", "BACK CSC"), ("COB", "BACK CSL"),
    ("COB", "MID SR"), ("COB", "SHIN SR"), ("COB", "MID SL"), ("COB", "SHIN SL"),
    ("PIX", "PIX 1"), ("PIX", "PIX 2"), ("PIX", "PIX 3"), ("PIX", "PIX 4"), ("PIX", "PIX 5"), ("PIX", "PIX 6"),
    ("COB", "BACK C"), ("HAZE", "HAZE"), ("PIN", "PIN SR"), ("PIN", "PIN SL"),
] + [("", "")] * 6

# Where each fixture hangs (fixture number -> position).
HANG = {n: pos for ns, pos in [(range(1, 9), "FOH"), (range(9, 19), "LX1"), ((19, 20), "LX2"), ((21,), "SR boom"),
                                ((22,), "SL boom"), (range(23, 29), "LX2"), ((29, 30), "SR boom"),
                                ((31, 32), "SL boom"), (range(33, 40), "LX2"), ((40,), "floor US"),
                                ((41,), "FOH SR"), ((42,), "FOH SL")] for n in ns}

TYPE_COL = {"C42": "#f2c14e", "ZOOM": "#5fa8d3", "COB": "#e07a5f", "PIX": "#9b72cf",
            "HAZE": "#8d99ae", "PIN": "#8d99ae", "": "#ffffff"}

GRID = colors.HexColor("#8a94a0")


def fit_label(text, width, big=15, small=9):
    """Bold centred label: one line at up to `big` pt, else two lines, shrunk to fit `width`."""
    def size_for(lines):
        w = max(pdfmetrics.stringWidth(l, "Sans-Bold", 1) for l in lines)
        return min(big, width / w)
    lines = [text]
    if " " in text and size_for(lines) < big * 0.95:
        words = text.split()
        splits = [[" ".join(words[:i]), " ".join(words[i:])] for i in range(1, len(words))]
        two = max(splits, key=size_for)
        if size_for(two) > size_for(lines):
            lines = two
    size = max(small, round(size_for(lines) * 4) / 4)
    st = ParagraphStyle("fit", fontName="Sans-Bold", fontSize=size, leading=size * 1.1, alignment=1, textColor=INK)
    return Paragraph("<br/>".join(esc(l) for l in lines), st)


def label_strip(cells, col_w, height, extra=()):
    t = Table([cells], colWidths=[col_w] * len(cells), rowHeights=[height])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.6, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 1.2), ("RIGHTPADDING", (0, 0), (-1, -1), 1.2),
                           ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]
                          + list(extra)))
    return t


KEY = ("<b>Key</b> · yellow Lightsky C42 (U2) · blue Tour Pro Zoom · orange TourCOB PAR · violet PixBar · "
       "grey hazer / pinspots. FACE 1 = DSR, 2 = DSC, 3 = DSL; L / R = lit from house left / right. "
       "Hung: 1–8 FOH · 9–18 LX1 · 19–20, 23–28, 33–39 LX2 · 21, 29–30 SR boom · 22, 31–32 SL boom · "
       "40 floor US · 41–42 FOH (pinspots only if the mirror ball is used). 43–48 spare. "
       "Confirm #38 PIX 6 and #39 BACK C exist on the rig.")


def fixture_labels(st, fixtures=None, key=KEY):
    """Fixture fader labels: 4 strips of 12 (console, wing 1, wing 2) and the key.
    fixtures = [(type, label)] for faders 1-48 (default: the show names)."""
    fixtures = fixtures or FIXTURES
    num = ParagraphStyle("num", fontName="Sans-Bold", fontSize=9, leading=10.5, alignment=1, textColor=INK)
    fx_w = 23.08 * mm
    story = []
    story += [P("Fixture fader labels", st["title"]),
              P("Cut on the lines and stick one above each fixture fader. Number = Mantra fixture number. "
                "Colour bar = fixture type.", st["sub"]), Spacer(0, 3 * mm)]
    titles = ["CONSOLE 1–12", "CONSOLE 13–24", "WING 1  25–36", "WING 2  37–48"]
    for blk in range(4):
        cells, cmds = [], []
        for i in range(12):
            n = blk * 12 + i + 1
            typ, name = fixtures[n - 1]
            cells.append([P(str(n), num), fit_label(name, fx_w - 2.6 * mm, big=13)] if name else [P(str(n), num)])
            cmds.append(("LINEABOVE", (i, 0), (i, 0), 3.5, colors.HexColor(TYPE_COL[typ])))
        story += [P("<b>%s</b>" % titles[blk], st["m"]), label_strip(cells, fx_w, 16 * mm, cmds), Spacer(0, 3 * mm)]
    story.append(P(key, st["note"]))
    return story


TAG = ParagraphStyle("tag", fontName="Sans", fontSize=7.5, leading=9, alignment=1, textColor=INK)
PB_W = 27.7 * mm


def playback_strip(pn, pname, cells, st, heads=None, cmds=()):
    """One page of 10 playback labels. cells = (memory or None, label, note); heads = extra header text."""
    row = []
    for k, (mid, name, note) in enumerate(cells):
        head = P("P%d · M%d" % (pn, k + 1) + (" · <b>%s</b>" % esc(heads[k]) if heads and heads[k] else ""), TAG)
        row.append([head] if mid is None else
                   [head, fit_label(name, PB_W - 2.4 * mm)] + ([P(esc(note), TAG)] if note else []))
    return KeepTogether([P("<b>PAGE %d · %s</b>" % (pn, pname), st["m"]),
                         label_strip(row, PB_W, 19 * mm, list(cmds)), Spacer(0, 2.2 * mm)])


def build_labels(mems):
    st = styles(7.5)
    tag = TAG
    footer = ("%s · LSC Mantra Lite + 2 wings · %s · labels %s · %s"
              % (SHOWNAME, os.path.basename(MTR), REV, DATE))
    path = os.path.join(OUT, "TLM_R13_1_Mantra_Labels.pdf")
    doc = Doc(path, "TLM R13.1 Mantra Labels", footer, landscape(A4))
    story = []

    story += fixture_labels(st)
    story.append(PageBreak())

    # playback faders: one strip per page. (memory, label, note under the label)
    def look(i):  # "M03 UNDERWATER" -> "UNDERWATER"
        return re.sub(r"^M\d+\s+", "", mems.get(i, {}).get("name", ""))

    empty = (None, "", "")
    pages = [
        (1, "VENUE", [(0, "WORK", ""), (1, "WHITE", ""), (2, "WARM", ""), (3, "COOL", ""), (4, "BLUE", ""),
                      (5, "RED", ""), empty, empty, (8, "PIXBAR", ""), (9, "CURTAIN CALL", "")]),
        (2, "ACT ONE", [(10, "PRESHOW", "Q1–11"), (11, "LESSON", "Q12–17"), (12, "STORM", "Q18–27.5"),
                        (13, "SHORE", "Q28–30.5"), (14, "TRANSFORM", "Q31–37"), (15, "INTERVAL", "Q38"),
                        empty, empty, (18, "WORK", ""), (19, "SAFE", "")]),
        (3, "ACT TWO", [(20, "PALACE", "Q39–44"), (21, "JELLYFISH", "Q45–49"), (22, "LAIR", "Q50–58.5"),
                        (23, "DRY LAND", "Q59–59.7"), (24, "WEDDING", "Q60–63.5"), (25, "BOWS", "Q64–65")]
                       + [empty] * 4),
        (4, "SONGS", [(30 + i, s, "") for i, s in enumerate(
            ["ROCK LOBSTER", "FEELING GOOD", "YOUR WORLD", "WELLERMAN", "TIME OF MY LIFE", "CRAB RAVE",
             "JELLYFISH", "POOR SOULS", "EVERYBODY", "PIRATE"])]),
        (5, "FX", [(40, "WARM CHASE", ""), (41, "COOL CHASE", ""), (42, "PARTY CHASE", ""), (43, "HAZE", ""),
                   (44, "HAYWIRE", "Q57 on · Q57b off"), (45, "JELLY PULSE", "")] + [empty] * 4),
        (6, "LOOKS", [(50 + i, look(50 + i), "") for i in range(10)]),
        (7, "LOOKS", [(60 + i, look(60 + i), "") for i in range(7)] + [empty] * 3),
    ]
    pb_w = PB_W
    story += [P("Playback labels — one strip per page", st["title"]),
              P("QLab plays these memories. Keep the P2 strip on the desk in Act One, swap to P3 at the interval. "
                "Songs are on P4. Blank = empty memory.", st["sub"]), Spacer(0, 2 * mm)]
    for pn, pname, cells in pages + [(8, "BACKUP", [(70, "BACKUP", "reference only")] + [empty] * 9)]:
        if pn == 8:
            story.append(PageBreak())
        cmds = []
        if pn in (2, 3, 4):
            cmds.append(("BOX", (0, 0), (-1, -1), 2, HEAD))
        if pn == 2:
            cmds.append(("BACKGROUND", (9, 0), (9, 0), colors.HexColor("#d9f2d9")))
        if pn == 5:
            cmds.append(("BACKGROUND", (4, 0), (4, 0), TINT))
        heads = ["S%d" % (k + 1) for k in range(10)] if pn == 4 else None
        story.append(playback_strip(pn, pname, cells, st, heads, cmds))

    # reminder strips, page tabs, write-in blanks
    story += [Spacer(0, 2 * mm), P("Desk strips, page tabs and spares", st["title"]),
              P("Stick the strips along the top of the Mantra.", st["sub"]), Spacer(0, 3 * mm)]
    rem = ParagraphStyle("rem", fontName="Sans-Bold", fontSize=12, leading=14, textColor=INK)
    for txt in ("QLab runs the show  ·  desk = backup  ·  SAFE = P2 M10",
                "QLab down:  P2 / P3 scene (songs P4)  ›  Next Cue  ·  after a flash, Next Cue again",
                "HAYWIRE P5 M5: on Q57, off Q57b  ·  O = all off  ·  A L = clear  ·  T S = save"):
        t = Table([[P(esc(txt), rem)]], colWidths=[277 * mm], rowHeights=[11 * mm])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, HEAD), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                               ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f6f9"))]))
        story += [t, Spacer(0, 2.5 * mm)]
    story += [Spacer(0, 2 * mm), P("<b>PAGE TABS – stick beside the Page button</b>", st["m"])]
    tabs = ["P1 VENUE", "P2 ACT 1", "P3 ACT 2", "P4 SONGS", "P5 FX", "P6 LOOKS", "P7 LOOKS", "P8 BACKUP", "P9–10 FREE"]
    tab_w = 30.7 * mm
    story += [label_strip([fit_label(x, tab_w - 2.4 * mm, big=13) for x in tabs], tab_w, 11 * mm), Spacer(0, 4 * mm)]
    for w in ("WING 1 PLAYBACKS – write-in (unused in this show)", "WING 2 PLAYBACKS – write-in (unused in this show)",
              "SPARE BLANK LABELS – write in by hand"):
        cells = [[P("M%d" % (i + 1), tag)] if "WING" in w else "" for i in range(10)]
        story += [P("<b>%s</b>" % w, st["m"]), label_strip(cells, pb_w, 14 * mm, [("VALIGN", (0, 0), (-1, -1), "TOP")]),
                  Spacer(0, 3 * mm)]
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
