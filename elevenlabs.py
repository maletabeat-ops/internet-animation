"""Озвучка через ElevenLabs + автоподгонка таймингов анимации.
Нужны: ELEVENLABS_API_KEY (и опционально ELEVENLABS_VOICE_ID).
Запуск: python3 elevenlabs.py && node render.mjs video && python3 audio.py && (mux)
"""
import os, json, base64, subprocess, urllib.request

KEY = os.environ['ELEVENLABS_API_KEY']
VOICE = os.environ.get('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')
MODEL = os.environ.get('ELEVENLABS_MODEL', 'eleven_multilingual_v2')

# текст для ElevenLabs и якоря: [время фразы в старой (RHVoice) озвучке, начало фразы в новом тексте]
SCENES = {
 'hook': ("Что происходит, когда ты открываешь сайт? За одну десятую секунды случается целое приключение. Погнали!",
          [[0, 'Что'], [1.45, 'когда'], [3.45, 'За одну'], [5.3, 'целое'], [7.7, 'Погнали']]),
 'type': ("Ты вводишь адрес. Например, котики точка ру. И жмёшь Энтер.",
          [[0.1, 'Ты'], [1.3, 'Например'], [2.32, 'котики'], [3.6, 'И жмёшь'], [4.0, 'Энтер']]),
 'dns': ("Но компьютеры не понимают названий. Им нужны цифры. Поэтому браузер спрашивает DNS. Это телефонная книга интернета.",
         [[0, 'Но'], [2.7, 'Им'], [3.99, 'Поэтому'], [6.54, 'Это']]),
 'ip': ("DNS находит номер сервера — IP-адрес. Теперь браузер знает, куда стучаться.",
        [[0, 'DNS'], [2.37, 'номер'], [3.47, 'IP'], [5.24, 'Теперь']]),
 'packets': ("Запрос режется на маленькие кусочки — пакеты. Каждый летит своим путём, через десятки роутеров. А иногда и через океан, по подводным кабелям.",
             [[0, 'Запрос'], [3.0, 'пакеты'], [3.66, 'Каждый'], [5.75, 'через десятки'], [7.5, 'А иногда'], [9.36, 'по подводным']]),
 'server': ("Пакеты добираются до сервера. Он собирает их, понимает запрос и отправляет страницу обратно.",
            [[0.1, 'Пакеты'], [2.25, 'Он'], [3.65, 'понимает']]),
 'build': ("Браузер собирает сайт. Каркас. Стили. Картинки. И вот — котики на экране!",
           [[0, 'Браузер'], [1.82, 'Каркас'], [2.5, 'Стили'], [3.12, 'Картинки'], [3.9, 'И вот'], [4.69, 'котики']]),
 'outro': ("И всё это быстрее, чем ты моргнёшь. Вот так работает интернет.",
           [[0, 'И всё'], [2.4, 'моргнёшь'], [3.25, 'Вот так']]),
}

old = {s['id']: s for s in json.load(open('timeline_rhvoice.json'))}
out = []
os.makedirs('voice11', exist_ok=True)
for sid, (text, anchors) in SCENES.items():
    req = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128',
        data=json.dumps({'text': text, 'model_id': MODEL,
                         'voice_settings': {'stability': 0.4, 'similarity_boost': 0.8, 'style': 0.35, 'use_speaker_boost': True}}).encode(),
        headers={'xi-api-key': KEY, 'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    open(f'voice11/{sid}.mp3', 'wb').write(base64.b64decode(r['audio_base64']))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'voice11/{sid}.mp3', f'voice/{sid}.wav'], check=True)
    al = r['alignment']; chars = ''.join(al['characters']); st = al['character_start_times_seconds']
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'voice/{sid}.wav']))
    warp, pos = [], 0
    for old_t, phrase in anchors:
        i = chars.find(phrase, pos)
        if i < 0: print('  якорь не найден:', sid, phrase); continue
        pos = i + 1; warp.append([round(st[i], 3), old_t])
    warp.append([round(dur, 3), old[sid]['dur']])
    out.append({'id': sid, 'say': text, 'cap': old[sid]['cap'], 'dur': round(dur, 3), 'warp': warp})
    print(sid, round(dur, 2), warp)
json.dump(out, open('timeline.json', 'w'), ensure_ascii=False, indent=1)
print('готово: timeline.json обновлён')
