# Shorts style guide (reference: balloon.json / balloon.py)

"I Grabbed the Balloon Nobody Can Let Go Of" is the approved example. New shorts copy its format,
pacing and fixes. Start a new story by copying `balloon.json` + `balloon.py`.

## Format
- 1080x1440 (3:4), no black bars, 30 fps, H.264 + AAC, ~60–95 s.
- R6 blocky characters only (blocky.py). Narrator uses the user's avatar.
- No background music unless asked. Synthesized SFX (audio.py) on every action.
- Free assets only. Credit any Creator Store model in `models` (written to `render/<slug>_credits.txt`).

## Script
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
