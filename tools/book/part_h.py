"""Part H — Props List & Preset Sheets (R13.1: re-paged to the April 2026 script)."""
from core import *  # noqa: F401,F403

# id, prop, type, qty, scenes, script pp, used by, preset, notes
PROPS = [
    ("P01", "Child's toy (“the latest craze”)", "Hand", "1", "S1", "11", "Ariel", "SL table",
     "Current must-have kids' toy; Ariel enters with it behind her back. Pick something topical."),
    ("P02", "Queen Marina's trident", "Hand", "1", "S1, S5, S7, S10", "11, 52", "Marina", "SR table",
     "Raised on p 52 (“heir to this trident!”). Light, no sharp points; never swung near others."),
    ("P03", "Marvel comic", "Personal", "1", "S2", "16–17", "Slap", "SL table", "Real comic or printed cover. Slip and Slap's running joke."),
    ("P04", "Ladder", "Hand", "1", "S3", "19", "Sailor 1", "SR wing",
     "Short, light wooden ladder (or painted prop). Crosses in front of Godfrey and Evan; walks into Sailor 2."),
    ("P05", "Small boxes marked “SALT”", "Consumable", "3–4", "S3", "19", "Sailor 2", "SL table",
     "Empty boxes or a little paper/foam filler — no real salt (slip hazard before the storm and water). Sweep after the scene."),
    ("P06", "Fish — intact, soft (thrown)", "Hand", "1 + spare", "S3", "19", "Deck → Willis", "SL table",
     "“A fish is thrown on from the wings.” Willis catches and pockets it. Soft, light, easy to catch."),
    ("P07", "Fish — “battered”", "Personal", "1", "S3", "22", "Willis", "Willis's costume",
     "Willis pulls it out after the storm. Preset in a second pocket, or swap off-stage — decide in rehearsal."),
    ("P08", "Weather report paper", "Personal", "1", "S3", "20", "Sailor 3", "SR table", "“The weather will be sunny.”"),
    ("P09", "Willis's list of princesses", "Personal", "1", "S3", "20–21", "Willis", "SR table",
     "Scroll or clipboard: Kelly, Bella, Penelope."),
    ("P10", "Water pistols — weather gag", "Effect", "2–4", "S3", "20", "Deck / ensemble", "Both wings (bucket)",
     "Spray the audience (R-23). Clean water only, filled on call; small bursts below head height."),
    ("P11", "Godfrey's lifejacket", "Costume", "1", "S3, S5", "21–22", "Godfrey", "SR (dresser)",
     "He exits p 21 and runs back on wearing it. Quick put-on: clip or velcro front."),
    ("P12", "Large seashell (Ariel's voice)", "Hand", "1 + spare", "S5, S6, S8", "31, 36, 43–44", "Octavia → Deck → plinth",
     "SL wing shelf", "Octavia collects it from the wings on p 31, taunts Ariel with it in Scene Six (p 36), then it sits on the "
     "plinth in Scene Eight. Dame must be able to open it: hinged or a lid."),
    ("P13", "Ariel's tail-to-legs change", "Costume", "—", "S5", "30–31", "Ariel / wardrobe", "On Ariel",
     "Transformation under the Q35 white hit: tear-away tail or skirt. Rehearse with lighting."),
    ("P14", "Cue cards (set of 8, large)", "Hand", "1 set + spare", "S6, S7", "37–38, 40", "Ariel", "SR table",
     "Readable from the back row, matte finish. Ariel passes each off-stage — ASM catches them in order."),
    ("P15", "Jellyfish costume / puppet", "Costume", "1", "S7", "40–42", "Ensemble (jellyfish)", "Upstage cross-over",
     "Enters behind the cast several times. Clear path behind; performer must see out."),
    ("P16", "Plinth for the shell", "Set", "1", "S8", "43", "Deck", "Off SL (set in blackout)",
     "Stable, on the SP4 floor mark. Shell sits in its special (#10)."),
    ("P17", "Captain America shield (Frisbee)", "Personal", "1", "S8", "43", "Slip", "SL table", "Homemade look is the joke. Frisbee with painted star."),
    ("P18", "Iron Man gauntlet (washing-up glove + torch)", "Personal", "1", "S8", "43", "Slap", "SL table",
     "Torch taped to a rubber glove. Fresh batteries each show."),
    ("P19", "Slippers", "Hand", "6–8", "S8", "47", "Ensemble", "SR table",
     "“Armed with slippers.” Soft, light; thrown only if choreographed and never at the audience."),
    ("P20", "Water pistols — cross-fire", "Effect", "4–6", "S8", "47", "Ensemble", "Both wings (bucket)",
     "Catches the audience in the cross-fire (R-23). Refill at the interval; towels ready."),
    ("P21", "Inflatable armbands", "Costume", "3 pairs", "S9", "48", "Evan, Willis, Godfrey", "SR (dresser)",
     "Evan and Willis enter wearing them; Godfrey wears a pair too. Check inflation."),
    ("P22", "Rubber rings", "Hand", "3", "S9", "48", "Godfrey", "SR table",
     "One round his waist, two carried and handed to Evan and Willis. Spare pump."),
    ("P23", "Homemade superhero capes", "Costume", "2", "S10", "51", "Slip, Slap", "SL (dresser)", "Worn at the wedding — the ‘Under the Sea / Under DC’ joke."),
    ("P24", "Octavia's bridal costume", "Costume", "1", "S10", "51", "Octavia", "SL (dresser)",
     "Check the quick change from Scene Eight with wardrobe."),
    ("P25", "Guards' spears or staffs (optional)", "Hand", "2", "S10", "53", "Guards", "SR table", "For the arrest. Blunt, light; optional."),
    ("P26", "Order of service (optional)", "Hand", "1", "S10", "—", "Godfrey", "SL table",
     "Optional dressing only — not called for in the April 2026 text. Cut if not wanted."),
]

SCN = ["Prol.", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S12"]

PLOT = [
    ("Pre-show", "—", "All props preset (preset sheets). Water pistols NOT filled — fill on call only. Shell on SL shelf; plinth off SL; "
                      "cue cards in order SR."),
    ("Prologue", "6–7", "No props."),
    ("Scene One", "8–12", "Ariel collects P01 toy (SL). Marina enters with P02 trident (SR). Ariel exits with toy → back to SL table."),
    ("Scene Two", "13–18", "Slap enters with P03 comic (SL). Returns it on exit. Blackout change → ship."),
    ("Scene Three", "19–23", "P04 ladder, P05 salt boxes, P06 fish thrown from SL, P08 report, P09 list. P10 pistols from both wings "
                             "(Q19.2 rain burst). Godfrey exits p 21 — dresser puts on P11 lifejacket. After tabs: sweep, check stage dry."),
    ("Scene Four", "24–26", "No props. Deck finishes sweep upstage of tabs; preset Scene Five."),
    ("Scene Five", "27–33", "Octavia collects P12 shell from the SL shelf (p 31) and keeps it. P13 tail-to-legs change under the Q35 flash."),
    ("Interval", "—", "Interval reset (below). Refill water pistols for Scene Eight. Shell stays with Octavia's props (SL)."),
    ("Scene Six", "34–39", "Octavia enters with P12 shell (p 36) and hands it to the SL ASM on her exit. Ariel enters with P14 cue cards (p 37); "
                           "SR ASM catches each card in order and hands Card 3 to Dame."),
    ("Scene Seven", "40–42", "Dame enters with Card 3 (p 40). P15 jellyfish enters upstage (repeats with Q47). ASM sets P16 plinth + P12 "
                             "shell on the SP4 mark in the blackout into Scene Eight."),
    ("Scene Eight", "43–47", "Slip P17 shield, Slap P18 gauntlet (SL). Dame opens the shell. Ensemble P19 slippers (SR) and P20 pistols "
                             "(both wings), p 47. After tabs: strike plinth + shell, towels down, stage dry check."),
    ("Scene Nine", "48–50", "P21 armbands on Evan, Willis, Godfrey (SR dresser); Godfrey carries P22 rubber rings and hands two over."),
    ("Scene Ten", "51–54", "P23 capes, P24 bridal costume (SL dresser). Marina P02 trident (p 52). Optional P25 spears (p 53), P26."),
    ("Scene Twelve", "55", "Clear props from the stage edge for bows."),
]

CARDS = [("Card 0", "“Say its Coral Singers”", "Shown first, to Evan while Godfrey calls from off-stage (p 37)"),
         ("Card 1", "“With any luck, by next year…”", "p 37"), ("Card 2", "“I'll be going out with one of these…”", "p 38"),
         ("Card 3", "Picture of a very weird, strange-looking fish", "p 38 · goes back on with Dame in Scene Seven (p 40)"),
         ("Card 4", "“And you'll be taking out one of these…”", "p 38"), ("Card 5", "Picture of a plate of fish and chips", "p 38"),
         ("Card 6", "“But for now, let me say…”", "p 38"), ("Final", "“They're about LOVE, ACTUALLY”", "p 38 · revealed to Flanders")]


def _scenes(sc):
    out = set()
    for s in sc.replace(" ", "").split(","):
        out.add(s)
    return out


def tracking():
    rows = []
    for p in PROPS:
        used = _scenes(p[4])
        idx = [i for i, s in enumerate(SCN) if s in used]
        cells = []
        for i, s in enumerate(SCN):
            if s in used:
                cells.append("●")
            elif idx and idx[0] < i < idx[-1] and p[2] in ("Hand", "Personal", "Set") and p[0] in ("P02", "P12", "P14"):
                cells.append("–")
            else:
                cells.append("")
        rows.append(["**%s** %s" % (p[0], p[1][:34])] + cells)
    return table(["Prop"] + SCN, rows, [62 * mm] + [9 * mm] * len(SCN))


def preset(title, ids):
    rows = [[p[0], p[1], p[3], p[6], p[4]] + ["☐"] * 6 for p in PROPS if p[0] in ids]
    return [H3(title), table(["ID", "Prop", "Qty", "Used by", "Scenes", "1", "2", "3", "4", "5", "6"], rows,
                             [11 * mm, 50 * mm, 16 * mm, 29 * mm, 22 * mm] + [7 * mm] * 6)]


def build(path):
    d = PartDoc(path, "H", "Props List & Preset Sheets",
                "Every prop the script calls for, re-paged to the April 2026 script: tracking chart, preset sheets for each side, "
                "running plot, cue-card list and resets.")
    d.add(title_block("PART H · %s · %s" % (REV, DATE), "Props List & Preset Sheets",
                      "Every prop the script calls for, where it lives and who handles it"))
    d.add(stats([("26", "props and prop-costumes"), ("2", "water effects (R-23)"), ("8", "cue cards + spares"),
                 ("11", "scenes with props")]))
    d.add(box("new", "R13.1", "Re-paged to the licensed script revised April 2026 (page numbers move by one from Scene Six onwards). "
              "Every prop was checked against the new text: all are still called for except P26, which is optional dressing. "
              "The props themselves are unchanged from R8."))
    d.add(box("rule", "CONTINUITY TRAPS", "1 Card 3 (the weird fish) is passed off in Scene Six and goes back on with Dame at the top "
              "of Scene Seven (p 40). 2 The shell travels: SL shelf → Octavia (Scene Five) → Octavia (Scene Six) → plinth (Scene "
              "Eight). 3 Willis needs a second, battered fish for p 22. 4 The salt boxes spill just before the storm and the water "
              "— no real salt; sweep after the scene."))
    d.add(P("Stage right / stage left are the actor's right and left, facing the audience (stage right = audience left).", "muted"))

    d.add(H1("1 Master props list"))
    d.add(table(["ID", "Prop", "Type", "Qty", "Scenes", "Script pp", "Used by", "Preset (proposed)", "Notes / make"],
                [[p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]] for p in PROPS],
                [9 * mm, 27 * mm, 14 * mm, 10 * mm, 14 * mm, 13 * mm, 19 * mm, 19 * mm, 45 * mm], bold_first=True))

    d.add(PageBreak(), H1("2 Props tracking chart"))
    d.add(P("● in use · – stays with the performer or on stage between uses. The interval falls between S5 and S6.", "muted"))
    d.add(tracking())
    d.add(H2("Props tables, water stations and dressers"))
    d.add(table(["Where", "What"], [
        ["SR props table", "Trident · weather report · list · cue cards (in order) · slippers · rubber rings · spears · spare fish"],
        ["SR wing", "Ladder (floor)"],
        ["SL props table", "Toy · comic · salt boxes · fish (to throw) · shield · gauntlet · order of service (opt.)"],
        ["SL wing shelf ★", "Shell"], ["Off SL", "Plinth (set in the blackout into Scene Eight)"],
        ["Water stations SR + SL", "Pistols · bucket · towels — clear of the floor booms (R-24, R-26)"],
        ["Dresser SR", "Lifejacket, armbands"], ["Dresser SL", "Capes, bridal costume"]], [42 * mm, 128 * mm], bold_first=True))

    d.add(PageBreak(), H1("3 Preset sheets"))
    d.add(P("Tick each performance (1–6). Initial the bottom when the table is checked.", "muted"))
    d.add(*preset("Stage-right props table", {"P02", "P08", "P09", "P14", "P19", "P22", "P25", "P04"}))
    d.add(*preset("Stage-left props table", {"P01", "P03", "P05", "P06", "P17", "P18", "P26", "P12"}))
    d.add(*preset("Dressers, water stations, set and personal",
                  {"P11", "P21", "P23", "P24", "P10", "P20", "P16", "P07", "P15", "P13"}))
    d.add(table(["Checked by (SR)", "Checked by (SL)", "Water stations", "DSM informed"], [["", "", "", ""]],
                [42.5 * mm] * 4))

    d.add(PageBreak(), H1("4 Running props plot"))
    d.add(table(["Scene", "Script pp", "Props in / out, hand-offs and resets"], [list(r) for r in PLOT],
                [24 * mm, 18 * mm, 128 * mm], bold_first=True))

    d.add(H1("5 Cue cards, consumables and resets"))
    d.add(H3("Cue-card list (Scene Six, pp 37–38)"))
    d.add(table(["Card", "Shows", "Notes"], [list(c) for c in CARDS], [18 * mm, 72 * mm, 80 * mm], bold_first=True))
    d.add(P("About A2 or larger, black lettering on white matte board, lettering at least 10 cm high so the back row can read it. "
            "Number the backs in small print. Make a full spare set. SR ASM stacks them in order after every show."))
    d.add(H3("Consumables"))
    d.add(table(["Item", "Per show", "Stock"], [["Clean water for pistols", "~2 L", "Refill at interval"],
                                                ["Torch batteries (gauntlet)", "Check", "Fresh pack"],
                                                ["Paper/foam ‘salt’ filler", "Refill boxes", "Bag"],
                                                ["Towels (stage and front row)", "6+", "Wash nightly"],
                                                ["Gaffer and glow tape", "—", "Roll each"], ["Spare fish, spare shell", "—", "1 each"],
                                                ["Pump for rubber rings / armbands", "—", "1"]], [80 * mm, 40 * mm, 50 * mm]))
    d.add(H3("Interval reset"))
    d.add(checklist(["Salt debris and water swept/dried (Scenes Three & Five)", "Refill water pistols for Scene Eight (both wings)",
                     "Shell back on SL shelf if Octavia has put it down", "Cue cards in order on SR table", "Card 3 ready to hand to Dame",
                     "Plinth ready off SL", "Slippers, shield, gauntlet (torch works)", "Rubber rings and armbands inflated",
                     "Capes and bridal costume with SL dresser"], cols=2))
    d.add(H3("Post-show"))
    d.add(checklist(["Collect all personal props from dressing rooms", "Dry water pistols and towels; empty buckets",
                     "Re-order cue cards; check for damage", "Count: fish ×2, shell, comic, toy, trident",
                     "Log breakages and missing items in the show report (Part A)"], cols=2))
    d.add(notes_area("Props notes / repairs", 5))
    return d.build()
