# Конвейер и команды

Всё запускается из `cartoons/`.

| Файл | Роль |
|---|---|
| `template.html` | Каркас новой сцены: `FMT`, `W/H/U`, камера `CAM` + `layer()`, субтитры, `WT()`, motion blur `MB`, `SFX`, `MUSIC` |
| `<name>.html` | Сцена. Отдаёт `window.META = {TOTAL, SFX, MUSIC, VO}`, `window.frameJPEG(t)`, `window.READY` |
| `<name>_script.json` | `{"text": "...", "voice": "<id, необязательно>"}` — текст озвучки |
| `voice.py <name>` | ElevenLabs with-timestamps → `voice_<name>.wav` + `<name>_words.json` (слова с t0/t1) |
| `render.mjs <name> [preview t…]` | Playwright/Chromium рендерит кадры → `<name>_video.mp4`; превью → `prev/<name>_<t>.jpg` |
| `sfx.py <name>` | Синтез эффектов по `SFX`, музыка по `MUSIC`, голос с задержкой `VO`, ducking → `<name>_mix.wav` |
| `make.sh <name>` | Голос (если нет) → кадры → звук → `<name>.mp4` / `<name>_h.mp4` |
| `review.sh <file> [шаг]` | Контактные листы с таймкодом, первый/последний кадр, параметры, громкость, тишина |

## Команды
```bash
cd cartoons
python3 voice.py myname                        # только озвучка (после правки текста удали voice_myname.wav)
node render.mjs myname preview 1 4.5 9         # быстрые пробные кадры
FMT=h node render.mjs myname preview 3         # то же для горизонтали
./make.sh myname                               # полная сборка вертикали
FMT=h ./make.sh myname                         # горизонталь → myname_h.mp4
./review.sh myname.mp4 0.5                     # проверка → review_myname/
```
Долгий рендер (~1–3 мин на 20 с) запускай в фоне и жди завершения, не опрашивая его через sleep.

## Озвучка ElevenLabs
- Ключ — Network secret окружения для `api.elevenlabs.io` с **custom header** `xi-api-key` и **без префикса**.
  Тип Basic или префикс Bearer дают 401 (`authorization header must contain a valid bearer token`).
  Проверка: `curl -s -o /dev/null -w '%{http_code}' https://api.elevenlabs.io/v1/user` → 200.
- Голос по умолчанию `JBFqnCBsd6RMkjVDRZzb`, модель `eleven_multilingual_v2`. Разные персонажи — разные `voice`
  (для диалогов делай несколько script-файлов или реплик и сводить в `sfx.py`).
- Числа пиши словами («тысяча девятьсот двадцать пятый»), иначе голос может прочитать их неправильно. Субтитры показывают сказанное.
- В сцене: `WT('подстрока', n)` — время начала n-го слова с подстрокой, уже со сдвигом `VO`. Привязывай к нему действия и склейки.

## Звук (`sfx.py`)
- Эффекты: step, boot, boop, roll, swish, whoosh, kick, fall, bonk, thud, bounce, twinkle, pop, hmm, ding, gust, flap, catch, gull,
  lamp, bell, honk, paper, sip, pigeon, shatter, sniff, coins, scroll, gasp, drum. Новый звук добавляй в `fx()`.
  Если складываешь звуки разной длины, используй `mixp()`, иначе получишь ошибку broadcast.
- Музыка: `uke` (весёлая укулеле), `city` (тёплый эмбиент + музыкальная шкатулка), `paris` (аккордеон-мюзет, вальс),
  `rome` (лира + бубен). Новая — функция `music_<имя>()` и запись в словарь `mus`.
- Итог проходит через `tanh` с запасом 0,8. Проверяй пик в `review.sh`: он должен быть ниже −1 dBFS.
