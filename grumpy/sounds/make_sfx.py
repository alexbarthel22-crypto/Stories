"""Selbst erzeugte Soundeffekte (keine Rechte Dritter). Aufruf: python3 make_sfx.py -> sfx/*.wav"""
import wave
from pathlib import Path
import numpy as np

SR = 44100
OUT = Path(__file__).parent / "sfx"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(3)


def save(name, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def t(sec):
    return np.arange(int(sec * SR)) / SR


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for k in range(len(x)):
        s = (1 - a) * x[k] + a * s; y[k] = s
    return y


def noise(sec):
    return rng.standard_normal(int(sec * SR))


# Grollen (Vulkan/Insel wächst)
tt = t(3.0); save("rumble", lp(noise(3.0), 90) * np.minimum(tt / 0.6, 1) * np.minimum((3.0 - tt) / 1.0, 1) * (1 + 0.4 * np.sin(2 * np.pi * 7 * tt)))
# Explosion
tt = t(2.2); save("boom", (lp(noise(2.2), 400) * 0.7 + np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-tt / 0.08)) / SR)) * np.exp(-tt / 0.5))
# Welle: anschwellendes Rauschen + Aufprall
tt = t(2.6)
swell = np.minimum(tt / 1.2, 1) ** 2 * np.exp(-np.maximum(tt - 1.2, 0) / 0.6)
crash = np.where(tt > 1.15, np.exp(-(tt - 1.15) / 0.35), 0)
save("wave", lp(noise(2.6), 1500) * swell + lp(noise(2.6), 3000) * crash * 0.8)
# dumpfer Aufprall (Baum, Rucksack)
tt = t(0.8); save("thud", (np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-tt / 0.03)) / SR) + 0.4 * lp(noise(0.8), 600)) * np.exp(-tt / 0.15))
# Prasseln (Zigarettenregen): viele kleine Klicks
x = np.zeros(int(2.4 * SR))
for _ in range(260):
    i = int(rng.uniform(0, 2.2) * SR); n = int(0.012 * SR)
    x[i:i + n] += rng.standard_normal(n) * np.exp(-np.arange(n) / (0.002 * SR)) * rng.uniform(0.3, 1)
save("patter", x - lp(x, 1500))
# Plopp (etwas erscheint)
tt = t(0.25); save("pop", np.sin(2 * np.pi * np.cumsum(300 + 900 * tt / 0.25) / SR) * np.exp(-tt / 0.05))
# Platschen
tt = t(0.9); save("splash", (lp(noise(0.9), 2500) - lp(noise(0.9), 300)) * np.exp(-tt / 0.18) * np.minimum(tt / 0.01, 1))
# Flugzeug: Propeller-Brummen mit Doppler
tt = t(3.2)
f = 95 * (1 + 0.08 * np.tanh((1.6 - tt) * 2))
prop = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + lp(noise(3.2), 500) * 0.6
save("plane", lp(prop, 900) * np.exp(-((tt - 1.6) / 1.1) ** 2))
# Magie: aufsteigendes Glitzern (Insel wird riesig)
x = np.zeros(int(2.6 * SR))
for k, m in enumerate([69, 72, 76, 79, 81, 84, 88, 91, 93]):
    f0 = 440 * 2 ** ((m - 69) / 12); i = int(k * 0.18 * SR); n = int(0.9 * SR)
    seg = np.sin(2 * np.pi * f0 * np.arange(n) / SR) * np.exp(-np.arange(n) / (0.25 * SR))
    x[i:i + n] += seg[: len(x) - i]
save("magic", x)
print("SFX:", sorted(p.name for p in OUT.glob("*.wav")))
