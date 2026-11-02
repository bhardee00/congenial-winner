#!/bin/bash
# Runs on its own: finish 'The Wish' render, encode it, then render + encode 'The Voice'.
cd "$(dirname "$0")/../.."
LOG=work/queue.log
echo "$(date) queue started" >> $LOG
while pgrep -f "work/wish/wish.blend" > /dev/null; do sleep 30; done
n=$(ls work/wish/frames | wc -l); echo "$(date) wish render ended with $n frames" >> $LOG
if [ "$n" -lt 3744 ]; then blender -b work/wish/wish.blend -P pipeline/wish/story.py -- render 0 3744 >> work/wish/logs/full.log 2>&1; fi
bash pipeline/wish/encode.sh wish >> $LOG 2>&1 && echo "$(date) WISH_ENCODED" >> $LOG
mkdir -p work/voice/logs
blender -b work/voice/wish.blend -P pipeline/wish/voice.py -- render 0 3606 > work/voice/logs/full.log 2>&1
echo "$(date) voice render ended with $(ls work/voice/frames | wc -l) frames" >> $LOG
bash pipeline/wish/encode.sh voice >> $LOG 2>&1 && echo "$(date) VOICE_ENCODED" >> $LOG
