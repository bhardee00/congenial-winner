#!/bin/bash
# Cloud environment setup: installs Blender, graphics libs, fonts, voice model.
apt-get update -y
apt-get install -y blender libegl1 libegl-mesa0 libgl1-mesa-dri ffmpeg
pip install -q kokoro-onnx soundfile pillow
python3.12 -m pip install -q --break-system-packages numpy  # Blender 4.0 (Ubuntu) runs Python 3.12; the sound mix needs numpy there
cd "$(dirname "$0")" && mkdir -p work/tts
[ -f work/tts/kokoro.onnx ] || curl -sSL -o work/tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f work/tts/kokoro-fp32.onnx ] || curl -sSL -o work/tts/kokoro-fp32.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f work/tts/voices.bin ] || curl -sSL -o work/tts/voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
[ -f work/Fredoka.ttf ] || curl -sSL -o work/Fredoka.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf"
cp -n assets/face_*.png work/ 2>/dev/null || true
