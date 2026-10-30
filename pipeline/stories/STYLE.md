# Shorts style guide (reference: balloon.json / balloon.py)

"I Grabbed the Balloon Nobody Can Let Go Of" is the approved example. New shorts copy its format,
pacing and fixes. Start a new story by copying `balloon.json` + `balloon.py`.

## Reference short breakdown (the user's example, 1:47, analysed frame by frame)
- **Cuts:** ~65 shots in 107 s. Median shot is 0.9 s in the first half and 1.5 s in the second. Hard cuts on every
  sentence and often mid-sentence. A few long tracking shots (up to 12 s) while someone walks.
- **Camera:** wide lens (~20–24 mm), low and close to the characters. Slow continuous dolly or push on every shot,
  with a slight handheld float. People walk *toward* the camera. Foreground props are huge in frame (shoes, flashlight,
  socks, glue bottle). Over-the-shoulder shots, and extreme close-ups of faces for emotional beats.
- **Inserts:** full-screen object close-ups as their own 0.5–1 s shots (a recurring clock motif 3:00 / 2:59 / 4:00, a heart
  monitor, shoes, a rope). They're used as rhythm beats and story clues.
- **Look:** very bright and saturated, with soft shadows and ambient occlusion. Glossy reflective water with ripple rings.
  Time of day sets the mood: deep-blue night with a bright moon glint, pink sunset, warm daylight, mint hospital.
  A white glow-out is used as a dream or transition.
- **Captions:** one word at a time, no pop animation. Ours are white bold Arial-style with a thin outline. (The reference moves captions per shot; the user prefers them fixed in one spot, so ours don't move.)
- **Faces:** classic Roblox-style. Expressive brows, worried or sad eyes, a drawn tear streak, closed eyes when asleep.
  No floating emote icons.
- **Audio:** fast narrator (~4 words/s), quiet background music under it the whole time (~15 dB below the voice), and sound effects.
- **Story:** first person. A strange rule in a town (everyone sleepwalks into the lake at 3 a.m.), with clues planted
  (clock, shoes, socks, rope). An emotional twist at the end (hospital, dad holding my hand), and the opening image repeats.

- 1080x1440 (3:4), no black bars, 30 fps, H.264 + AAC.
- Length 1:20–2:30, aim for **~2:00** every time. At our voice speeds that is ~540 words / ~55–60 lines
  (balloon: 406 words = 1:30).
- R6 blocky characters only (blocky.py). Narrator uses the user's avatar.
- Music: "Lurking Behind" by The Fly Guy Five (royalty free), quiet under the voice and ducked while anyone talks.
  Story json: `"music_file": "assets/music/fly_guy_five_lurking_behind.mp3", "music_credit": "Lurking Behind - The Fly Guy Five"`
  (the alternative is `fly_guy_five_hide_and_sneak.mp3`). Synthesized SFX (audio.py) on every action.
- The user's own sound effects live in assets/sfx/<name>.wav|mp3. They replace a synthesized effect with the same
  name, or add a new name, in every short (`ctx.sfx("poof", f)`). Current: poof (appear/disappear, time jumps, landings), pop (props and on-screen graphics appearing).
- Story type: a mix of comedy (deal / three backfiring attempts) and emotional mystery (strange rule, clues, twist).
- Free assets only. Credit any Creator Store model in `models` (written to `render/<slug>_credits.txt`).

## Script
Current target structure (from the user's reference transcript, ~570 words, dialogue-heavy):
cold open mid-chaos → "You see, the day before…" → a deal with money on the line ("That's it?" "That's it.")
→ "How hard could it be?" → attempt 1 backfires → the person paying pulls me aside → attempt 2 backfires bigger
→ "One more. If not, you get nothing." → they "help" and make it worse → reveal ("Did you pay him?") and silence
→ a sweet moment → "Thanks for the easiest $X of my life" → the cold-open gag happens again.
Drafts: pipeline/stories/ideas/.

- First-person narrator, short deadpan sentences, one absurd fact per line.
- Hook in line 1 (the impossible thing happens in the first 3 seconds).
- Escalating montage of places/attempts ("I tried everything." → rapid list).
- A "rule" reveal two-thirds in, then a callback ending that mirrors the opening
  (the dad's handshake → the daughter's handshake).
- Other voices are short, one-line interruptions, and the joke is in the reply ("Don't care. We're live.").

## Voice
- ElevenLabs Adam (pNInz6obpgDQGcFmaJgB). Narrator 1.33x, others 1.68x, "change audio pitch" on.
- The user records them: one narrator file plus one file with all other lines, in script order (`others_order`).
- To fix a single line, record just that line and add it under `voice_files.replace`
  (keep the recorded wording in `original_text`).

## Emotion (faces.py / avatar.react)
- Change the main character's expression on **every line**, and again on the punchline beat inside it.
  Side characters react too (crowds turn and react together).
- 27 faces: smile, happy, grin, smug, laugh, love, starstruck, relieved, determined, suspicious, confused,
  annoyed, blank, nervous, worried, embarrassed, shock, big_eyes, terrified, scream, sad, cry, angry, furious,
  disgusted, dizzy, sleepy.
- react() adds the extras automatically: an emote pop (! ? sweat anger steam hearts zzz stars; `emote_kind="bulb"`
  for ideas), a head squash on shock, a red flush and shake on anger, a droop on sad, a shake on laugh, tears on cry.
  Every character blinks on its own.
- **Head motion (every short from the parrot short on):** heads move whenever someone talks and whenever their
  expression changes. react() plays a head gesture for each emotion on the neck pivot (shock jerks back, laugh bobs,
  cry shakes, suspicious tilts, angry shakes, and so on). avatar.talk() is SUBTLE (user feedback: a nod on every
  word was too much): a small soft nod (2–3°) on a few stressed words, at most one every ~0.4 s, plus a slow gentle
  turn. Dialogue at full strength, narration at half. These add to the story's own head poses.
- Big emotional beats get a punch-in on the face.
- Emote pops are OFF by default (the reference has none); use `emote_kind=` only for a deliberate gag.
- Captions stay in ONE fixed spot (70% down the frame) for the whole short. The user asked for this; don't move them
  around per shot (shortkit.CAPTION_MODE = "fixed").
  Every shot floats slightly like a handheld camera. Use `S.whiteout(f)` for a dream or memory glow.

## Pacing and camera
- New shot every 1–3 s; a cut on every new sentence or beat.
- Every shot moves: eased push-in, follow, orbit or punch zoom. No static frames.
- Punch zoom or shake on a punchline/impact, then a wide shot to show the payoff.

## Rules learned from review (check these on every shot)
1. The camera must not sit inside crowds, trees or buildings. A runner runs **toward** the camera, in front of people.
2. If the line says something moves (goes up, falls down), it moves **in that shot** and the camera follows it, keeping it centred.
3. Characters in vehicles sit inside them and lean out. Never float outside them or clip into parts (blades, doors).
4. Every shot shows the subject **and** what they are reacting to: the face plus the goose, the face plus the ship throwing.
5. A zoom always lands on something: usually the face, with the right expression (angry = red skin, mad eyes, mad mouth).
6. Props the line mentions must be visible and believable: the truck is shown before the string is tied, and the held item is in the hand.
7. On-screen graphics stay small and end with their cut (LIVE = flashing red dot plus "LIVE", top-left).
8. Captions show one word at a time, yellow with a black outline, matching the recorded wording exactly.

## Workflow
1. Write the script → the user approves → the user records the voices → place them in `assets/voice/`.
2. `python3 pipeline/make_short.py pipeline/stories/<story>.json --preview` and check the frames in `work/short/preview/`.
3. Push `render/<slug>.blend`. The user opens it in Blender 4.0, checks the scene is SHORT,
   then does Render → Render Animation.

## Reference #2: the step-counter short (part_1 52 s + part_2 61 s, analysed frame by frame)
This is now the main style to copy 1:1.
- **Story shape:** a town-wide rule with a number attached ("everyone gets 1,000,000 steps for life; at 0 your legs
  turn to stone"). First-person kid narrator with a mom and a baby sister.
  1. Hook: the rule and the number in the first line.
  2. A tour of the town coping with the rule (old man on a bench with stone legs, a "NO RUNNING – EMERGENCIES ONLY"
     sign, grandmas on a zip line, the mailman on a pogo stick, kids wheelbarrowed to school).
  3. How I wasted mine (laps, dog races) → birthday reveal: 300 left, mom screams.
  4. Coping (wheelbarrow, practising handstands).
  5. Crisis: the baby's stroller rolls toward the river and everyone freezes because nobody wants to spend theirs.
  6. I spend everything; the big countdown 300 → 0; legs turn to stone; I use the skill I practised (walk on hands) and save her.
  7. Mom hugs us. "After that, the town changed": everyone does what I did. A wide town ending.
- **Signature visual:** a glowing green/teal counter on EVERY character's chest. Full-screen counter inserts at key
  moments, and big on-screen countdown numbers during the climax.
- **Cuts:** part 1 (setup) about 1.7 s per shot, a cut on every sentence. Part 2 (the climax) has longer follow-cam
  run shots (3–11 s) broken by quick reaction cuts and counter inserts. The stroller roll gets slow-motion-feeling shots.
- **Look:** a realistic-lit Brookhaven-style suburb (detailed houses, trees, cars, a park on a hill, a river,
  "STEPWELL ELEMENTARY", a 24/7 supermarket). Warm daylight, soft shadows, classic Roblox faces on R6 bodies.
- **Captions:** small white bold sans, one word, fixed in the lower middle (matches ours).
- **Audio:** the mix sits around -18 dB mean with peaks near 0 dB. The voice is up front, with a light music bed and
  SFX on actions (whoosh, stone crack, gasp, the counter ticking down).

## From "Ten Thousand Words" on (reference #2 look)
- **No dead air (user request):** voices flow with no pauses. Story json `"tight": {"max_pause": 0.1, "line_gap": 0.06}`
  shortens every pause inside a line and between lines (voice_import.py). Use it on every new short.
- **Town kit (pipeline/town.py, assets/town):** free CC0 Kenney houses, cars, road pieces and furniture, plus Poly Haven
  sky and ground textures. `town.sky(set)`, `town.place("suburban/building-type-c", loc, yaw)`, `town.street()`,
  `town.tree()`, `town.pine()`. Kenney houses face +Y, and cars and furniture face -Y at yaw 0.
  Scales: houses x24, cars x4.2, furniture x7.5.
- **Clothes:** printed shirts and pants (plaid, floral, stripes, dots, denim) via look `shirt_tex` / `pants_tex`
  (town.cloth_png makes them in the story's _images.py).
- **Chest counter:** `town.counter(av, {frame: badge png})`. A dark rounded badge with mint numbers, ticking down one per
  spoken word (with a soft "counter" tick sound). Big mint countdown numbers go over the climax as overlays.

## Reference #3: the "Karen at the supermarket" short (46 s, analysed frame by frame)
The user wants this TYPE of video (not this story): simple, clear, every shot explains what is happening.
- **Story formula:** first-person kid narrator with family (a baby sibling in the cart, a calm sassy mom).
  1. One public place (a supermarket).
  2. An entitled stranger (Karen) picks on the family's weakest member (the baby).
  3. She escalates three times: complains, rams the cart, folds their cart in half and throws the bottle.
  4. The family answers calmly and cleverly (baby: "goo goo gaga", mom: a side-eye one-liner, smug).
  5. Karen does something even bigger: screams for the manager, goes LIVE on her phone.
  6. Twist reveal: the manager bows to the family; the founder's statue is grandma/mom ("my mom owns the store").
  7. Karen is banned forever.
  8. Callback gag: a "NO KARENS" sign signed with the baby's tiny footprint.
- **Length and pace:** 46 s and about 43 cuts, so roughly 1.1 s per shot. A cut on every phrase.
- **Camera:** mostly still or a slow push at eye level. Medium shots of the speaker, with the listener's shoulder or cart in frame.
  Close-ups for each reaction. A few wides showing the store aisle and who stands where. A full-screen insert for props
  (phone LIVE screen, fish tank, the sign).
- **Acting (copy this):**
  - Characters mostly stand and gesture: point, arms crossed, hand on head, hand on hip, both arms out, shrug.
  - Talking = small head tilts and a slight body sway, not big nods.
  - Every line has a big expressive face, including Roblox meme faces (side-eye smug, chad grin, scream, crying, angry brows).
  - Walks are short and purposeful (marching in, storming out), with a stiff, bouncy Roblox walk.
  - Physical gags are quick and readable: the cart flips and groceries fly, a pink perfume cloud, cartoon stars on impact,
    a thrown bottle, falling confetti.
- **Look:** a bright pastel store. A checkered mint/cream floor, a green trim band, colourful shelves, a SALE sign, flat soft
  lighting. Characters wear layered Roblox clothing and big hair accessories.
- **Captions:** ONE word, UPPERCASE, white bold with a black outline, near the TOP of the frame (~12%).
- **Audio:** loud and clear (mean -15 dB), with the narrator on top and quick SFX on gags.
- **Built for reference #3 (karen.py is the template):**
  - `acting.py`: act(av, f, "point" | "cross" | "hips" | "head" | "facepalm" | "shrug" | "arms_out" | "arms_up" | "wave" | "phone" | "hold" | "hug" | "fists" | "stop"), chatter() for talking sway, tilt(), bounce_walk().
  - New meme faces: sideeye, chad, raspberry, meltdown.
  - Story json `"captions": {"y": 0.115, "upper": true, "size": 66, "stroke": 5}` gives UPPERCASE captions at the top.
