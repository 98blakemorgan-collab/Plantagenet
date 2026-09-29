"""Part I — Projection Backgrounds."""
import glob
import os

from core import *  # noqa: F401,F403
import show as S_
import make_printouts as mp

THUMBS = os.path.join(os.path.dirname(S_.SHOW), "..", "production", "assets", "thumbs")
THUMBS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                       "production", "assets", "thumbs"))

BACKDROPS = {  # id: (title, image prompt, motion prompt or None, note)
    "BG-01": ("House / preshow",
              "A deep blue ocean seen from below, soft beams of sunlight falling through the water from a rippling "
              "surface, tiny drifting bubbles and particles, dark vignette at the edges, calm and inviting.",
              "Light beams slowly sway, particles drift upward, surface ripples shimmer.",
              "Runs low (about 40 % opacity) under house light."),
    "BG-02": ("Beneath the Waves — the coral",
              "A magical underwater coral kingdom, colourful coral reefs and swaying sea grass framing the left and "
              "right edges, a distant glowing shell-shaped palace far in the background, shafts of turquoise light, "
              "open calm water in the centre.",
              "Sea grass sways, small silhouetted fish schools cross the far background, light caustics ripple.",
              "Main underwater look. Loop A for the Prologue and Q36.5, loop B for the Scene Five bar."),
    "BG-03": ("Coral Conservatoire (singing lesson)",
              "An underwater music room built from coral and shells, a large scallop-shell stage and seaweed curtains "
              "at the sides, pearl music stands and bubbles shaped like musical notes, warm golden light.", None,
              "Still. Seen only if the tabs are open for Scene Two."),
    "BG-04": ("Octavia's storm spell",
              "Dark churning underwater currents swirling in a spiral, deep purple and sickly green light, a sense of "
              "gathering magic.", "The whirlpool slowly turns and tightens, purple light pulses gently.",
              "Plays under 'the lighting churns' (Q16.5); out on the Q17 blackout."),
    "BG-05": ("Ship — calm sea",
              "A blue sunny day on a gentle ocean, soft white clouds, distant horizon.", "Gentle swell, clouds drift, sun glints move on the water.",
              "Keep the rocking tiny — strong motion on a big screen makes audiences queasy."),
    "BG-06": ("Weather report — 'sunny'",
              "An absurdly perfect sunny sky, a big bright sun, perfect blue sky, fluffy clouds, over a calm sea.",
              None, "Comic snap for the weather gag (Q19)."),
    "BG-07": ("The storm",
              "A violent storm at sea, towering dark waves, driving rain, low black clouds lit from inside, deep "
              "blue and steel grey.", "Rain falls, waves heave, clouds churn. No lightning.",
              "Lightning comes from the Mantra (Q21, Q23, Q25) — never flashes in the video (R-04)."),
    "BG-08": ("The shore",
              "A quiet sandy cove at sunrise just after a storm, soft peach and pale gold sky, small waves, "
              "driftwood and a coil of rope at the edges, rocks framing the sides.",
              "Small waves wash in and out, clouds drift, light slowly warms.",
              "Scene Four is played in front of the tabs: seen only if the tabs are open or a gauze is used."),
    "BG-09": ("Transformation magic",
              "Swirling magical energy, violet and cyan glowing particles spiralling around an empty centre, "
              "sparkles and soft light trails, dark background.",
              "Particles spiral slowly upward and inward. Gentle, not flashing.",
              "Runs under the transformation (Q33) and the voice transfer (Q52). The white hits come from lighting."),
    "BG-10": ("Royal palace — great hall",
              "The grand hall of a seaside palace, tall arched windows over the sea, marble columns, red and gold "
              "drapes, warm afternoon sun.", "Curtains stir, sunlight shifts, sea sparkles.",
              "Spare — BG-18 is used for the palace."),
    "BG-11": ("Jellyfish search",
              "A playful bright underwater scene, coral and kelp framing the edges, soft pink and cyan jellyfish "
              "drifting far in the background, bubbles, cheerful light.",
              "Distant jellyfish pulse and drift upward, bubbles rise, kelp sways.",
              "The real jellyfish is a performer — the video ones stay small and distant."),
    "BG-12": ("Octavia's lair (first version)",
              "A dark sea-witch's cave, jagged rock arches, eerie green glow from cracks, deep purple shadows.",
              "Green glow pulses slowly, dark particles drift.", "Spare — BG-19 is used for the lair."),
    "BG-13": ("Back on dry land — palace terrace",
              "A sunny palace terrace above the sea, stone balustrade, potted flowers, bright blue sea and sky.",
              None, "Still. Comic armbands scene (Q59)."),
    "BG-14": ("The wedding (indoor hall)",
              "The seaside great hall dressed for a royal wedding, white and gold flowers, a flower arch, "
              "candlelight.", "Candles flicker, petals drift down.", "Spare — the script sets the wedding outdoors (BG-20)."),
    "BG-15": ("Finale — fireworks",
              "A celebratory night sky over the sea and a distant palace, soft fireworks, reflections on the water.",
              "Fireworks bloom and fade slowly. No rapid flashes.", "Spare — swap with BG-26 if the director prefers fireworks."),
    "BG-16": ("Interval card",
              "A calm underwater scene with empty space in the upper centre for a title, soft blue light, coral "
              "silhouettes along the bottom.", None, "Still. Add the interval text in QLab, not in the image."),
    "BG-17": ("Busy coral reef",
              "A lively coral reef bustling with small tropical fish, starfish and anemones along the edges and "
              "upper background, turquoise water, sunbeams, open water in the lower centre.",
              "Schools of small fish swim slowly across the upper background, sea grass sways.",
              "Scene One (script p 8). Fish stay small and high so they don't compete with dancers."),
    "BG-18": ("Grand ballroom",
              "A grand royal ballroom by the sea, crystal chandeliers, red drapes and tall arched windows with the "
              "ocean beyond, red carpet, warm evening light.",
              "Chandelier crystals glint, curtains stir, the sea sparkles.", "Scene Six (script p 34)."),
    "BG-19": ("Dingy cave with jars and bones",
              "A dark sea-witch's cave, shelves of glowing potion jars, fish skeletons on the floor, eerie green and "
              "purple glow, a faint pool of light in the centre.",
              "Potions glow and pulse slowly, murky particles drift, green mist creeps.",
              "Scene Eight (script p 43). The shell is lit by SP4 — no bright glow in the video centre."),
    "BG-20": ("Palace gardens wedding (outdoors)",
              "The sunny outdoor terrace of a seaside palace dressed for a wedding, a white flower arch, rose "
              "garlands, the blue sea beyond, soft golden light.",
              "Petals drift down slowly, garlands flutter, the sea sparkles.", "Scene Ten (script p 51)."),
    "BG-21": ("After the storm — clearing sky",
              "Storm clouds breaking apart to a calm blue sky and a rainbow, the sea settling.",
              "Clouds drift apart, sunlight widens, the rainbow brightens slowly.",
              "Q27 — 'the cyclorama reverts to calm seas' (script p 22)."),
    "BG-22": ("Rock Lobster beach party",
              "A retro beach party under the sea: the reef strung with glowing lanterns in hot pink, orange, lime and "
              "turquoise, surfboards in the sand, bubbles like confetti.",
              "Lanterns bob, lights glow and dim softly in sequence (no flashing), bubbles float up.",
              "S1 Rock Lobster (Q8); crossfades to BG-17 at Q9."),
    "BG-23": ("Ballroom rave",
              "The grand ballroom at night turned into a party: mirror-ball glow, soft beams of cyan, magenta and "
              "orange light through haze, sparkles on the floor.",
              "Beams sweep slowly, mirror-ball specks drift. No strobing.",
              "S6 Crab Rave (Q40). Beam colours match the S6 lighting."),
    "BG-24": ("Potion storm",
              "Inside the sea-witch's cave, a swirling vortex of green and purple potion smoke rising from a "
              "cauldron, glowing jars on the shelves.", "Smoke swirls slowly upward, glow brightens and fades.",
              "Spare — optional for the S8 build and climax (not in the workspace)."),
    "BG-25": ("Celebration — confetti and rainbow",
              "The palace gardens in full celebration, rainbow ribbons, confetti drifting, soft rainbow light, the "
              "sea glowing gold.", "Confetti falls slowly, ribbons wave, rainbow light shimmers.",
              "S9 Absolutely Everybody (Q63)."),
    "BG-26": ("Tall ship at sunset",
              "A proud tall ship in silhouette on a glowing sea at sunset, orange and purple sky, a lighthouse on a "
              "distant headland.", "The ship rides the swell, clouds move slowly. No fast cuts.",
              "S10 He's a Pirate — the bows play-out (Q64)."),
}

STYLE = ("Painted storybook theatre backdrop, soft gouache and watercolour illustration, gentle brush texture, "
         "rich but slightly muted colours, wide 16:9 composition, no people, no characters, no text.")
NEGATIVE = ("people, mermaids, faces, animals in focus, characters, cartoon mascots, Disney style, text, letters, "
            "logos, watermark, signature, frame, border, harsh white highlights, busy detail in the lower centre")
LOOP = "Locked-off camera, no cuts, very slow gentle motion, seamless loop, calm enough to sit behind dialogue."


def thumb(bg):
    f = glob.glob(os.path.join(THUMBS, bg + "_*.jpg"))
    return f[0] if f else None


def cue_plan():
    """[(cue, action, file or None)] from the workspace, in show order."""
    plan = []
    for g in mp.load_qlab():
        n = g.get("number", "")
        if not n or n.startswith("E"):
            continue
        kids = [c["name"] for c in g.get("cues") or []]
        new = [k.split(" ", 1)[1] for k in kids if k.startswith("VIDEO ")]
        out = [k for k in kids if k.startswith("FADE OUT VIDEO")]
        if new:
            plan.append((n, "in", new[0]))
        elif out:
            plan.append((n, "black", None))
    return plan


def build(path):
    d = PartDoc(path, "I", "Projection Backgrounds",
                "The 26 backdrops, the projection cue plan as wired into the workspace, the matching "
                "lighting for each picture, and the prompts behind them.")
    plan = cue_plan()
    used = sorted({os.path.basename(f).split("_")[0] for _, a, f in plan if f})
    d.add(title_block("PART I · %s · %s" % (REV, DATE), "Projection Backgrounds",
                      "The backdrops, matched to the cyclorama calls in the April 2026 script and wired into "
                      "TLM_Show_R13_1.qlab5."))
    d.add(stats([(str(len(used)), "backdrops in the cue plan"), ("26", "backdrop designs BG-01…BG-26"),
                 (str(len([p for p in plan if p[1] == "in"])), "picture changes"),
                 (str(len([p for p in plan if p[1] == "black"])), "fades to black"),
                 ("15–16 s", "seamless loops, 1920×1080 HEVC")]))
    d.add(box("rule", "HOW THE BACKDROPS PLAY",
              ["26 backdrops (BG-01 to BG-26), matched to the script's cyclorama calls; every loop is a seamless "
               "15–16 s HEVC file. BG-21 clears from the storm to calm seas.",
               "They play from the workspace itself: every picture change is a Video cue plus a 2-second "
               "fade in/out inside the numbered cue group, so the picture always changes with the light and "
               "sound on the same GO. The files live in `media/video` and `media/stills` inside "
               "TLM_R13_REBUILT_Show_Files and are found by relative path."]))

    d.add(H1("1 Projection cue plan"))
    d.add(P("What is on the screen from cue to cue, read from the workspace. Each change is a 2 s crossfade; "
            "**black** fades the picture out and leaves the screen black (use the projector's AV-mute too). "
            "Loops run on infinite loop. The swatch shows the lighting QLab fires on the same GO."))
    rows = []
    for n, action, f in plan:
        c = S_.CUE.get(n)
        light = ""
        strip = ""
        if c and c["lx"]:
            x = c["lx"][0]
            _, summ, _ = S_.position_summary(x["p"], x["m"], x["c"])
            strip = swatch_strip(summ, cell=4.2 * mm, h=4 * mm)
            light = "P%d M%d · %s" % (x["p"], x["m"], c["look"])
        if action == "in":
            bg = os.path.basename(f).split("_")[0]
            t = thumb(bg)
            img = picture(t, 34 * mm) if t else ""
            kind = "still" if f.startswith("stills") else "loop"
            rows.append(["**Q%s**" % n, img, "**%s** %s\n" % (bg, BACKDROPS.get(bg, ("", ))[0]) +
                         "`%s` (%s)" % (os.path.basename(f), kind), (c["name"] if c else ""), strip, light])
        else:
            rows.append(["**Q%s**" % n, "", "**Fade to black** (VID-99 / AV-mute)", (c["name"] if c else ""),
                         strip, light])
    d.add(table(["Cue", "Picture", "Media", "Moment", "Light", "Mantra look"], rows,
                [12 * mm, 36 * mm, 46 * mm, 30 * mm, 26 * mm, 20 * mm]))
    d.add(box("rule", "PROJECTION RULES",
              ["No flashing is in any video: lightning and magic hits come from the Mantra (R-04). BG-09 runs "
               "under both the transformation (Q33) and the voice transfer (Q52).",
               "The backlight and PixBars run hard. Keep them tilted downstage so the screen only sees the "
               "projector (R-25), and check washout with BG-02, BG-18 and BG-20 running.",
               "Emergency: QLab **E2 VID-99 BLACK** puts a black frame on the stage; the projector's AV-mute is "
               "the backup. If a video file fails, the matching still in `media/stills` is the fallback."]))

    d.add(H1("2 Backdrop gallery"))
    d.add(P("All 26 designs. Stills are the 1920×1080 frames; the loops move gently from them."))
    cells, row = [], []
    for bg in sorted(BACKDROPS):
        t = thumb(bg)
        at = [("Q" + n) for n, a, f in plan if f and os.path.basename(f).startswith(bg + "_")]
        label = "**%s** %s<br/>%s" % (bg, BACKDROPS[bg][0], ("Used at " + ", ".join(at)) if at else "spare / fallback")
        row.append([picture(t, 52 * mm) if t else "", Paragraph(md(label).replace("&lt;br/&gt;", "<br/>"),
                                                                 S["small"])])
        if len(row) == 3:
            cells.append(row)
            row = []
    if row:
        cells.append(row + [""] * (3 - len(row)))
    g = Table(cells, colWidths=[56.6 * mm] * 3)
    g.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                           ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1)]))
    d.add(g)

    d.add(H1("3 Script cyclorama calls — April 2026 script pages"))
    calls = [("p 8", "Busy coral reef with fish and sea creatures", "Q9", "BG-17 (after BG-22 for Rock Lobster at Q8)"),
             ("p 19", "Blue sunny day on a gentle ocean", "Q18", "BG-05"),
             ("p 21", "Dark and stormy with lightning", "Q20", "BG-07; lightning from the Mantra"),
             ("p 22", "Cyclorama reverts to calm seas", "Q27", "BG-21 clearing sky"),
             ("p 27", "Underwater scene", "Q31", "BG-02 loop B"),
             ("p 34", "Inside a grand ballroom", "Q39", "BG-18; BG-23 rave for Crab Rave at Q40"),
             ("p 41", "Under the sea (curtains slowly open)", "Q45–45.5", "BG-11 jellyfish"),
             ("p 43", "Dark dingy cave, fish bones and weird jars", "Q50", "BG-19; BG-09 magic at Q52"),
             ("p 51", "Outdoors at the royal palace, wedding flowers", "Q60", "BG-20; BG-25 confetti at Q63")]
    d.add(table(["Page", "Script calls for", "Cue", "Media"], [list(c) for c in calls],
                [14 * mm, 70 * mm, 20 * mm, 66 * mm]))
    d.add(P("Scenes Two, Four and Nine are played in front of the tabs: their pictures (BG-03, BG-08, BG-13) are "
            "only seen if the tabs are open or a gauze is used — decide at the tech (To Find & Confirm)."))

    d.add(H1("4 Making or remaking a backdrop"))
    d.add(steps([
        "Generate the image prompt as a 16:9 still in an AI image tool (landscape 16:9).",
        "Pick the best version; upscale to at least 1920×1080 (the Epson's native resolution — check the label).",
        "For loops: load the approved still into an image-to-video tool with the motion prompt; make 5–10 s clips.",
        "Make it loop: join clips and cross-dissolve the end into the start (or ping-pong water and particles). "
        "The show loops are 15–16 s.",
        "Export 1920×1080, 24–30 fps, no audio, H.264/HEVC. **Keep the same file name** so its cue picks it up.",
        "Copy it into `TLM_R13_REBUILT_Show_Files/media/video` (or `stills`), replacing the old file, then test on "
        "the real projector with the stage lights on."]))
    d.add(box("rule", "RULES FOR EVERY BACKGROUND",
              ["One look for the whole show: every prompt ends with the same style line. Keep the lower centre "
               "calm and darker. No people, mermaids or characters, and no text. No flashing or strobing. Original "
               "designs only — the script says 'not Disney'; never name a film, studio, character or artist.",
               "Rights: check the tool's terms allow public performance and note the tool and date for each file. "
               "Screen brightness is about half a laptop's — generate slightly brighter and lower-contrast."]))
    d.add(table(["Shared text", ""], [["**Style line**", STYLE], ["**Negative prompt**", NEGATIVE],
                                      ["**Loop tail**", LOOP]], [34 * mm, 136 * mm]))

    d.add(H1("5 Prompt cards"))
    for bg in sorted(BACKDROPS):
        title, img, motion, note = BACKDROPS[bg]
        t = thumb(bg)
        at = [("Q" + n) for n, a, f in plan if f and os.path.basename(f).startswith(bg + "_")]
        txt = [Paragraph(md("**%s — %s**  ·  %s" % (bg, title, ", ".join(at) if at else "spare")), S["cellb"]),
               Paragraph(md("**Image:** " + img + " " + STYLE), S["cell"])]
        if motion:
            txt.append(Paragraph(md("**Motion:** " + motion + " " + LOOP), S["cell"]))
        txt.append(Paragraph(md("**Note:** " + note), S["cell"]))
        txt.append(Paragraph(md("☐ generated  ☐ approved  ☐ 1920×1080  ☐ loop checked  ☐ in QLab"), S["muted"]))
        card = Table([[picture(t, 44 * mm) if t else "", txt]], colWidths=[47 * mm, 123 * mm])
        card.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (0, -1), 0)]))
        d.add(KeepTogether(card))
    d.add(notes_area("Director / design notes", 6))
    return d.build()
