"""Stimme: Vorspann abschneiden, lange Pausen kürzen, Wortzeiten umrechnen."""
import json, subprocess, numpy as np, wave, sys
SR = 24000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1] + '.wav', '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
words = json.load(open(sys.argv[1] + '_words.json'))
start = next(w[1] for w in words if w[0].lower().startswith(('shel', 'schel'))) - 0.12
words = [w for w in words if w[1] >= start - 0.1]
# Pausen anhand Wortgrenzen: Lücke > MAXP wird auf MAXP gekürzt
MAXP = 0.32
segs = []      # (src_a, src_b) Abschnitte, die behalten werden
cur = start
for w0, w1 in zip(words, words[1:]):
    gap_a, gap_b = w0[2], w1[1]
    if gap_b - gap_a > MAXP + 0.05:
        keep_end = gap_a + MAXP / 2
        segs.append((cur, keep_end))
        cur = gap_b - MAXP / 2
segs.append((cur, words[-1][2] + 0.5))
out = []
fade = int(0.01 * SR)
mapping = []
t_new = 0.0
for sa, sb in segs:
    x = a[int(sa * SR):int(sb * SR)].copy()
    x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
    out.append(x)
    mapping.append((sa, sb, t_new))
    t_new += sb - sa
y = np.concatenate(out)


def conv(t):
    for sa, sb, tn in mapping:
        if t <= sb:
            return tn + max(0.0, t - sa)
    return t_new


nw = [(w[0], round(conv(w[1]), 3), round(conv(w[2]), 3)) for w in words]
json.dump(nw, open('audio/vo_words.json', 'w'), ensure_ascii=False)
with wave.open('audio/vo.wav', 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
print('dur', round(len(y) / SR, 2))
print(' '.join(f'{w[0]}@{w[1]:.2f}' for w in nw))
