"""Звук для мультиков: эффекты по событиям из <name>_meta.json + синтезированная музыка.
Запуск: python3 sfx.py stickman|city  ->  <name>_mix.wav
"""
import sys, json, wave, numpy as np

SR = 44100
name = sys.argv[1]
meta = json.load(open(f'{name}_meta.json'))
TOTAL = meta['TOTAL']
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(3)
T = lambda d: np.arange(int(d * SR)) / SR


def env(d, a, r):
    t = T(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def mixp(*xs):
    o = np.zeros(max(len(x) for x in xs))
    for x in xs: o[:len(x)] += x
    return o
def lowpass(x, cutoff):  # one-pole, vectorised via FFT-free IIR approximation
    a = np.exp(-2 * np.pi * np.broadcast_to(cutoff, x.shape) / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def sweep(f0, f1, d, kind='exp'):
    t = T(d); f = f0 * (f1 / f0) ** (t / d) if kind == 'exp' else np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def whoosh(d, c0=300, c1=2500):
    t = T(d); k = np.sin(np.pi * t / d) ** 2
    return lowpass(noise(d), c0 + (c1 - c0) * k) * k * 2.5
def pluck(f, d=1.2, bright=1.0):
    t = T(d); x = sum(np.sin(2 * np.pi * f * h * t) * (bright / h ** 1.6) * np.exp(-t * (2.2 + h * 1.4)) for h in range(1, 7))
    return x * np.minimum(1, t / .003)


def fx(n):
    if n == 'step': return mixp(lowpass(noise(.05), 900) * env(.05, .001, .012) * 3, sweep(160, 90, .06) * env(.06, .001, .02) * .4)
    if n == 'boot':
        return mixp(lowpass(noise(.07), 1400) * env(.07, .001, .016) * 3.2, sweep(140, 70, .08) * env(.08, .001, .025) * .5)
    if n == 'boop': return sweep(500, 1000, .14) * env(.14, .003, .06) * .7
    if n == 'roll':
        d = 1.5; t = T(d); return lowpass(noise(d), 500) * (1 - t / d) * (1 + .5 * np.sin(2 * np.pi * 9 * t)) * 1.2
    if n == 'swish': return whoosh(.28, 800, 5000) * .6
    if n == 'whoosh': return whoosh(.6, 400, 3500)
    if n == 'kick': return mixp(sweep(180, 50, .22) * env(.22, .001, .07) * 1.3, lowpass(noise(.05), 3000) * env(.05, .0005, .01) * 1.5)
    if n == 'fall': return sweep(1800, 500, .55, 'lin') * np.minimum(1, T(.55) / .05) * .25
    if n == 'bonk':
        t = T(.45); f = 260 * (1 + .25 * np.exp(-t * 9) * np.sin(2 * np.pi * 22 * t))
        return mixp(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.45, .001, .14) * 1.1, lowpass(noise(.03), 5000) * env(.03, .0005, .006))
    if n == 'thud': return mixp(sweep(120, 40, .35) * env(.35, .002, .1) * 1.4, lowpass(noise(.12), 700) * env(.12, .001, .03) * 2)
    if n == 'bounce': return sweep(200, 420, .12) * env(.12, .002, .05) * .9
    if n == 'twinkle':
        x = np.zeros(int(1.6 * SR))
        for i, f in enumerate([1568, 2093, 1760, 2349, 1976, 2637, 2093, 2794]):
            p = np.sin(2 * np.pi * f * T(.25)) * env(.25, .002, .07) * .25; o = int(i * .18 * SR); x[o:o + len(p)] += p
        return x
    if n == 'pop': return sweep(900, 300, .08) * env(.08, .002, .03) * .8
    if n == 'hmm':
        t = T(.6); f = 180 + 30 * np.sin(np.pi * t / .6)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) + .3 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * t / .6) * .35
    if n == 'ding':
        t = T(1.2); return (np.sin(2 * np.pi * 1318 * t) + .4 * np.sin(2 * np.pi * 1976 * t)) * env(1.2, .002, .3) * .35
    if n == 'gust':
        d = 2.4; t = T(d); k = np.sin(np.pi * t / d) ** 1.5
        return lowpass(noise(d), 250 + 1500 * k * (1 + .3 * np.sin(2 * np.pi * 1.7 * t))) * k * 3
    if n == 'flap':  # cloth / wings flutter
        d = .5; t = T(d); return lowpass(noise(d), 2500) * (np.abs(np.sin(2 * np.pi * 14 * t)) ** 3) * (1 - t / d) * 1.6
    if n == 'catch': return mixp(lowpass(noise(.09), 4000) * env(.09, .001, .02) * 2.4, sweep(300, 150, .08) * env(.08, .001, .02) * .3)
    if n == 'gull':
        d = .5; t = T(d); f = 1100 + 600 * np.sin(np.pi * t / d) - 400 * t / d
        x = np.sin(2 * np.pi * np.cumsum(f) / SR); x = np.tanh(x * 2) * np.sin(np.pi * t / d) ** 2
        return x * .18
    if n == 'lamp': return mixp(lowpass(noise(.5), 1200) * env(.5, .02, .15) * 1.4, sweep(90, 60, .4) * env(.4, .02, .1) * .5)
    if n == 'bell':
        t = T(4.0); return sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * dcy) for f, a, dcy in [(196, .5, .6), (392.5, .35, .9), (466, .2, 1.2), (587, .15, 1.6), (784, .1, 2.2)]) * .5
    raise ValueError(n)


def music_uke():
    bpm = 112; beat = 60 / bpm; out = np.zeros(N)
    chords = [[261.6, 329.6, 392.0], [196.0, 246.9, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 349.2]]
    t = 0.4; i = 0
    while t < TOTAL - .5:
        ch = chords[(i // 8) % 4]; f = ch[[0, 1, 2, 1][i % 4]] * 2
        p = pluck(f, .7, 1.0) * .1; o = int(t * SR); out[o:o + len(p)] += p[:N - o]
        if i % 4 == 0:
            b = pluck(ch[0] / 2, 1.0, .6) * .16; out[o:o + len(b)] += b[:N - o]
        if i % 2 == 1:
            s = lowpass(noise(.04), 6000) * env(.04, .001, .01) * .05; s = s - lowpass(s, 2000); out[o:o + len(s)] += s[:N - o]
        t += beat / 2; i += 1
    return out


def music_city():
    out = np.zeros(N); tt = np.arange(N) / SR
    # warm pad: detuned saws through lowpass, slow chord changes (3/4 feel)
    chords = [[146.8, 220.0, 293.7, 349.2], [130.8, 196.0, 261.6, 329.6], [116.5, 174.6, 233.1, 293.7], [130.8, 196.0, 261.6, 311.1]]
    seg = 3.6
    pad = np.zeros(N)
    for ci in range(int(TOTAL / seg) + 2):
        ch = chords[ci % 4]; o = int(ci * seg * SR); d = seg + 1.2; t = T(d)
        a = np.minimum(1, t / 1.0) * np.minimum(1, (d - t) / 1.2)
        x = sum(((2 * ((f * dt * t) % 1) - 1)) for f in ch for dt in (0.997, 1.003)) * a
        x = x[:max(0, N - o)]; pad[o:o + len(x)] += x
    out += lowpass(pad, 900) * .035
    # music-box / harpsichord arpeggio
    beat = .4; t = 1.2; i = 0
    while t < TOTAL - 1:
        ch = chords[int(t / seg) % 4]; f = ch[[1, 2, 3, 2, 1, 3][i % 6]] * 2
        p = pluck(f, 1.0, 1.4) * .055; o = int(t * SR); out[o:o + len(p)] += p[:N - o]
        t += beat; i += 1
    # ambience: soft wind + water lapping
    amb = lowpass(noise(N / SR), 400) * (0.6 + .4 * np.sin(2 * np.pi * .13 * tt))
    out += amb * .12
    return out


ev = np.zeros(N)
for t, n, v in meta['SFX']:
    x = fx(n) * v; o = int(t * SR)
    if o >= N: continue
    ev[o:o + len(x)] += x[:N - o]
mus = {'uke': music_uke, 'city': music_city}[meta.get('MUSIC', 'uke')]()
fade = np.minimum(1, np.arange(N) / (SR * .5)) * np.clip((TOTAL - np.arange(N) / SR) / 1.0, 0, 1)
mix = (ev * .8 + mus) * fade
mix = np.tanh(mix * 1.1) * .9
st = np.stack([mix, mix], 1)
with wave.open(f'{name}_mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', name, TOTAL)
