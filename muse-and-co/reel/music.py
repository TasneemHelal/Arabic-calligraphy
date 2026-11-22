# Original 15 s track for the Muse & Co. reel: 128 BPM upbeat pop-house in F major, with SFX on the animation cues.
# Everything is synthesised here, so the track is fully owned (no licensing).
import numpy as np, wave
from scipy.signal import butter, sosfilt

SR, BPM = 44100, 128
B = 60 / BPM                       # one beat = 0.46875 s
LEN = 15.0
N = int(SR * LEN)
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)

def midi(n): return 440 * 2 ** ((n - 69) / 12)
def env(n, a=.003, d=.2, curve=6):
    t = np.arange(n) / SR
    e = np.exp(-t * curve / max(d, 1e-3)); k = int(a * SR)
    if k: e[:k] *= np.linspace(0, 1, k)
    return e
def flt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def add(sig, t, gain=1., pan=0.):
    i = int(t * SR); sig = sig[: max(0, N - i)]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * gain * l * 1.414; mix[i:i + len(sig), 1] += sig * gain * r * 1.414

def kick():
    n = int(.42 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, .001, .42, 5) + .25 * flt(rng.standard_normal(n), "highpass", 3000) * env(n, .0005, .01, 6)
def clap():
    n = int(.25 * SR); x = flt(rng.standard_normal(n), "bandpass", [900, 2600])
    e = env(n, .001, .18, 6)
    for k in (0.0, .011, .022): e += .6 * env(n, .001, .012, 6) * (np.arange(n) >= int(k * SR))
    return x * e * .9
def hat(open_=False):
    n = int((.22 if open_ else .05) * SR)
    return flt(rng.standard_normal(n), "highpass", 7500) * env(n, .001, .22 if open_ else .045, 5)
def snare():
    n = int(.18 * SR); t = np.arange(n) / SR
    return (.6 * flt(rng.standard_normal(n), "bandpass", [1500, 7000]) + .5 * np.sin(2 * np.pi * 190 * t)) * env(n, .001, .16, 6)
def saw(f, n, detune=(-.12, -.05, 0, .05, .12)):
    t = np.arange(n) / SR
    return sum(2 * ((t * f * 2 ** (d / 12) + p) % 1) - 1 for d, p in zip(detune, rng.random(len(detune)))) / len(detune)
def stab(notes, dur=.2, cutoff=3200):
    n = int(dur * SR); x = sum(saw(midi(m), n) for m in notes) / len(notes)
    return flt(x, "lowpass", cutoff) * env(n, .003, dur, 4)
def bass(note, dur=.2):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(note)
    x = .7 * np.sin(2 * np.pi * f * t) + .35 * flt(saw(f, n, (0,)), "lowpass", 900)
    return x * env(n, .004, dur, 3)
def pluck(note, dur=.3):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(note)
    return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * env(n, .002, dur, 7)
def noise_sweep(dur, f0, f1, up=True):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); seg = 512
    for i in range(0, n, seg):
        fr = i / n; fc = f0 * (f1 / f0) ** fr
        out[i:i + seg] = flt(x[i:i + seg], "bandpass", [fc * .7, min(fc * 1.4, SR / 2 - 100)], 1)
    e = np.linspace(0, 1, n) ** 2 if up else np.linspace(1, 0, n) ** 1.5
    return out * e
def crash(dur=2.5):
    n = int(dur * SR); return flt(rng.standard_normal(n), "highpass", 5000) * env(n, .002, dur, 4)
def boom():
    n = int(1.4 * SR); t = np.arange(n) / SR
    f = 30 + 80 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, 1.4, 3.5)

CHORDS = {"F": [65, 69, 72], "C": [64, 67, 72], "Dm": [65, 69, 74], "Bb": [65, 70, 74]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34}
PROG = ["F", "C", "Dm", "Bb"]
bt = lambda b: b * B
duck = np.ones(N)                                  # sidechain envelope for pumping bass/stabs

# ---- INTRO (beats 0-7): word hits every 2 beats, building snare roll + riser, gap before drop
for i, b in enumerate([0, 2, 4, 6]):
    add(kick(), bt(b), .9); add(stab(CHORDS[PROG[i]], .38, 2200), bt(b), .55)
    add(pluck(77 + [0, 2, 4, 7][i], .35), bt(b), .25, .3)
for b in np.arange(0, 7.5, .5): add(hat(), bt(b + .25 if b % 1 else b), .22, -.3)
for k, b in enumerate(np.concatenate([np.arange(4, 6, .5), np.arange(6, 7.5, .25)])):
    add(snare(), bt(b), .2 + .5 * k / 10)
add(noise_sweep(bt(4) - .05, 300, 9000), bt(4) - .05, .35)

# ---- DROP (beats 8-27)
add(crash(), bt(8), .25); add(boom(), bt(8), .5)
for b in range(8, 28):
    add(kick(), bt(b), 1.0)
    i0 = int(bt(b) * SR); n = int(.22 * SR)
    duck[i0:i0 + n] = np.minimum(duck[i0:i0 + n], 1 - .75 * np.exp(-np.arange(n) / SR * 18))
    if b % 2 == 1: add(clap(), bt(b), .55, .05)
    add(hat(True), bt(b + .5), .18, .35)
    for s in (.25, .75): add(hat(), bt(b + s), .12, -.35)
    ch = PROG[((b - 8) // 4) % 4]
    add(stab(CHORDS[ch], .2), bt(b + .5), .42, (-.2 if b % 2 else .2))
for b in np.arange(8, 28, .5):                     # off-beat bass
    ch = PROG[(int(b - 8) // 4) % 4]
    add(bass(ROOT[ch] + (12 if (b * 2) % 4 == 3 else 0), .2), bt(b + .25), .55)

# ---- OUTRO (beats 28-31): final chord + crash, sparkle arpeggio
add(kick(), bt(28), 1.0); add(crash(3.5), bt(28), .28); add(boom(), bt(28), .5)
add(stab(CHORDS["F"] + [77], 2.6, 2600), bt(28), .5)
add(bass(41, 1.8), bt(28), .6)
for k, m in enumerate([84, 88, 91, 96, 91, 96, 100]): add(pluck(m, .5), bt(28.5) + k * B / 4, .16, (-.5 + k / 6))

# ---- SFX on animation cues
add(noise_sweep(.55, 800, 6000, up=False), 3.62, .35, -.3)                  # brush whoosh
for k, m in enumerate([84, 88, 91, 96]): add(pluck(m, .35), 4.78 + k * .06, .2, .4 - k * .25)   # paint splash

# apply sidechain to everything except a bit of the kick/clap transient (simple approach: gentle global pump)
mix *= (.55 + .45 * duck)[:, None]
mix[-int(.6 * SR):] *= np.linspace(1, 0, int(.6 * SR))[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) * .89
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("music ok", LEN, "s; drop at", round(bt(8), 3), "s; impact at", round(bt(20), 3), "s")
