# Roblox Shorts Pipeline

Makes vertical (1080x1920) narrated, captioned Roblox-style animated Shorts with Blender.

**Status: work in progress.** Built so far:
- `pipeline/fetch_avatar.py` – downloads the channel avatar (user 2011327607) pieces from Roblox (Open Cloud asset delivery when `ROBLOX_API_KEY` is set)
- `pipeline/prep_avatar.py` – poses the R15 parts from their rig attachments, fetches meshes/textures, maps the shirt/pants templates → `work/avatar/rig.json`
- `pipeline/avatar.py` – Blender: builds the posable avatar from `rig.json` (joint pivots `torso`, `waist`, `head`, `la`/`ra` + elbows/wrists, `ll`/`rl` + knees/ankles, swappable faces, hand grips for props)
- `pipeline/avatar_preview.py` – Blender: front / three-quarter / posed preview renders of the avatar
- `pipeline/rbx.py` – reads Roblox binary models (.rbxm) and meshes (v1–v5)
- `pipeline/tts.py` – narration with the Kokoro voice model
- `pipeline/scene_dock_test.py` – Blender (Eevee) test scene: dock, lake, town, sunset/sky lighting, 3 camera cuts
- `pipeline/finish.py` – one-word yellow captions, freeze effect, final MP4 encode
- `pipeline/web_v1_*` – first (low-quality) three.js version, kept for reference

## Making a short
```
python3 pipeline/make_short.py pipeline/stories/pause_remote.json [--preview]
```
Narrates the story (Adam voice, 1.3x), downloads the free Creator Store models it lists (free, script-free only;
credits written to `render/<slug>_credits.txt`), draws the captions/cards, then builds every set in Blender and packs
everything into `render/<slug>.blend`. `--preview` also renders one small frame per shot into `work/short/preview/`.

Render the final 1080x1920 MP4 (with voice and captions) on any PC with Blender 4.0:
```
blender -b render/I_Found_a_Remote_That_Pauses_the_World.blend -a
```
It writes `render/I_Found_a_Remote_That_Pauses_the_World.mp4` next to the .blend.

Pipeline pieces: `shortkit.py` (sets, cameras, acting, the edit), `stories/<name>.py` (a story's sets and shots),
`characters.py` (rigged pigeon), `models.py` / `rbx_model.py` (Creator Store models), `faces.py` (expressions).

## Avatar
```
python3 pipeline/fetch_avatar.py 2011327607   # needs ROBLOX_API_KEY with asset:read + legacy-asset:manage
python3 pipeline/prep_avatar.py
blender -b -P pipeline/avatar_preview.py      # optional check
blender -b -P pipeline/scene_dock_test.py -- 32 && blender -b work/scene.blend -a
```

## Session setup
Paste `bash setup.sh` (run from this repo) into the environment's Setup script, or run it at the start of a session.
Downloaded Roblox assets go in `work/` and are not committed.
