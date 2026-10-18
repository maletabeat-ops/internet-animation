"""Озвучка ElevenLabs с таймингами слов: python3 voice.py <name>
Берёт текст из <name>_script.json, пишет voice_<name>.wav и <name>_words.json (слова + время)."""
import os, sys, json, base64, subprocess, urllib.request
name = sys.argv[1]
cfg = json.load(open(f'{name}_script.json'))
voice = cfg.get('voice', os.environ.get('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb'))
req = urllib.request.Request(
    f'https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128',
    data=json.dumps({'text': cfg['text'], 'model_id': 'eleven_multilingual_v2',
                     'voice_settings': {'stability': .42, 'similarity_boost': .8, 'style': .4, 'use_speaker_boost': True}}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
open(f'voice_{name}.mp3', 'wb').write(base64.b64decode(r['audio_base64']))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'voice_{name}.mp3', '-ar', '44100', '-ac', '1', f'voice_{name}.wav'], check=True)
al = r['alignment']; ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
words, cur = [], None
for c, a, b in zip(ch, st, en):
    if c.isspace():
        if cur: words.append(cur); cur = None
        continue
    if cur is None: cur = {'w': c, 't0': a, 't1': b}
    else: cur['w'] += c; cur['t1'] = b
if cur: words.append(cur)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'voice_{name}.wav']))
json.dump({'dur': dur, 'words': words}, open(f'{name}_words.json', 'w'), ensure_ascii=False)
print(name, round(dur, 2), 'с,', len(words), 'слов')
