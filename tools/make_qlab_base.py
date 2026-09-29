#!/usr/bin/env python3
"""Build BASE_SHOW_2026.qlab5: the QLab 5 base workspace for the Mantra venue base.

It matches BASE_SHOW_2026.mtr memory for memory:
  - P1 venue looks (STAGE WORK, FULL STAGE WHITE, ...): one GO each; every
    look releases the other P1 looks, so only one is ever up.
  - Rig ID I1-I4: every fixture of one type at once (C42, ZOOM, COB, PIX); I5 clears.
  - Rig test T1-T40 (P2 M1 - P5 M10, the TEST memories): one fixture per GO,
    each releasing the one before.
  - E1 STOP ALL (QLab panic), E2 ALL OFF (releases every base memory),
    E3 STAGE WORK.

Every workspace setting - the MANTRA network patch (OSC to 2.0.0.1 port 8000),
audio, video, OSC access, key map - is copied unchanged from the R13.1
workspace, and the cues are cloned from its own OSC, group, memo and script
cues, so they are written exactly the way QLab 5 writes them.

Usage: python3 tools/make_qlab_base.py
Output: package/TLM_R13_REBUILT_Show_Files/BASE_SHOW_2026.qlab5
"""
import copy
import os
import plistlib
import re
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(ROOT, "package", "TLM_R13_REBUILT_Show_Files")
TEMPLATE = os.path.join(SHOW, "TLM_Show_R13_1.qlab5")
MTR = os.path.join(SHOW, "BASE_SHOW_2026.mtr")
OUT = os.path.join(SHOW, "BASE_SHOW_2026.qlab5")
NAME = "BASE_SHOW_2026"

UID = plistlib.UID
LOOK_FADE, TEST_FADE, OFF_FADE = 2000, 0, 2000
# Rig ID sweep: last word of the TEST memory names -> label (the hazer is left to its own test cue)
ID_TYPES = [("LIGHTSKY", "C42"), ("ZOOM", "ZOOM"), ("TOURCOB", "COB"), ("PIXBAR", "PIX")]


# --------------------------------------------------------------------------
# Mantra base: memory index -> name   (index = (page - 1) * 10 + memory - 1)
# --------------------------------------------------------------------------

def mantra_memories():
    t = open(MTR, encoding="latin-1").read()
    secs = re.split(r"^\[([^\]]+)\]\s*$", t, flags=re.M)
    d = {secs[i]: secs[i + 1] for i in range(1, len(secs), 2)}
    mems = {}
    for k in d:
        m = re.fullmatch(r"Memory(\d+)-Cue0", k)
        if m:
            kv = dict(l.split("=", 1) for l in d[k].splitlines() if "=" in l)
            mems[int(m.group(1))] = kv.get("Name", "")
    return mems


def pm(index):
    return index // 10 + 1, index % 10 + 1


def osc(index, level, fade):
    p, m = pm(index)
    return "/PlayMemory/Page=%d/Memory=%d/Cue=1/Level=%d/Fade=%d" % (p, m, level, fade)


# --------------------------------------------------------------------------
# NSKeyedArchiver graph editing
# --------------------------------------------------------------------------

class Archive:
    def __init__(self, data):
        self.data = data
        self.objs = data["$objects"]

    def get(self, ref):
        return self.objs[ref.data] if isinstance(ref, UID) else ref

    def add(self, obj):
        self.objs.append(obj)
        return UID(len(self.objs) - 1)

    def classname(self, obj):
        return self.get(obj["$class"])["$classname"] if isinstance(obj, dict) and "$class" in obj else None

    def dict_items(self, obj):
        """Items of an archived NSDictionary as (key string, value ref)."""
        return [(self.get(k), v) for k, v in zip(obj["NS.keys"], obj["NS.objects"])]

    def clone(self, ref):
        """Deep-copy the object graph under ref. Class records and $null are shared."""
        memo = {}

        def cp(r):
            if not isinstance(r, UID) or r.data == 0:
                return r
            o = self.objs[r.data]
            if isinstance(o, dict) and "$classname" in o:
                return r
            if r.data in memo:
                return memo[r.data]
            new = self.add(None)
            memo[r.data] = new
            if isinstance(o, dict):
                self.objs[new.data] = {k: (cp(v) if k != "$class" else v) if not isinstance(v, list)
                                       else [cp(x) for x in v] for k, v in o.items()}
            elif isinstance(o, list):
                self.objs[new.data] = [cp(x) for x in o]
            else:
                self.objs[new.data] = copy.copy(o)
            return new
        return cp(ref)

    def compact(self):
        """Drop objects no longer reachable from the root and renumber."""
        order, index = [0], {0: 0}
        stack = [self.data["$top"]["root"].data]

        def refs(o):
            vals = o.values() if isinstance(o, dict) else (o if isinstance(o, list) else [])
            for v in vals:
                if isinstance(v, UID):
                    yield v.data
                elif isinstance(v, list):
                    yield from (x.data for x in v if isinstance(x, UID))
        seen = set()
        while stack:
            i = stack.pop()
            if i in seen:
                continue
            seen.add(i)
            if i not in index:
                index[i] = len(order)
                order.append(i)
            stack.extend(reversed(list(refs(self.objs[i]))))

        def remap(v):
            if isinstance(v, UID):
                return UID(index[v.data])
            if isinstance(v, list):
                return [remap(x) for x in v]
            return v
        new = []
        for i in order:
            o = self.objs[i]
            if isinstance(o, dict):
                o = {k: remap(v) for k, v in o.items()}
            elif isinstance(o, list):
                o = [remap(x) for x in o]
            new.append(o)
        self.data["$objects"] = self.objs = new
        self.data["$top"] = {k: remap(v) for k, v in self.data["$top"].items()}

    def dump(self):
        return plistlib.dumps(self.data, fmt=plistlib.FMT_BINARY, sort_keys=False)


def uid_for(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "tlm-base-2026/" + "/".join(parts))).upper()


class Cues:
    """Cue factory: clones the template cues of the R13.1 workspace."""

    def __init__(self, ar):
        self.ar = ar
        top = ar.get(ar.data["$top"]["root"])
        self.lists_root = top
        self.main = ar.get(ar.get(top["cues"])["NS.objects"][0])
        assert ar.get(self.main["name"]) == "Main Cue List"
        by_number = {}
        for ref in ar.get(self.main["cues"])["NS.objects"]:
            num = ar.get(ar.get(ref)["number"])
            num = num.get("NS.string") if isinstance(num, dict) else num
            by_number[num] = ref
        self.memo_tpl = by_number["66"]      # MemoCue
        self.panic_tpl = by_number["E1"]     # group: panic script
        self.group_tpl = by_number["E3"]     # group holding one MANTRA OSC cue
        e3 = ar.get(self.group_tpl)
        self.osc_tpl = ar.get(e3["cues"])["NS.objects"][0]
        assert ar.classname(ar.get(self.osc_tpl)) == "OSCCue"
        assert ar.classname(ar.get(self.memo_tpl)) == "MemoCue"
        self.count = 0

    def _set(self, cue, key, value):
        cue[key] = self.ar.add(value)

    def _notes(self, cue, text):
        notes = self.ar.get(cue["notes"])
        notes["NSString"] = self.ar.add(text)

    def _common(self, ref, number, name, notes, uid):
        cue = self.ar.get(ref)
        self._set(cue, "number", number)
        self._set(cue, "name", name)
        self._set(cue, "uniqueID", uid)
        self._notes(cue, notes)
        self.count += 1
        return cue

    def osc(self, message, name, uid):
        ref = self.ar.clone(self.osc_tpl)
        cue = self._common(ref, "", name, message, uid)
        self._set(cue, "oscString", message)
        params = self.ar.get(cue["allParameterValues"])
        for key, val in self.ar.dict_items(params):
            if key == "com.figure53.oscmessage":
                vals = self.ar.get(val)
                for k2, v2 in zip(vals["NS.keys"], range(len(vals["NS.keys"]))):
                    if self.ar.get(k2) == "custom":
                        vals["NS.objects"][v2] = self.ar.add(message)
                        break
                else:
                    raise SystemExit("OSC template has no custom message")
        return ref

    def group(self, number, name, notes, children):
        ref = self.ar.clone(self.group_tpl)
        cue = self._common(ref, number, name, notes, uid_for("group", number))
        self.ar.get(cue["cues"])["NS.objects"] = children
        return ref

    def memo(self, number, name, notes):
        ref = self.ar.clone(self.memo_tpl)
        self._common(ref, number, name, notes, uid_for("memo", number))
        return ref

    def panic(self):
        ref = self.ar.clone(self.panic_tpl)
        cue = self._common(ref, "E1", "STOP ALL (QLab panic)", "Panics every QLab cue. Does not touch the Mantra.",
                           uid_for("group", "E1"))
        for child in self.ar.get(cue["cues"])["NS.objects"]:
            self._set(self.ar.get(child), "uniqueID", uid_for("E1", "script"))
            self.count += 1
        return ref


def build():
    mems = mantra_memories()
    looks = [i for i in range(10) if mems.get(i)]
    tests = [i for i in range(10, 50) if mems.get(i)]
    assert len(tests) == 40, "expected 40 TEST memories on P2-P5, found %d" % len(tests)

    raw = plistlib.load(open(TEMPLATE, "rb"))
    outer = Archive(raw)
    top = outer.get(raw["$top"]["root"])
    ws = dict(outer.dict_items(top))
    lists = Archive(plistlib.loads(outer.get(ws["cueLists"])["NS.data"]))
    q = Cues(lists)

    def mem_osc(i, level, fade, tag):
        p, m = pm(i)
        msg = osc(i, level, fade)
        label = ("MANTRA " if level else "MANTRA RELEASE ") + msg
        return q.osc(msg, label, uid_for(tag, str(i), str(level)))

    cues = [q.memo("0", "%s - QLab base for the Mantra venue base" % NAME,
                   "Load BASE_SHOW_2026.mtr on the Mantra (Home > Tools > Import Show). "
                   "Every cue sends OSC to the MANTRA patch (2.0.0.1 port 8000, Play Memory). "
                   "P1 looks: one at a time. T1-T40: one fixture at a time. E2 ALL OFF clears the desk.")]

    cues.append(q.memo("V", "P1 VENUE LOOKS", "Each look releases the other P1 looks."))
    for i in looks:
        p, m = pm(i)
        kids = [mem_osc(i, 100, LOOK_FADE, "look")]
        kids += [mem_osc(j, 0, LOOK_FADE, "look-off-%d" % i) for j in looks if j != i]
        cues.append(q.group("V%d" % m, mems[i], "Mantra P%d M%d %s at 100 %%, other P1 looks off" % (p, m, mems[i]), kids))

    # Type sweep: every fixture of one type at once, from the TEST memories ("TEST 23 TOURCOB" -> TOURCOB)
    cues.append(q.memo("I", "RIG ID - one fixture type at a time",
                       "I1-I4 light every fixture of one type together so you can count and find them. "
                       "Each releases the other test memories. I5 clears. Then run T1-T40."))
    by_type = {}
    for i in tests:
        by_type.setdefault(mems[i].split()[-1], []).append(i)
    n = 0
    for word, label in ID_TYPES:
        group = by_type.get(word, [])
        if not group:
            continue
        n += 1
        kids = [mem_osc(i, 100, TEST_FADE, "id-%s" % word) for i in group]
        kids += [mem_osc(j, 0, TEST_FADE, "id-off-%s" % word) for j in tests if j not in group]
        cues.append(q.group("I%d" % n, "ALL %s (%d)" % (label, len(group)),
                            "Mantra %s: %d fixtures at 100 %%, other test memories off"
                            % (", ".join("P%d M%d" % pm(i) for i in group), len(group)), kids))
    cues.append(q.group("I%d" % (n + 1), "RIG ID END", "Releases every test memory.",
                        [mem_osc(j, 0, TEST_FADE, "id-end") for j in tests]))

    cues.append(q.memo("T", "RIG TEST - one fixture at a time",
                       "T1-T40 = the TEST memories on P2-P5, one per fixture in patch order. "
                       "Each releases the one before. T41 releases T40."))
    for n, i in enumerate(tests, 1):
        p, m = pm(i)
        kids = [mem_osc(i, 100, TEST_FADE, "test")]
        if n > 1:
            kids.append(mem_osc(tests[n - 2], 0, TEST_FADE, "test-off-%d" % i))
        cues.append(q.group("T%d" % n, mems[i], "Mantra P%d M%d %s" % (p, m, mems[i]), kids))
    cues.append(q.group("T%d" % (len(tests) + 1), "RIG TEST END", "Releases the last test memory.",
                        [mem_osc(tests[-1], 0, TEST_FADE, "test-end")]))

    cues.append(q.memo("E", "EMERGENCY", "E1 panic QLab · E2 all Mantra memories off · E3 stage work light."))
    cues.append(q.panic())
    cues.append(q.group("E2", "ALL OFF (Mantra)", "Releases every memory in the base show.",
                        [mem_osc(i, 0, OFF_FADE, "all-off") for i in looks + tests]))
    cues.append(q.group("E3", "STAGE WORK (Mantra P1 M1)", "Work light: P1 M1 %s at 100 %%." % mems[looks[0]],
                        [mem_osc(looks[0], 100, LOOK_FADE, "e3")]))

    main_uid = uid_for("list", "main")
    lists.get(q.main["cues"])["NS.objects"] = cues
    q.main["uniqueID"] = lists.add(main_uid)
    lists.compact()

    # outer workspace: new cue lists, name, ids, count
    def set_ws(key, value):
        for k, v in zip(top["NS.keys"], range(len(top["NS.keys"]))):
            if outer.get(k) == key:
                top["NS.objects"][v] = outer.add(value)
                return
        raise KeyError(key)
    outer.get(ws["cueLists"])["NS.data"] = lists.dump()
    set_ws("workspaceName", NAME)
    set_ws("uniqueID", uid_for("workspace"))
    set_ws("selectedCueListID", main_uid)
    set_ws("totalCues", q.count)
    outer.compact()
    with open(OUT, "wb") as f:
        f.write(outer.dump())
    return OUT, q.count


if __name__ == "__main__":
    path, n = build()
    print("%s  (%d cues)" % (os.path.relpath(path, ROOT), n))
