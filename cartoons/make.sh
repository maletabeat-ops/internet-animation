#!/bin/bash
# Сборка мультиков: [FMT=v|h] [FPS=30] ./make.sh <name> [<name> ...]
#   FMT=v — вертикальный 1080×1920 (по умолчанию), FMT=h — горизонтальный 1920×1080
#   Если есть <name>_script.json, а озвучки ещё нет — сначала делается голос ElevenLabs (voice.py).
#   Результат: <name>.mp4 (для FMT=h — <name>_h.mp4)
set -e
cd "$(dirname "$0")"
export FMT=${FMT:-v} FPS=${FPS:-30}
for n in ${@:-stickman city}; do
  if [ -f "${n}_script.json" ] && [ ! -f "voice_${n}.wav" ]; then python3 voice.py "$n"; fi
  out="$n.mp4"; [ "$FMT" = h ] && out="${n}_h.mp4"
  node render.mjs "$n" video
  python3 sfx.py "$n"
  ffmpeg -y -loglevel error -i "${n}_video.mp4" -i "${n}_mix.wav" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$out"
  rm -f "${n}_video.mp4" "${n}_mix.wav" "${n}_meta.json"
  echo "Готово: $(pwd)/$out"
done
