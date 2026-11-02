#!/bin/bash
# Frames (720x1280 PNG) -> 1080x1920 30fps H.264, silent, no captions.
set -e
D="$(cd "$(dirname "$0")/../.." && pwd)/work/wish"
ffmpeg -v error -y -framerate 30 -start_number 0 -i "$D/frames/f_%05d.png" \
  -vf "scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -crf 16 -r 30 -an -movflags +faststart "${1:-$D/the_wish_9x16.mp4}"
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,codec_type -of compact "${1:-$D/the_wish_9x16.mp4}"
