# Как работает интернет — анимация с озвучкой

Вертикальное видео 1080×1920 (~65 с): что происходит за 0,1 секунды, когда открываешь сайт —
адрес → DNS → IP → пакеты → сервер → браузер собирает страницу.

Готовое видео: `kak-rabotaet-internet.mp4`

## Как устроено

| Файл | Что делает |
|---|---|
| `anim.html` | Вся анимация на canvas. Открывается в браузере (клик — старт). |
| `script.json` | Текст озвучки и субтитров по сценам |
| `timeline.json` | Длительности сцен (и тайминги новой озвучки, если есть) |
| `elevenlabs.py` | Озвучка через ElevenLabs + автоподгонка анимации под темп голоса |
| `render.mjs` | Рендер кадров через Playwright/Chromium → `video.mp4` |
| `audio.py` | Синтез звуковых эффектов и бита, сведение с голосом → `mix.wav` |
| `make.sh` | Полная сборка одной командой |
| `voice/` | Текущая озвучка (RHVoice, офлайн) |

## Сборка

```bash
pip install numpy
./make.sh            # с текущей озвучкой
./make.sh --eleven   # с озвучкой ElevenLabs (ключ — Network secret для api.elevenlabs.io
                     # с заголовком xi-api-key, или переменная ELEVENLABS_API_KEY)
```

Нужны `ffmpeg`, Node.js с Playwright и Chromium.

## Мультики (`cartoons/`)

Ролики-мультики, нарисованные кодом, с озвучкой ElevenLabs: стикмен, «Золотой час», «Париж» (Люстиг), «Рим» (дудл).
Скилл для Claude Code: `.claude/skills/cartoon-video/` (режиссура, стили, конвейер, проверка).

```bash
cd cartoons
./make.sh rome            # вертикально 1080×1920 → rome.mp4
FMT=h ./make.sh myscene   # горизонтально 1920×1080 → myscene_h.mp4
./review.sh rome.mp4      # контактные листы, параметры, громкость
```
Новая сцена начинается с копии `cartoons/template.html`.
