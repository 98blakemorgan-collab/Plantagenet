#!/usr/bin/env python3
"""Build the BASE_SHOW_2026 printouts: the link map and the Mantra label sheet.

Everything is read from the base show files, so the printouts show what they
actually do:
  - BASE_SHOW_2026.qlab5   which QLab cue sends which OSC to which page/memory
  - BASE_SHOW_2026.mtr     memory names, which fixtures each memory lights, patch

Usage:  python3 tools/make_base_printouts.py            (needs reportlab)
Output: package/TLM_R13_REBUILT_Show_Files/docs/BASE_SHOW_2026_Link_Map.pdf
        package/TLM_R13_REBUILT_Show_Files/docs/BASE_SHOW_2026_Mantra_Labels.pdf
        (both also copied to production/TLM_Show_R13_1/03_Lighting_Mantra)
"""
import os
import plistlib
import re
import shutil

import make_printouts as mp
from make_printouts import P, esc, mm, colors, landscape, A4, Spacer, PageBreak, Table, TableStyle, ParagraphStyle

ROOT = mp.ROOT
QLAB = os.path.join(mp.SHOW, "BASE_SHOW_2026.qlab5")
MTR = os.path.join(mp.SHOW, "BASE_SHOW_2026.mtr")
PROD = os.path.join(ROOT, "production", "TLM_Show_R13_1", "03_Lighting_Mantra")
FOOTER = "%s · BASE_SHOW_2026.qlab5 + BASE_SHOW_2026.mtr · %s · %s" % (mp.SHOWNAME, mp.REV, mp.DATE)

# Mantra network (not stored in the QLab file; see Part C)
UNIVERSE_ROUTE = {1: "desk DMX XLR out", 2: "Art-Net / sACN → node 2.0.0.10 → FOH bar"}
SHORT = {"STAGE WORK": "WORK", "FULL STAGE WHITE": "WHITE", "WARM STAGE": "WARM", "COOL STAGE": "COOL",
         "BLUE STAGE": "BLUE", "RED STAGE": "RED", "PIXBAR WASH": "PIXBAR", "CURTAIN CALL": "CURTAIN CALL"}
OSC = re.compile(r"/PlayMemory/Page=(\d+)/Memory=(\d+)/Cue=(\d+)/Level=(\d+)/Fade=(\d+)")


# --------------------------------------------------------------------------
# Read the base files
# --------------------------------------------------------------------------

def load_mtr():
    t = open(MTR, encoding="latin-1").read()
    secs = re.split(r"^\[([^\]]+)\]\s*$", t, flags=re.M)
    d = {secs[i]: secs[i + 1] for i in range(1, len(secs), 2)}

    def kv(sec):
        return dict(l.split("=", 1) for l in d.get(sec, "").splitlines() if "=" in l)

    mems = {}
    for k in d:
        m = re.fullmatch(r"Memory(\d+)-Cue0", k)
        if m:
            c = kv(k)
            lit = {int(x.group(1)): int(v) for key, v in c.items()
                   for x in [re.fullmatch(r"Channel(\d+)_Level", key)] if x and int(v) > 0}
            mems[int(m.group(1))] = {"name": c.get("Name", ""), "lit": lit}
    patch, p = {}, kv("Patch")
    for i in range(int(p.get("NumPatchItems", 0))):
        start, end = int(p["Item%d_StartDmx" % i]), int(p["Item%d_EndDmx" % i])
        patch[int(p["Item%d_Channel" % i]) + 1] = {
            "model": p["Item%d_Model" % i], "u": start // 512 + 1, "a": start % 512 + 1, "b": end % 512 + 1}
    return mems, patch


def load_qlab():
    ws = mp._unarchive(plistlib.load(open(QLAB, "rb")))
    main = mp._unarchive(plistlib.loads(ws["cueLists"]))["cues"][0]
    net = {n["data"]["uniqueID"]: n["data"] for n in ws["settings"]["Network"]["networkPatches"]}
    cues = []
    for c in main["cues"]:
        if not c.get("cues"):
            continue  # memos
        fires, releases, patches = [], [], set()
        for k in c["cues"]:
            m = OSC.search(k.get("oscString") or "")
            if not m:
                continue
            patches.add(k.get("networkPatchID"))
            p, mem, _, level, fade = map(int, m.groups())
            (fires if level else releases).append((p, mem, level, fade))
        cues.append({"num": c["number"], "name": c["name"], "fires": fires, "releases": releases,
                     "script": any("source" in k for k in c["cues"]), "patches": patches})
    return ws["workspaceName"], net, cues


def idx(p, m):
    return (p - 1) * 10 + (m - 1)


def ranges(ns):
    ns, out = sorted(ns), []
    for n in ns:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(str(a) if a == b else "%d–%d" % (a, b) for a, b in out)


def lit_text(mem):
    lit = mem["lit"]
    if not lit:
        return "nothing (all at 0)"
    levels = sorted({round(v * 100 / 65535) for v in lit.values()})
    lv = "%d %%" % levels[0] if len(levels) == 1 else "%d–%d %%" % (levels[0], levels[-1])
    names = " " + mp.FIXTURES[next(iter(lit)) - 1][1] if len(lit) == 1 else ""
    return "#%s%s at %s" % (ranges(lit), names, lv)


def first_cue(cues):
    """Memory index -> the first QLab cue that fires it (V/T before the E emergency cues)."""
    out = {}
    for c in cues:
        for p, m, _, _ in c["fires"]:
            out.setdefault(idx(p, m), c["num"])
    return out


def fader(n):
    return "Console %d" % n if n <= 24 else ("Wing 1 · %d" % n if n <= 36 else "Wing 2 · %d" % n)


# --------------------------------------------------------------------------
# Link map
# --------------------------------------------------------------------------

def build_link_map(mems, patch, qlab):
    wsname, net, cues = qlab
    st = mp.styles(7.0)
    path = os.path.join(mp.OUT, "BASE_SHOW_2026_Link_Map.pdf")
    doc = mp.Doc(path, "BASE_SHOW_2026 Link Map", FOOTER, landscape(A4))
    story = [P("BASE_SHOW_2026 — what is linked to what, and where", st["title"]),
             P("Read from %s and BASE_SHOW_2026.mtr. Use the two together: QLab base on the Mac, base show on the "
               "Mantra. Fader number = fixture number." % os.path.basename(QLAB), st["sub"]), Spacer(0, 3 * mm)]

    # 1 the chain
    osc_patch = [n for n in net.values() if n["name"] == "MANTRA"][0]
    cs = osc_patch["clientStates"][0]
    story.append(P("1  The link, end to end", st["title"]))
    chain = [["QLab cue", "QLab network patch", "Mantra (desk)", "Memory → fixtures", "DMX out"],
             ["%s: V1–V10, T1–T41, E1–E3 (a group per GO)" % wsname,
              "%s · OSC over %s to %s port %d. Message: /PlayMemory/Page=P/Memory=M/Cue=1/Level=L/Fade=ms "
              "(L 100 = play, 0 = release)" % (osc_patch["name"], "TCP" if cs["useTcp"] else "UDP", cs["host"], cs["port"]),
              "IP 2.0.0.1 · Tools › Setup › Remote Triggers: OSC · Play Memory · port 8000 (set on the desk)",
              "Page P, memory M of BASE_SHOW_2026.mtr lights the fixtures listed in section 2",
              "U1: %s · U2: %s" % (UNIVERSE_ROUTE[1], UNIVERSE_ROUTE[2])]]
    story += [mp.make_table(chain[0], [chain[1]], [52 * mm, 70 * mm, 55 * mm, 50 * mm, 50 * mm], st), Spacer(0, 3 * mm)]

    # page map
    fired = first_cue(cues)
    rows = []
    for pg in range(1, 11):
        used = [i for i in range(idx(pg, 1), idx(pg, 10) + 1) if mems.get(i, {}).get("name")]
        if not used:
            rows.append(["P%d" % pg, "empty", "—", "—"])
            continue
        what = "Venue looks" if pg == 1 else "Rig test: one fixture per memory"
        mm_list = "M" + ranges([i % 10 + 1 for i in used])
        qc = ", ".join(fired.get(i, "not linked") for i in used)
        rows.append(["P%d" % pg, "%s · %s" % (what, mm_list), qc,
                     "labels page 2, strip P%d" % pg])
    story += [P("Mantra pages in the base show", st["h"]),
              mp.make_table(["Page", "What is on it", "QLab cues that fire it (M1 → M10)", "Label"], rows,
                            [14 * mm, 80 * mm, 130 * mm, 53 * mm], st), Spacer(0, 2 * mm)]
    extra = [i for i in sorted(mems) if i >= 100]
    story.append(P("<b>Not linked to QLab:</b> P1 M7–M8 (empty) and the area memories stored under internal IDs "
                   "%s — %s. They are not on a playback page, so no OSC message reaches them; use them from the "
                   "desk only." % (ranges(extra), ", ".join(mems[i]["name"] for i in extra)), st["note"]))
    story.append(PageBreak())

    # 2 every QLab cue
    story.append(P("2  Every QLab cue → Mantra page / memory → fixtures", st["title"]))
    rows, styles_ = [], []
    for c in cues:
        if c["script"]:
            rows.append(["<b>%s</b>" % esc(c["num"]), esc(c["name"]), "—", "—", "nothing: QLab only (panics every QLab cue)", "—"])
            styles_.append((len(rows) - 1, "crit"))
            continue
        fires = ["P%d M%d · %d %% · %.1f s" % (p, m, lv, f / 1000) for p, m, lv, f in c["fires"]]
        names = [mems[idx(p, m)]["name"] for p, m, _, _ in c["fires"]]
        lights = [lit_text(mems[idx(p, m)]) for p, m, _, _ in c["fires"]]
        rel = c["releases"]
        if rel:
            rel_txt = "P%d M%s" % (rel[0][0], ranges([m for _, m, _, _ in rel])) if len({p for p, _, _, _ in rel}) == 1 \
                else "%d memories (P%s)" % (len(rel), ranges({p for p, _, _, _ in rel}))
        else:
            rel_txt = "—"
        rows.append(["<b>%s</b>" % esc(c["num"]), esc(c["name"]), "<br/>".join(fires) or "—",
                     "<br/>".join(esc(n) for n in names) or "—", "<br/>".join(lights) or "—", rel_txt])
        if c["num"].startswith("E"):
            styles_.append((len(rows) - 1, "crit"))
    story.append(mp.make_table(["Cue", "QLab name", "Fires (page · memory · level · fade)", "Mantra memory",
                                "Lights (fixture # at level)", "Also releases"], rows,
                               [13 * mm, 45 * mm, 50 * mm, 42 * mm, 72 * mm, 55 * mm], st, styles_))
    story.append(PageBreak())

    # 3 every fixture
    story.append(P("3  Every fixture: where it is and what brings it up", st["title"]))
    looks = [c for c in cues if c["num"].startswith("V")]
    test_of = {}
    for c in cues:
        for p, m, _, _ in c["fires"]:
            lit = mems[idx(p, m)]["lit"]
            if c["num"].startswith("T") and len(lit) == 1:
                test_of[next(iter(lit))] = (c["num"], p, m)
    rows = []
    for n in range(1, 43):
        typ, label = mp.FIXTURES[n - 1]
        pt = patch.get(n)
        dmx = "U%d : %d–%d" % (pt["u"], pt["a"], pt["b"]) if pt else "not patched"
        model = pt["model"] if pt else "(optional pinspot)"
        t = test_of.get(n)
        in_looks = [c["num"] for c in looks if any(n in mems[idx(p, m)]["lit"] for p, m, _, _ in c["fires"])]
        rows.append(["<b>%d</b>" % n, "<b>%s</b>" % esc(label), esc(model), mp.HANG.get(n, ""), fader(n), dmx,
                     "P%d M%d" % (t[1], t[2]) if t else "—", t[0] if t else "—",
                     " ".join(in_looks) or "—"])
    table = mp.make_table(["#", "Label", "Desk fixture", "Hung", "Fader", "DMX universe : address",
                           "Test memory", "QLab test", "Also in venue looks"], rows,
                          [9 * mm, 24 * mm, 36 * mm, 18 * mm, 22 * mm, 34 * mm, 22 * mm, 18 * mm, 94 * mm], st)
    table.setStyle(TableStyle([("TOPPADDING", (0, 1), (-1, -1), 1.1), ("BOTTOMPADDING", (0, 1), (-1, -1), 1.1)]))
    story.append(table)
    story.append(Spacer(0, 2 * mm))
    story.append(P("Universe 1 = %s. Universe 2 = %s. Pinspots #41–42 are not in the base patch: add them as "
                   "generic dimmers at U1:37–38 only if the mirror ball is used (Part C step 5)."
                   % (UNIVERSE_ROUTE[1], UNIVERSE_ROUTE[2]), st["note"]))
    doc.build(story)
    return path


# --------------------------------------------------------------------------
# Label sheet
# --------------------------------------------------------------------------

def build_labels(mems, qlab):
    _, _, cues = qlab
    st = mp.styles(7.5)
    path = os.path.join(mp.OUT, "BASE_SHOW_2026_Mantra_Labels.pdf")
    doc = mp.Doc(path, "BASE_SHOW_2026 Mantra Labels", FOOTER, landscape(A4))
    story = mp.fixture_labels(st) + [PageBreak()]

    cue_of = first_cue(cues)
    story += [P("Playback labels — BASE_SHOW_2026", st["title"]),
              P("For the base show only (the R13.1 show has its own sheet). P1 = venue looks. P2–P5 = rig test, one "
                "fixture per memory. Header = page · memory · QLab cue.", st["sub"]), Spacer(0, 2 * mm)]
    for pg, pname in [(1, "VENUE LOOKS"), (2, "TEST 1–10"), (3, "TEST 11–20"), (4, "TEST 21–30"), (5, "TEST 31–40")]:
        cells, heads, cmds = [], [], []
        for k in range(10):
            i = idx(pg, k + 1)
            mem = mems.get(i)
            if not mem or not mem["name"]:
                cells.append((None, "", ""))
                heads.append("")
                continue
            if pg == 1:
                cells.append((i, SHORT.get(mem["name"], mem["name"]), ""))
            else:
                n = next(iter(mem["lit"]))
                typ, label = mp.FIXTURES[n - 1]
                cells.append((i, label, "fixture %d" % n))
                cmds.append(("LINEABOVE", (k, 0), (k, 0), 3.5, colors.HexColor(mp.TYPE_COL[typ])))
            heads.append(cue_of.get(i, ""))
        if pg == 1:
            cmds.append(("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#d9f2d9")))
        story.append(mp.playback_strip(pg, pname, cells, st, heads, cmds))

    story += [Spacer(0, 2 * mm), P("<b>PAGE TABS – stick beside the Page button</b>", st["m"])]
    tabs = ["P1 VENUE", "P2 TEST 1–10", "P3 TEST 11–20", "P4 TEST 21–30", "P5 TEST 31–40", "P6–10 EMPTY"]
    tab_w = 277 * mm / len(tabs)
    story += [mp.label_strip([mp.fit_label(x, tab_w - 2.4 * mm, big=13) for x in tabs], tab_w, 11 * mm),
              Spacer(0, 3 * mm)]
    rem = ParagraphStyle("rem", fontName="Sans-Bold", fontSize=12, leading=14, textColor=mp.INK)
    for txt in ("BASE SHOW  ·  desk: BASE_SHOW_2026.mtr  ·  QLab: BASE_SHOW_2026.qlab5",
                "V = venue look (one at a time)  ·  T = one fixture  ·  E2 = all off  ·  E3 = work light"):
        t = Table([[P(esc(txt), rem)]], colWidths=[277 * mm], rowHeights=[10 * mm])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, mp.HEAD), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                               ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f6f9"))]))
        story += [t, Spacer(0, 2 * mm)]
    doc.build(story)
    return path


def main():
    mems, patch = load_mtr()
    qlab = load_qlab()
    bad = [c["num"] for c in qlab[2] for p, m, _, _ in c["fires"] + c["releases"] if idx(p, m) not in mems]
    if bad:
        raise SystemExit("QLab base fires memories that are not in BASE_SHOW_2026.mtr: %s" % bad)
    os.makedirs(mp.OUT, exist_ok=True)
    for path in (build_link_map(mems, patch, qlab), build_labels(mems, qlab)):
        shutil.copy(path, os.path.join(PROD, os.path.basename(path)))
        print(os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
