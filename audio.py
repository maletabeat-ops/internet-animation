import json, wave, numpy as np
SR = 44100
meta = json.load(open('meta.json')); TL = meta['TL']; TOTAL = meta['TOTAL']
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(1)
T = lambda d: np.arange(int(d * SR)) / SR

def onepole(x, a):  # lowpass, a may be array
    y = np.empty_like(x); s = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
def sweep(f0, f1, d, kind='exp'):
    t = T(d); f = f0 * (f1 / f0) ** (t / d) if kind == 'exp' else np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def mixp(a, b):
    n = max(len(a), len(b)); o = np.zeros(n); o[:len(a)] += a; o[:len(b)] += b; return o
def env(d, a, r):
    t = T(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
def noise(d): return rng.uniform(-1, 1, int(d * SR))

def whoosh(d=.75, hi=.25):
    t = T(d); x = noise(d); k = np.sin(np.pi * t / d) ** 2
    return onepole(x, 0.02 + hi * k) * k * 2.2
def fx(name):
    if name == 'whoosh': return whoosh()
    if name == 'swish': return whoosh(.4, .45) * .8
    if name == 'pop': return sweep(950, 320, .09) * env(.09, .002, .03) * .8
    if name == 'drop': return sweep(500, 1100, .1) * env(.1, .002, .04) * .6
    if name == 'boom':
        return (sweep(130, 38, .8) * env(.8, .003, .25) + onepole(noise(.8), .08) * env(.8, .001, .05) * 2) * .9
    if name == 'key':
        n = noise(.03); n = np.diff(n, prepend=0) * env(.03, .0005, .006); return n * .5
    if name == 'thud': return mixp(sweep(170, 55, .3) * env(.3, .002, .09), np.diff(noise(.05), prepend=0) * env(.05, .0005, .01) * .4)
    if name == 'err':
        b = np.sign(np.sin(2 * np.pi * 180 * T(.13))) * .25; g = np.zeros(int(.06 * SR)); return np.concatenate([b, g, b])
    if name == 'glitch':
        d = .45; t = T(d); f = np.repeat(rng.choice([200, 400, 800, 1600, 3200], 30), int(d * SR / 30) + 1)[:len(t)]
        return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .15 * (1 - t / d)
    if name == 'ding':
        t = T(1.4); return (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1976 * t) + .25 * np.sin(2 * np.pi * 2637 * t)) * env(1.4, .002, .35) * .35
    if name == 'lock':
        a = fx('key') * 2; b = np.sin(2 * np.pi * 1500 * T(.15)) * env(.15, .002, .05) * .4
        return np.concatenate([a, np.zeros(2000), a, np.zeros(1500), b])
    if name == 'knock': return mixp(sweep(110, 70, .16) * env(.16, .001, .04) * 1.2, onepole(noise(.04), .2) * env(.04, .0005, .008))
    if name == 'burst':
        x = onepole(noise(.6), .3) * env(.6, .001, .12) * 1.2
        for k in range(6):
            p = fx('pop'); o = int((.04 + k * .05) * SR); x[o:o + len(p)] += p * .5
        return x
    if name == 'rise':
        d = 1.2; t = T(d); return (onepole(noise(d), 0.03 + .3 * t / d) * 1.5 + sweep(200, 900, d) * .15) * (t / d) ** 2
    if name == 'wave': d = 1.8; t = T(d); return onepole(noise(d), .015) * np.sin(np.pi * t / d) ** 2 * 3
    if name == 'confetti':
        x = np.zeros(int(1.0 * SR))
        for k in range(18):
            p = sweep(rng.uniform(1500, 3500), rng.uniform(800, 1500), .04) * env(.04, .001, .01) * .25
            o = int(rng.uniform(0, .9) * SR); x[o:o + len(p)] += p
        return x
    if name == 'blink': return sweep(380, 140, .18) * env(.18, .01, .06) * .6
    raise ValueError(name)

sfx = np.zeros(N)
for t, name in meta['SFX']:
    x = fx(name); o = int(max(t, 0) * SR); sfx[o:o + len(x)] += x[:N - o]

# voice
def readwav(p):
    w = wave.open(p); sr = w.getframerate(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    n2 = int(len(a) * SR / sr); return np.interp(np.arange(n2) * sr / SR, np.arange(len(a)), a)
voice = np.zeros(N)
for s in TL:
    a = readwav(f"voice/{s['id']}.wav"); a = a / (np.abs(a).max() + 1e-9) * .9
    o = int((s['start'] + .4) * SR); voice[o:o + len(a)] += a

# music: 112 bpm, Am F C G
bpm = 112; beat = 60 / bpm
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
t = np.arange(N) / SR
bar = (t / (beat * 4)).astype(int); ci = (bar // 1) % 4
pad = np.zeros(N); bass = np.zeros(N)
for k, ch in enumerate(chords):
    m = ci == k
    for note in ch:
        for det in (-.12, .12):
            f = mtof(note) * 2 ** (det / 12); ph = (t[m] * f) % 1; pad[m] += (2 * ph - 1) * .05
    f = mtof(ch[0] - 24); eighth = (t[m] / (beat / 2)) % 1
    bass[m] = np.sin(2 * np.pi * f * t[m]) * np.exp(-eighth * 3) * .35
pad = onepole(pad, .06)
drums = np.zeros(N)
kick = sweep(110, 42, .3) * env(.3, .001, .09) * .9
hat = np.diff(noise(.05), prepend=0) * env(.05, .0005, .012) * .25
nb = int(TOTAL / beat)
for i in range(nb):
    o = int(i * beat * SR); drums[o:o + len(kick)] += kick[:N - o]
    o2 = int((i + .5) * beat * SR); drums[o2:o2 + len(hat)] += hat[:N - o2]
music = pad + bass + drums
# ducking under voice
venv = onepole(np.abs(voice), .0008); venv = venv / (venv.max() + 1e-9)
duck = 1 - .55 * np.clip(venv * 4, 0, 1)
fade = np.clip(t / 1.5, 0, 1) * np.clip((TOTAL - t) / 1.5, 0, 1)
mix = voice * 1.0 + music * duck * fade * .32 + sfx * .45
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.abs(mix).max() * .93
w = wave.open('mix.wav', 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', len(mix) / SR)
