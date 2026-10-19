#!/bin/bash
# Проверка готового ролика: ./review.sh <file.mp4> [шаг_сек=0.5]
# Делает контактные листы по всему ролику (каждые N секунд, с таймкодом), кадры первого/последнего
# мгновения, параметры потока и громкость. Результат — в review_<имя>/ ; листы нужно открыть и просмотреть.
set -e
f="$1"; step="${2:-0.5}"; [ -f "$f" ] || { echo "нет файла $f"; exit 1; }
d="review_$(basename "${f%.*}")"; rm -rf "$d"; mkdir -p "$d"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels -of default=nw=1 "$f" | tee "$d/params.txt"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
w=$(ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0 "$f"); h=$(ffprobe -v error -select_streams v -show_entries stream=height -of csv=p=0 "$f")
if [ "$w" -gt "$h" ]; then tile=4x4; sc=480:-1; else tile=8x2; sc=270:-1; fi
ffmpeg -v error -i "$f" -vf "fps=1/$step,scale=$sc,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{pts\:hms}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=$tile" "$d/sheet_%02d.jpg"
ffmpeg -v error -ss 0.05 -i "$f" -frames:v 1 "$d/first.jpg"
ffmpeg -v error -sseof -0.1 -i "$f" -frames:v 1 "$d/last.jpg"
ffmpeg -hide_banner -nostats -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2 | tee "$d/loudness.txt"
ffmpeg -hide_banner -nostats -i "$f" -af silencedetect=n=-45dB:d=1.5 -f null - 2>&1 | grep silence_ | tee "$d/silence.txt" || true
echo "длительность: $dur с; листы: $(ls $d/sheet_*.jpg | wc -l) шт в $d/"
