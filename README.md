# Roblox Shorts Pipeline

Makes vertical (1080x1920) narrated, captioned Roblox-style animated Shorts with Blender.

**Status: work in progress.** Built so far:
- `pipeline/fetch_avatar.py` – downloads the channel avatar (user 2011327607) pieces from Roblox
- `pipeline/rbx.py` – reads Roblox binary models (.rbxm) and meshes (v1–v5)
- `pipeline/tts.py` – narration with the Kokoro voice model
- `pipeline/scene_dock_test.py` – Blender (Eevee) test scene: dock, lake, town, sunset/sky lighting, 3 camera cuts
- `pipeline/finish.py` – one-word yellow captions, freeze effect, final MP4 encode
- `pipeline/web_v1_*` – first (low-quality) three.js version, kept for reference

Next: assemble the real R15 avatar from the downloaded meshes, add Creator Store models (needs `ROBLOX_API_KEY`),
then a one-command `make_short` that takes a story idea and produces the finished video.

## Session setup
Paste `bash setup.sh` (run from this repo) into the environment's Setup script, or run it at the start of a session.
Downloaded Roblox assets go in `work/` and are not committed.
