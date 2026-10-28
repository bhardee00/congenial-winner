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
- **Captions:** one word at a time, yellow with a thick black outline, rounded bold font, about 5% of frame height,
  no pop animation. **Position changes per shot** (top ~15%, middle ~50% or bottom ~75%) to stay off faces.
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
- Big emotional beats get a punch-in on the face.
- Emote pops are OFF by default (the reference has none); use `emote_kind=` only for a deliberate gag.
- Captions place themselves per shot (auto: low, else top, else middle, wherever no face is on screen).
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
