#!/bin/bash
# Полная сборка: озвучка ElevenLabs -> кадры -> звук -> итоговое видео
set -e
cd "$(dirname "$0")"
[ -n "$ELEVENLABS_API_KEY" ] && python3 elevenlabs.py
node render.mjs video
python3 audio.py
ffmpeg -y -loglevel error -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart kak-rabotaet-internet.mp4
echo "Готово: $(pwd)/kak-rabotaet-internet.mp4"
