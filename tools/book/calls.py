"""DSM calls placed on the licensed script.

Each scene: (title, pages, [(cue, standby page, standby line, GO page, GO line, depts, what happens, note)])
"""

SCENES = [
    ("PRE-SHOW", "", [
        ("1", "—", "FOH manager: house opening", "—", "House opens", "QLAB FX", "Preshow state, house music, BG-01 low", ""),
        ("2", "—", "with Q1", "—", "Audience admitted", "QLAB", "Preshow music", ""),
        ("3", "—", "Beginners called", "—", "Places", "QLAB FX", "Fade house music toward standby; HZ-01", ""),
    ]),
    ("PROLOGUE — BENEATH THE WAVES", "pp 6–7", [
        ("4", "—", "FOH clearance received", "6", "FOH clearance — house out", "QLAB FX", "House out; underwater; ocean bed; BG-02", "Q4 and Q5 are called as a pair"),
        ("5", "6", "with Q4", "6", "House out complete (visual)", "QLAB", "Magical sound; SPIRIT enters", ""),
        ("6", "6", "“Her trident holds power…”", "6", "“…wants it for her own.”", "QLAB", "Evil chord; OCTAVIA enters; audience boo", ""),
        ("7", "6", "“Now off you go, go back to your lair.”", "6", "“…the last you've heard of me!”", "QLAB", "Evil chord; OCTAVIA exits laughing", ""),
        ("8", "7", "“I wish I could say, that was just a phase,”", "7", "“…and try not to get wet!”", "QLAB", "SPIRIT exits; opening number — S1 Rock Lobster follows (BG-22)", "S1 starts straight after Q8"),
    ]),
    ("SCENE ONE — BENEATH THE WAVES", "pp 8–12", [
        ("9", "8", "“They're not great material for the ocean either!”", "8", "FLANDERS: “Touché.”", "QLAB FX", "THEODORE enters; Rock Lobster fades out; BG-17 reef", ""),
        ("10", "9", "“Many years ago, the Queen's parents…”", "9", "“…not their biggest fin.”", "QLAB", "Fanfare; QUEEN MARINA enters", ""),
        ("11", "11", "“But don't you ever wonder what it's like up there?”", "12", "“…not even trying to understand me.”", "QLAB", "ARIEL runs off, upset", ""),
        ("12", "12", "“I'll go after her, shall I?”", "12", "THEO exits — TABS CLOSE", "QLAB", "End Scene One; Scene Two in front of tabs; DAME enters", "Tabs close on this cue"),
    ]),
    ("SCENE TWO — THE SINGING LESSON", "pp 13–18", [
        ("13", "13", "“Now, I wonder if there are any singing sensations…”", "13", "“…shall we have a look at you?”", "QLAB FOH", "House lights come up", ""),
        ("14", "13", "“Oh, (NAME OF MAN), that's a lovely name!”", "14", "“…I'm going to do it anyway!”", "QLAB", "Song: Dame Beluga — S2 Feeling Good follows", "House back down"),
        ("15", "15", "“The AUDIENCE reply ‘From the Top!’”", "16", "ARIEL: “Ok, how about this one…”", "QLAB", "Song: Ariel — S3 Part of Your World follows", ""),
        ("15.5", "16", "Song ends", "16", "FLANDERS: “That was incredible.”", "LX", "Lighting shifts; Ariel looks up (ship above); song fades", ""),
        ("16", "16", "“Oh dear. I've got a bad feeling about this.”", "16", "FLANDERS exits after her", "QLAB", "Evil chord; OCTAVIA emerges", ""),
        ("16.5", "17", "“You can control the weather?”", "17", "“…this is going to be spectacular!”", "LX QLAB", "Octavia raises her arms; the lighting churns; BG-04", ""),
        ("17", "17", "“Will you stop going on about superheroes…”", "18", "“…then you will be ‘Thore!’”", "QLAB DECK", "Evil chord, lights swirl — BLACKOUT", ""),
    ]),
    ("SCENE THREE — ABOARD THE SHIP", "pp 19–23", [
        ("18", "18", "In the blackout", "19", "Deck: “Clear”", "QLAB", "Ship deck (BG-05); song — S4 Wellerman follows", ""),
        ("19", "19", "“Now, I want a weather report.”", "20", "SAILOR: “The weather will be sunny.”", "QLAB FX", "Stage brightly lit; BG-06 sunny; Wellerman fades", ""),
        ("19.1", "20", "with Q19", "20", "SAILOR: “With gusts of wind”", "QLAB", "Fart sound", ""),
        ("19.2", "20", "with Q19", "20", "SAILOR: “And periodic rain.”", "QLAB FX DECK", "Rain burst SFX; water pistols spray the audience", "Audience gets wet — R-23"),
        ("19.3", "20", "with Q19", "20", "Pistols stop (visual)", "LX", "Lights return to normal; back to BG-05", ""),
        ("20", "21", "“I don't know why father wants me to marry…”", "21", "EVAN: “Don't start that again.”", "QLAB FX", "Storm starts: wind and rain, BG-07; HZ-04", ""),
        ("21", "21", "with Q20", "21", "“…lightning flashes” (a beat after Q20)", "QLAB", "First lightning flash — returns by itself", "Call straight after Q20"),
        ("22", "21", "“What was that?”", "21", "“It's just a bit of thunder and lightning.”", "QLAB", "Thunder again, stronger; ship creaks", ""),
        ("23", "21", "“There it is again! I said the sea was too calm!”", "21", "“…shouting ‘I told you so!’”", "QLAB", "Major lightning — returns by itself", ""),
        ("24", "21", "with Q23", "21", "The ship lurches (visual)", "QLAB FX", "Ship lurches; groan + water impact", "Water spray only if approved"),
        ("25", "21", "It thunders again", "22", "WILLIS: “Nature is shouting quite loudly, sir!”", "QLAB FX", "Storm crescendos; peak flash; HZ-05", ""),
        ("26", "22", "with Q25", "22", "EVAN thrown overboard (visual)", "QLAB", "Splash; low water bed", ""),
        ("27", "22", "“It's a good job I'm wearing this lifejacket.”", "22", "“…I think the storm is stopping.”", "QLAB FX", "The storm stops; BG-21 clears; HZ-06 off", ""),
        ("27.5", "22", "“Ladder, Salt, Catfish, Storm.”", "23", "“Then it's still my royal prerogative.”", "LX QLAB DECK", "TABS CLOSE — end Scene Three", ""),
    ]),
    ("SCENE FOUR — THE SHORE", "pp 24–26", [
        ("28", "23", "Tabs in", "24", "Deck: “Clear”", "QLAB", "Magical sound; SPIRIT appears; shore (BG-08)", ""),
        ("28.5", "24", "“Ariel kept him safe from a very watery grave,”", "24", "“…next for this prince and princess.”", "LX QLAB", "Magical sound; SPIRIT disappears", ""),
        ("29", "24", "“I'll just go and…”", "24", "FLANDERS exits", "QLAB", "Evan stirs and opens his eyes", ""),
        ("30", "25", "“What's it like, down there?”", "25", "EVAN: “No one else is… but I am.”", "QLAB", "Song: Ariel & Evan — S5 Time of My Life follows", ""),
        ("30.5", "26", "“It all sounds very sus-fish-ious to me!”", "26", "Evan and Willis follow off", "LX QLAB DECK", "BLACKOUT — end Scene Four; song fades", ""),
    ]),
    ("SCENE FIVE — THE BARGAIN", "pp 27–33", [
        ("31", "26", "In the blackout", "27", "Deck: “Clear”", "QLAB", "Back underwater (BG-02 B); bar ambience", ""),
        ("32", "29", "“Ariel, you are my daughter.”", "29", "DAME: “…superb vocal timbre.”", "QLAB", "Evil chord; OCTAVIA enters with SLIP and SLAP", ""),
        ("33", "30", "“Now, do we have a deal?”", "30", "OCTAVIA presents her hand", "QLAB FX", "Transformation standby; BG-09; HZ-07", ""),
        ("34", "30", "“What do you think, should I make the deal?”", "30", "ARIEL: “Ok, I'll do it!”", "QLAB FX", "They shake; transformation builds; music swells", ""),
        ("35", "30", "with Q34", "31", "Music peaks; Ariel stands on her legs (visual)", "QLAB", "White hit, returns by itself; transformation complete", ""),
        ("36", "31", "“I knew you'd like them… and now for your voice.”", "31", "“Oh Beluga, stop your wailing!”", "QLAB", "Magical sound; light travels from Ariel to the shell", ""),
        ("36.5", "31", "“You lot wouldn't know a happy ending…”", "32", "“…evil plans don't make themselves!”", "LX QLAB", "Evil chord; Octavia exits; court enters (BG-02)", ""),
        ("36.7", "32", "“Oh, I give up.”", "32", "Theodore panics — after a moment (visual)", "LX QLAB", "Magical sound; SPIRIT enters", ""),
        ("37", "32", "“So here is the task, and there's much to be done,”", "33", "“Find Ariel quickly, she needs those who care.”", "QLAB DECK", "TABS CLOSE — END OF ACT ONE", ""),
    ]),
    ("INTERVAL", "", [
        ("38", "—", "Tabs in, stage clear", "—", "Stage clear", "QLAB FOH", "House up; interval music; BG-16", ""),
    ]),
    ("SCENE SIX — THE ROYAL PALACE", "pp 34–38", [
        ("39", "—", "Act Two beginners", "34", "FOH clearance — house out", "QLAB FX", "Royal palace; BG-18 ballroom; haze off", "Q39 and Q40 are a pair"),
        ("40", "34", "with Q39", "34", "Palace revealed (visual)", "QLAB", "Song: Evan, Willis, Ensemble — S6 Crab Rave follows (BG-23)", ""),
        ("41", "34", "Song ending", "34", "Song ends — EVAN enters, lost in thought", "QLAB", "Quiet memory beat; back to BG-18; Crab Rave fades", ""),
        ("42", "35", "“If she was, she would have told us already!”", "36", "“…we need to talk with our guests.”", "QLAB", "Evil chord; OCTAVIA enters", ""),
        ("42.5", "36", "“…let's put this voice to good use, shall we.”", "36", "Octavia holds up the shell", "LX QLAB", "Octavia sings a line in Ariel's voice", "Playback (placeholder) or offstage mic — decide"),
        ("43", "37", "“Ariel turns over the cards…”", "37", "EVAN: “Its Coral singers.”", "QLAB", "Cue-card underscore starts", ""),
        ("44", "38", "“What's with the cards? What are they all about?”", "38", "Final card: “They're about LOVE, ACTUALLY”", "QLAB DECK", "BLACKOUT — end Scene Six", ""),
    ]),
    ("SCENE SEVEN — BENEATH THE WAVES", "pp 39–41", [
        ("45", "38", "In the blackout", "39", "Deck: “Clear”", "QLAB", "DAME enters with a cue card; BG-11", "In front of tabs"),
        ("45.5", "39", "“Now let's get going, or we might be stung…”", "39", "MARINA: “Not that kind of sting.”", "LX DECK", "CURTAINS SLOWLY OPEN — jellyfish scene", ""),
        ("46", "40", "“…shall we just do a short chorus instead?”", "40", "MARINA: “Agreed. After four… Four!”", "QLAB", "Short chorus — S7 follows (song still to choose)", ""),
        ("47", "40", "“Come on, let's keep singing.”", "40", "They sing again (pp 40–41, repeats)", "QLAB", "Jellyfish sting; cyan pulse returns by itself", "Manual repeats: P5 M6"),
        ("48", "41", "“Oh dear, I think the Jellyfish had a wobble!”", "41", "DAME exits", "QLAB", "Magical sound; SPIRIT enters", ""),
        ("49", "41", "“The shell cannot hold what was never hers to take,”", "41", "“…for Ariel's sake.”", "QLAB DECK", "Spirit exits — BLACKOUT", ""),
    ]),
    ("SCENE EIGHT — OCTAVIA'S LAIR", "pp 42–46", [
        ("50", "41", "In the blackout", "42", "Deck: “Clear”", "QLAB FX", "Lair (BG-19); shell on plinth in SP4; HZ-08", "Q50 and Q51 are a pair"),
        ("51", "42", "with Q50", "42", "Lair revealed (visual)", "QLAB", "Song: Octavia and Ensemble — S8 Poor Unfortunate Souls follows", ""),
        ("52", "43", "“Can't be too hard, now let me see…”", "43", "DAME: “Aha!” (opens the shell)", "QLAB", "Shell magic; BG-09; song fades", "≤3 flashes a second (R-04)"),
        ("53", "43", "“What's going on?”", "43", "“…we're at Eve Late Night Bar.”", "QLAB", "Shell spot off; spot on DAME", ""),
        ("54", "44", "“Stop that, immediately, or I'll stop it for you!”", "44", "“Give my daughter's voice back. Now” (shakes Dame)", "QLAB", "Spot moves to FLANDERS", ""),
        ("55", "44", "“Oh no, you're not getting the voice either.”", "44", "THEO: “…Her Majesty's Most Loyal Hermit…”", "QLAB", "Spot moves to THEODORE", ""),
        ("56", "44", "“Now you've got Ariel's voice!”", "44", "“…I didn't mean to get it.”", "QLAB", "Spot moves to MARINA", "Marina gets a man's voice (offstage)"),
        ("57", "44", "“Whose voice is it?”", "45", "THEO: “Give it to me!”", "QLAB FX", "Lights go haywire (HAYWIRE chase); magic sequence; HZ-09", ""),
        ("57b", "45", "with Q57", "45", "ARIEL enters — voice restored (visual)", "QLAB", "Restore hit, HAYWIRE off, SP1 on Ariel; restore SFX", ""),
        ("58", "46", "“No, but this lot will!”", "46", "DAME: “Run!”", "QLAB FX", "Water-pistol cross-fire; chase music; everyone exits", "See R-23"),
        ("58.5", "46", "with Q58", "46", "Stage clear (visual)", "LX QLAB DECK", "TABS CLOSE — end Scene Eight", ""),
    ]),
    ("SCENE NINE — BACK ON DRY LAND", "pp 47–49", [
        ("59", "46", "Tabs in", "47", "Deck: “Clear”", "QLAB", "Evan and Willis in armbands; BG-13 terrace", ""),
        ("59.5", "48", "“I know, but it's still my royal prerogative!”", "48", "Willis exits; Evan alone", "LX QLAB", "Magical sound; SPIRIT appears", ""),
        ("59.7", "48", "“Don't worry, Dear Evan, just play your part,”", "49", "“…the voice that sings to your heart!”", "LX QLAB DECK", "Magical sound as lights dim — BLACKOUT", ""),
    ]),
    ("SCENE TEN — THE WEDDING", "pp 50–53", [
        ("60", "49", "In the blackout", "50", "Deck: “Clear”", "QLAB", "The wedding outdoors (BG-20)", ""),
        ("61", "50", "“It's probably indigestion.”", "50", "“I didn't know indigestion was contagious!”", "QLAB FX", "Evil chord; OCTAVIA enters in bridal costume; haze off", ""),
        ("61.5", "50", "“We are here to join these two in matrimony…”", "50", "“…speak now or…”", "LX QLAB", "DAME and co. burst on: “Stop the wedding!”", ""),
        ("62", "53", "“He's right. I have good reason to be fearful…”", "53", "“…reassess every now and again.”", "QLAB", "Magical sound; SPIRIT appears", "Ariel sings a line live (p 52)"),
        ("63", "53", "“So Marina and Godfrey, will you do the honours?”", "53", "“…husband and mermaid!” — everyone cheers", "QLAB", "Song: Full Cast — S9 Absolutely Everybody follows (BG-25)", ""),
        ("63.5", "53", "Song ending", "53", "End of song", "LX DECK", "TABS CLOSE — end Scene Ten; song fades", ""),
    ]),
    ("SCENE TWELVE — FINALE / BOWS", "p 54", [
        ("64", "53", "Tabs in", "54", "Tabs open / bows music", "QLAB FOH", "Bows; BG-26 tall ship — S10 He's a Pirate follows", "No Scene Eleven in the script"),
        ("65", "54", "“So all that's left to say is…”", "54", "ALL: “See you again next year!” + applause", "QLAB FOH", "End of show; exit music; house up", ""),
    ]),
]


# --------------------------------------------------------------------------
# Page numbers from the licensed script as supplied (production/script_source)
# --------------------------------------------------------------------------
import os as _os
import re as _re
import json as _json

_SCRIPT = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "production", "script_source",
                        "script_pages.txt")
SCRIPT_PAGES = {}
if _os.path.exists(_SCRIPT):
    _t = open(_SCRIPT, encoding="utf-8").read()
    _parts = _re.split(r"=== PDF PAGE (\d+) ===\n", _t)
    for _i in range(1, len(_parts), 2):
        SCRIPT_PAGES[int(_parts[_i])] = _re.sub(r"\s+", " ", _parts[_i + 1]).lower() \
            .replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("…", "...")


def _norm(s):
    return s.lower().replace("’", "'").replace("‘", "'").replace("…", " ").strip(" .!?,'\"")


def _find(line, near):
    m = _re.findall(r"“([^”]+)”", line)
    if not m or not SCRIPT_PAGES:
        return None
    words = _norm(m[0]).replace("'", "'").split()
    words = [w for w in words if w not in ("...",)]
    if len(words) < 2:
        return None  # "Clear", "Run!" — too short to place
    frag = " ".join(words[:5]) if not m[0].lstrip().startswith("…") else " ".join(words[-5:])
    hits = [n for n, tx in SCRIPT_PAGES.items() if frag in tx]
    if not hits:
        return None
    return min(hits, key=lambda n: (abs(n - near), n))


def _resolve():
    out = []
    last = None
    for title, pages, cues in SCENES:
        new = []
        for q, sp, sl, gp, gl, depts, what, note in cues:
            nsp = _find(sl, int(sp) if sp.isdigit() else (last or 1))
            ngp = _find(gl, int(gp) if gp.isdigit() else (last or 1))
            if sp.isdigit():
                sp = str(nsp or max(int(sp), last or 0))
            if gp.isdigit():
                gp = str(ngp or max(int(gp), int(sp) if sp.isdigit() else 0, last or 0))
                last = int(gp)
            new.append((q, sp, sl, gp, gl, depts, what, note))
        nums = [int(c[3]) for c in new if c[3].isdigit()] + [int(c[1]) for c in new if c[1].isdigit()]
        pages = ("pp %d–%d" % (min(nums), max(nums))) if nums and pages else pages
        out.append((title, pages, new))
    return out


# Resolved (standby page, GO page) per cue. Page numbers only, so it is safe to commit; rebuilt from the
# script render when that is present, otherwise read back so a checkout without it builds the same pages.
_FROZEN = _os.path.join(_os.path.dirname(__file__), "script_page_numbers.json")
if SCRIPT_PAGES:
    SCENES = _resolve()
    _json.dump({c[0]: [c[1], c[3]] for _t, _p, cs in SCENES for c in cs}, open(_FROZEN, "w"), indent=0)
elif _os.path.exists(_FROZEN):
    _fz = _json.load(open(_FROZEN))
    SCENES = [(t, p, [(q, _fz.get(q, [sp])[0], sl, _fz.get(q, [0, gp])[1], gl, d, w, n)
                      for q, sp, sl, gp, gl, d, w, n in cs]) for t, p, cs in SCENES]

GO_PAGE = {c[0]: c[3] for _t2, _p2, cs in SCENES for c in cs}

# Scene page ranges from the headings in the supplied script (matches Word's contents page)
SCENE_PAGES = {"PROLOGUE": "pp 6–7", "SCENE ONE": "pp 8–12", "SCENE TWO": "pp 13–18", "SCENE THREE": "pp 19–23",
               "SCENE FOUR": "pp 24–26", "SCENE FIVE": "pp 27–33", "SCENE SIX": "pp 34–39",
               "SCENE SEVEN": "pp 40–42", "SCENE EIGHT": "pp 43–47", "SCENE NINE": "pp 48–50",
               "SCENE TEN": "pp 51–54", "SCENE TWELVE": "p 55"}
SCENES = [(t, next((v for k, v in SCENE_PAGES.items() if t.startswith(k)), p), cs) for t, p, cs in SCENES]

# Casting (from the casting sheet, 28 Sep 2026): role -> (actor, songs sung, dances)
CASTING = [
    ("Ariel", "Hayley", "Part of Your World · Time of My Life", "Absolutely Everybody"),
    ("Dame Beluga", "Michelle", "Feeling Good", "Absolutely Everybody"),
    ("Flanders", "Kelly", "", "Rock Lobster · Absolutely Everybody"),
    ("Queen Marina", "Lorraine", "", "Absolutely Everybody"),
    ("Octavia", "Hannah", "Poor Unfortunate Souls", "Absolutely Everybody"),
    ("Theodore", "Emma", "", "Absolutely Everybody"),
    ("Prince Evan", "Jett", "Sea Shanty · Time of My Life", "Absolutely Everybody"),
    ("King Godfrey", "Jeff", "", "Absolutely Everybody"),
    ("Willis", "Eliott", "Sea Shanty", "Absolutely Everybody"),
    ("Slip", "Flyn", "", "Absolutely Everybody"),
    ("Slap", "Matthew", "", "Absolutely Everybody"),
    ("Spirit of the Sea 1", "Kerry", "", "Absolutely Everybody"),
    ("Spirit of the Sea 2", "Tracey", "", "Absolutely Everybody"),
    ("Jellyfish", "Helen", "", "Absolutely Everybody"),
    ("Scarlotte / Sailor 3 / Courtier / Scary Fish", "Grace", "Sea Shanty", "Rock Lobster · Crab Rave · Poor Unfortunate Souls · Absolutely Everybody"),
    ("Paulette / Sailor 1 / Courtier / Scary Fish", "Aubrey", "Sea Shanty", "Rock Lobster · Crab Rave · Poor Unfortunate Souls · Absolutely Everybody"),
    ("Charlotte / Sailor 2 / Courtier / Scary Fish", "Isobelle", "Sea Shanty", "Rock Lobster · Crab Rave · Poor Unfortunate Souls · Absolutely Everybody"),
    ("Kandy / Courtier / Scary Fish", "Shelli", "", "Rock Lobster · Crab Rave · Poor Unfortunate Souls · Absolutely Everybody"),
    ("Mermaid / Courtier / Scary Fish", "Maddie", "", "Rock Lobster · Crab Rave · Poor Unfortunate Souls · Absolutely Everybody"),
    ("Dancer", "Sarah", "", "Crab Rave · Absolutely Everybody"),
]
