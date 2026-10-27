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

Next: add Creator Store models (the key now has `creator-store-product:read`), then a one-command `make_short`
that takes a story idea and produces the finished video.

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
