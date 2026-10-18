#!/bin/bash
# Сборка мультиков: ./make.sh [stickman] [city]  (без аргументов — оба)
set -e
cd "$(dirname "$0")"
for n in ${@:-stickman city}; do
  node render.mjs "$n" video
  python3 sfx.py "$n"
  ffmpeg -y -loglevel error -i "${n}_video.mp4" -i "${n}_mix.wav" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$n.mp4"
  rm -f "${n}_video.mp4" "${n}_mix.wav" "${n}_meta.json"
  echo "Готово: $(pwd)/$n.mp4"
done
