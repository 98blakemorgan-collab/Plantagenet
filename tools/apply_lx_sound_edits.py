#!/usr/bin/env python3
"""Apply the R13.1 lighting and sound review edits to the show files, in place.

  Mantra  TLM_nov_2026_final.mtr
    L1  Flash hits white: Q21, Q23, Q25, Q35, Q57b and the M09 LIGHTNING look
    L2  Storm Q20-Q25b take their colours from M08 STORM (levels kept);
        Q26 becomes a low deep-blue storm tail
    L3  Preshow / house / interval / end states use the M02 HOUSE backlight colour
    L4  Shell cues Q36 and Q52-Q56: side and backlight down to M12 VOICE SHELL
        levels so the shell special is the brightest thing on stage
    Every edited cue is also edited at its position in the P8 backup list.

  QLab  TLM_nov_2026_final.qlab5
    S1  Starting levels on every audio cue (songs stay at 0 dB); the three
        absolute FADE TO cues keep the same drop from the new level
    S2  Storm layers: Q22 fades out Q20, Q26 fades out Q25 and takes Q22 down
        to -21 dB, Q27's storm fade-outs are 2.5 s
    S3  Q19's 16 s wind/rain bed is disarmed so the rain lands on Q19.2
    S4  House, preshow, end-of-act, interval and exit music loop

Runs only on the exact R13.1 files it was written for (SHA-256 checked) and
records the new hashes in BUILD_METADATA.json and ASSEMBLE_TLM_nov_2026_final.command.
"""
import hashlib
import json
import math
import os
import plistlib
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(ROOT, "package", "TLM_nov_2026_final")
MTR = os.path.join(SHOW, "TLM_nov_2026_final.mtr")
QLAB = os.path.join(SHOW, "TLM_nov_2026_final.qlab5")
META = os.path.join(SHOW, "BUILD_METADATA.json")
ASSEMBLER = os.path.join(ROOT, "package", "ASSEMBLE_TLM_nov_2026_final.command")
SECTION_MAP = os.path.join(SHOW, "TLM_nov_2026_final_MANTRA_SECTION_MAP.csv")

MTR_IN = "95cf3c690c2cef573c58e761f27eb54491f3e102684a1ab3f597a232fcae24c2"
QLAB_IN = "5dca0842f16f9c12c096e4389d939a564bca6a3d874619dd3fa97eda1bcb86ab"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ==========================================================================
# Mantra
# ==========================================================================

FOH = range(1, 7)
LX1 = range(13, 19)
SIDE = (21, 22, 29, 30, 31, 32)
BACK = (23, 24, 25, 26, 27, 28, 39)
PIX = range(33, 39)
WHITE = 0xFFFFFFFF
DEEP_BLUE = 0xFF1E3CFF          # already used in the file

# Internal memory ids (see tools/book/show.py PAGE_LAYOUT)
M02_HOUSE, M08_STORM, M09_LIGHTNING, M12_SHELL = 51, 57, 58, 61
BACKUP = 70


def pct(p):
    return round(p * 65535 / 100)


class Mtr:
    def __init__(self, path):
        text = open(path, encoding="latin-1").read()
        parts = re.split(r"^\[([^\]]+)\]\n", text, flags=re.M)
        assert parts[0] == ""
        self.names = parts[1::2]
        self.bodies = parts[2::2]
        self.index = {n: i for i, n in enumerate(self.names)}

    def cue(self, mem, k):
        return "Memory%d-Cue%d" % (mem, k)

    def get(self, sec, ch, attr):
        m = re.search(r"^Channel%d_%s=(\d+)$" % (ch, attr), self.bodies[self.index[sec]], flags=re.M)
        return int(m.group(1)) if m else None

    def set(self, sec, ch, attr, value):
        i = self.index[sec]
        body, n = re.subn(r"^(Channel%d_%s=)\d+$" % (ch, attr), r"\g<1>%d" % value, self.bodies[i], flags=re.M)
        assert n == 1, (sec, ch, attr)
        self.bodies[i] = body

    def lit(self, sec, chans):
        return [c for c in chans if (self.get(sec, c, "Level") or 0) > 0]

    def name(self, sec):
        return re.search(r"^Name=(.*)$", self.bodies[self.index[sec]], flags=re.M).group(1)

    def write(self, path):
        text = "".join("[%s]\n%s" % (n, b) for n, b in zip(self.names, self.bodies))
        # [ZZ_FileEnd] Size= is the file's own size in bytes
        for _ in range(3):
            size = len(text.encode("latin-1"))
            text = re.sub(r"(\[ZZ_FileEnd\]\nSize=)\d+", r"\g<1>%d" % size, text)
        assert len(text.encode("latin-1")) == size
        open(path, "w", encoding="latin-1", newline="").write(text)


def backup_positions():
    import csv
    out = {}
    for r in csv.DictReader(open(SECTION_MAP, newline="")):
        out[(int(r["Internal Memory ID"]), int(r["Cue In Section"]) - 1)] = int(r["Backup Position"]) - 1
    return out


def edit_mtr():
    m = Mtr(MTR)
    bpos = backup_positions()
    log = []

    def both(mem, k):
        """The performance cue and its copy in the P8 backup list."""
        secs = [m.cue(mem, k)]
        if (mem, k) in bpos:
            b = m.cue(BACKUP, bpos[(mem, k)])
            assert m.name(b).replace("BACKUP - ", "") == m.name(secs[0]), (b, m.name(b), m.name(secs[0]))
            secs.append(b)
        return secs

    look = lambda mem: m.cue(mem, 0)

    # L1 flash hits white on every colour fixture (FOH stays cool white)
    for mem, k in [(12, 4), (12, 7), (12, 10), (14, 4), (22, 8), (M09_LIGHTNING, 0)]:
        for sec in both(mem, k):
            for ch in m.lit(sec, list(LX1) + list(SIDE) + list(BACK) + list(PIX)):
                m.set(sec, ch, "Colour", WHITE)
        log.append("white flash: %s" % m.name(m.cue(mem, k)))

    # L2 storm palette from M08 STORM, levels unchanged
    storm = look(M08_STORM)
    for k in (3, 5, 6, 8, 9, 11):
        for sec in both(12, k):
            for ch in m.lit(sec, list(LX1) + list(SIDE) + list(BACK) + list(PIX)):
                assert m.get(storm, ch, "Colour") is not None, (sec, ch)
                m.set(sec, ch, "Colour", m.get(storm, ch, "Colour"))
        log.append("M08 storm colours: %s" % m.name(m.cue(12, k)))
    # Q26 low blue storm tail
    for sec in both(12, 12):
        for ch in m.lit(sec, LX1):
            m.set(sec, ch, "Colour", m.get(storm, ch, "Colour"))
        for ch in m.lit(sec, SIDE):
            m.set(sec, ch, "Colour", m.get(storm, ch, "Colour"))
            m.set(sec, ch, "Level", pct(30))
        for ch in m.lit(sec, BACK):
            m.set(sec, ch, "Colour", DEEP_BLUE)
            m.set(sec, ch, "Level", pct(45))
    log.append("low deep-blue tail: %s" % m.name(m.cue(12, 12)))

    # L3 house states in the M02 HOUSE backlight colour
    house = look(M02_HOUSE)
    for mem, k in [(10, 0), (10, 1), (10, 2), (15, 0), (25, 1)]:
        for sec in both(mem, k):
            for ch in m.lit(sec, BACK):
                m.set(sec, ch, "Colour", m.get(house, ch, "Colour"))
        log.append("M02 house backlight: %s" % m.name(m.cue(mem, k)))

    # L4 shell cues: side/back to the M12 VOICE SHELL levels
    shell = look(M12_SHELL)
    side_lv = max(m.get(shell, c, "Level") or 0 for c in SIDE)
    back_lv = max(m.get(shell, c, "Level") or 0 for c in BACK)
    assert 0 < side_lv < pct(20) and 0 < back_lv < pct(20)
    for mem, k in [(14, 6), (22, 2), (22, 3), (22, 4), (22, 5), (22, 6)]:
        for sec in both(mem, k):
            for ch in m.lit(sec, SIDE):
                m.set(sec, ch, "Level", side_lv)
            for ch in m.lit(sec, BACK):
                m.set(sec, ch, "Level", back_lv)
        log.append("shell levels (side %d%%, back %d%%): %s"
                   % (round(side_lv * 100 / 65535), round(back_lv * 100 / 65535), m.name(m.cue(mem, k))))

    return m, log


# ==========================================================================
# QLab (NSKeyedArchiver: every value is a shared reference, so edits append
# a new value object and repoint the key; nothing shared is mutated)
# ==========================================================================

U = plistlib.UID


def db(x):
    return 10 ** (x / 20)


# Starting levels in dB by media file prefix; songs (S01-S10) and Ariel's
# recorded line stay at 0 dB. Anything not listed is a sting or magic SFX (-6).
LEVELS = {
    "Q001": -6, "Q002": -6, "Q037": -6, "Q038": -6, "Q065": -6,        # house / interval music
    "Q004": -15, "Q031": -15, "Q045": -15, "Q050": -15, "Q059": -15, "Q060": -15,   # beds
    "Q041": -18, "Q043": -12, "Q039": -6, "Q058": -6,                  # underscore / music
    "Q019": -9, "Q019-1": -3, "Q019-2": -9,                            # weather gag
    "Q020": -9, "Q022": -9, "Q025": -6, "Q021": -3, "Q023": -3, "Q024": -6, "Q026": -6,  # storm
    "Q035": -3, "Q042-5": 0,
}
DEFAULT_SFX = -6


class Qlab:
    def __init__(self, path):
        self.ws = plistlib.load(open(path, "rb"))
        wo = self.ws["$objects"]
        root = wo[self.ws["$top"]["root"].data]
        rk = {wo[k.data]: v for k, v in zip(root["NS.keys"], root["NS.objects"])}
        self.blob = wo[rk["cueLists"].data]
        self.arc = plistlib.loads(self.blob["NS.data"])
        self.o = self.arc["$objects"]
        self.refs = {}
        for x in self.o:
            for v in (x.values() if isinstance(x, dict) else x if isinstance(x, list) else ()):
                for u in (v if isinstance(v, list) else [v]):
                    if isinstance(u, U):
                        self.refs[u.data] = self.refs.get(u.data, 0) + 1
        self.cues = [x for x in self.o if isinstance(x, dict) and "uniqueID" in x and "name" in x]

    def R(self, x):
        return self.o[x.data] if isinstance(x, U) else x

    def S(self, x):
        """String value (plain or NSMutableString)."""
        v = self.R(x)
        return v["NS.string"] if isinstance(v, dict) and "NS.string" in v else v

    def own(self, u):
        """Object behind u, which must not be shared."""
        assert self.refs.get(u.data) == 1, ("shared object", u)
        return self.o[u.data]

    def put(self, obj, key, value):
        self.o.append(value)
        obj[key] = U(len(self.o) - 1)

    def nsget(self, d, key):
        for k, v in zip(d["NS.keys"], d["NS.objects"]):
            if str(self.R(k)) == key:
                return v
        raise KeyError(key)

    def nsput(self, d, key, value):
        i = [str(self.R(k)) for k in d["NS.keys"]].index(key)
        self.o.append(value)
        d["NS.objects"][i] = U(len(self.o) - 1)

    def group(self, num):
        (g,) = [c for c in self.cues if self.S(c.get("number")) == num]
        return g

    def children(self, g):
        return self.own(g["cues"])["NS.objects"]

    def child(self, num, prefix):
        (u,) = [u for u in self.children(self.group(num)) if self.S(self.o[u.data]["name"]).startswith(prefix)]
        return u, self.o[u.data]

    def name(self, c):
        return self.S(c["name"])

    def file(self, c):
        ft = self.R(c.get("fileTarget"))
        return self.S(ft.get("relativePath")) if isinstance(ft, dict) and "relativePath" in ft else None

    def level_entry(self, c):
        lv = self.own(c["levels"])
        ent = self.own(lv["entries"])
        return self.own(self.nsget(ent, "0"))

    def fade_entry(self, c):
        f = self.own(c["fade"])
        ent = self.own(f["entries"])
        return self.own(self.nsget(ent, "0"))

    def notes_replace(self, c, old, new):
        n = self.own(c["notes"])
        s = self.S(n["NSString"])
        assert old in s and "NSAttributeInfo" not in n, (s, old)
        self.put(n, "NSString", s.replace(old, new))

    def save(self, path):
        self.blob["NS.data"] = plistlib.dumps(self.arc, fmt=plistlib.FMT_BINARY, sort_keys=False)
        open(path, "wb").write(plistlib.dumps(self.ws, fmt=plistlib.FMT_BINARY, sort_keys=False))


def edit_qlab():
    q = Qlab(QLAB)
    log = []

    # S1 starting levels
    set_to = {}
    for c in q.cues:
        path = q.file(c)
        if not path or not path.startswith("media/audio/"):
            continue
        base = os.path.basename(path)
        if base.startswith("S"):
            continue
        key = re.match(r"(Q\d{3}(?:-\d)?)_", base).group(1)
        lvl = LEVELS.get(key, DEFAULT_SFX)
        e = q.level_entry(c)
        assert q.R(e["initialLevel"]) == 1.0, (base, q.R(e["initialLevel"]))
        if lvl:
            q.put(e, "initialLevel", db(lvl))
        set_to[q.S(c["uniqueID"])] = lvl
        log.append("%+d dB  %s" % (lvl, base))

    # absolute FADE TO cues keep the same drop from the new starting level
    for num, prefix, drop in [("3", "FADE TO -10 dB Q2 ", -10), ("46", "FADE TO -12 dB Q45 ", -12),
                              ("51", "FADE TO -12 dB Q50 ", -12)]:
        _, c = q.child(num, prefix)
        start = set_to[q.S(c["cueTargetUniqueID"])]
        e = q.fade_entry(c)
        assert abs(q.R(e["endValue"]) - db(drop)) < 1e-6
        q.put(e, "endValue", db(start + drop))
        q.put(c, "name", q.name(c).replace("FADE TO %d dB" % drop, "FADE TO %d dB" % (start + drop)))
        log.append("Q%s: %s" % (num, q.name(c)))

    # S2 storm layers
    g27 = q.children(q.group("27"))
    u20, f20 = q.child("27", "FADE OUT Q20 ")
    u25, f25 = q.child("27", "FADE OUT Q25 ")
    u24, f24 = q.child("27", "FADE OUT Q24 ")
    for u in (u20, u25, u24):
        g27.remove(u)
    q.children(q.group("22")).append(u20)
    q.put(f20, "duration", 3.0)
    q.children(q.group("26")).extend([u25, u24])
    q.put(f25, "duration", 4.0)
    # Q24's groan is a 3.9 s one-shot, long gone by Q27: reuse its fade cue to take Q22 down at Q26
    _, s22 = q.child("22", "SFX Wind/rain + ship creaks")
    f24["cueTargetUniqueID"] = s22["uniqueID"]   # shared immutable string
    q.put(f24, "name", "FADE TO -21 dB Q22 SFX Wind/rain + ship creaks")
    q.put(f24, "stopTargetWhenDone", False)
    q.put(f24, "duration", 4.0)
    q.put(q.fade_entry(f24), "endValue", db(-21))
    for prefix in ("FADE OUT Q19 ", "FADE OUT Q22 "):
        _, c = q.child("27", prefix)
        assert q.R(c["duration"]) == 1.0
        q.put(c, "duration", 2.5)
    log += ["Q22: fade out Q20 over 3 s", "Q26: fade out Q25 over 4 s; Q22 to -21 dB over 4 s",
            "Q27: storm fade-outs 1 s -> 2.5 s"]

    # S3 Q19 bed off; notes follow
    _, s19 = q.child("19", "SFX Wind / comedy FX / rain")
    q.put(s19, "armed", False)
    q.notes_replace(q.group("19"), "Sound: Wind / comedy FX / rain cue as scripted",
                    "Sound: Weather report (wind/rain bed disarmed - gusts at 19.1, rain at 19.2)")
    q.notes_replace(q.group("19.2"), "Sound: -", "Sound: Rain burst")
    log.append("Q19: wind/rain bed disarmed; Q19/Q19.2 notes updated")

    # S4 house music loops
    for num, prefix in [("1", "SFX House music"), ("2", "SFX Preshow music"), ("37", "SFX End-act"),
                        ("38", "SFX Interval music"), ("65", "SFX Exit music")]:
        _, c = q.child(num, prefix)
        assert q.R(c["infiniteLoop"]) is False
        q.put(c, "infiniteLoop", True)
        log.append("Q%s: %s loops" % (num, prefix[4:]))

    return q, log


def main():
    assert sha(MTR) == MTR_IN, "Mantra file is not the R13.1 file these edits were written for"
    assert sha(QLAB) == QLAB_IN, "QLab workspace is not the R13.1 file these edits were written for"
    (m, lx), (q, snd) = edit_mtr(), edit_qlab()
    m.write(MTR)
    q.save(QLAB)
    meta = json.load(open(META))
    meta["sha256_before_lx_sound_edits"] = {"mantra": MTR_IN, "qlab": QLAB_IN}
    meta["sha256"] = {"mantra": sha(MTR), "qlab": sha(QLAB)}
    meta["r13_1_lx_sound_edits"] = [
        "Mantra: flash hits Q21/Q23/Q25/Q35/Q57b and look M09 LIGHTNING are white on every colour fixture",
        "Mantra: storm Q20-Q25b use the M08 STORM colours (levels unchanged); Q26 is a low deep-blue tail "
        "(back 45 %, side 30 %)",
        "Mantra: Q1/Q2/Q3/Q38/Q65 backlight in the M02 HOUSE colour",
        "Mantra: Q36 and Q52-Q56 side/backlight at the M12 VOICE SHELL levels",
        "Mantra: the same edits made at each cue's P8 backup position; [ZZ_FileEnd] Size re-checked",
        "QLab: starting levels on all 69 audio cues (songs 0 dB, beds -15/-18 dB, SFX -6 dB, thunder -3 dB, "
        "house music -6 dB); FADE TO cues at Q3/Q46/Q51 keep the same drop",
        "QLab: storm - Q22 fades out Q20 (3 s); Q26 fades out Q25 and takes Q22 to -21 dB (4 s); "
        "Q27 fade-outs 2.5 s (fade cues moved from Q27, total cue count unchanged)",
        "QLab: Q19 wind/rain bed disarmed; Q19/Q19.2 notes updated",
        "QLab: Q1/Q2/Q37/Q38/Q65 music set to loop",
    ]
    asm = open(ASSEMBLER, newline="").read()
    for var, old, new in (("QLAB_SHA", QLAB_IN, meta["sha256"]["qlab"]), ("MTR_SHA", MTR_IN, meta["sha256"]["mantra"])):
        assert asm.count('%s="%s"' % (var, old)) == 1, var
        asm = asm.replace('%s="%s"' % (var, old), '%s="%s"' % (var, new))
    open(ASSEMBLER, "w", newline="").write(asm)
    json.dump(meta, open(META, "w"), indent=2, ensure_ascii=False)
    open(META, "a").write("\n")
    print("\n".join(["MANTRA"] + lx + ["", "QLAB"] + snd))


if __name__ == "__main__":
    main()
