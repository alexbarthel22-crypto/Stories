#!/usr/bin/env python3
"""Bereitet eine Story fürs Rendern vor.

  python3 tools/prep.py stories/<name>.json [--ohne-stimmen]

- erzeugt die Stimmen mit Gemini-TTS (oder ElevenLabs), zwischengespeichert: nur neue/geänderte Sätze werden neu erzeugt
- berechnet das Timing jedes Beats, Untertitel-Häppchen und die Mundbewegung (Lautstärke pro Frame)
- mischt Stimmen + Atmo + Geräusche zu build/<name>/mix.wav
- schreibt build/<name>/timeline.json für die Render-Engine
"""
import base64, hashlib, json, time, urllib.error, os, re, subprocess, sys, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
args = [a for a in sys.argv[1:] if not a.startswith('--')]
NO_TTS = '--ohne-stimmen' in sys.argv
# --neu "Textstück" erzeugt passende Sätze neu (mehrfach möglich)
NEU = [sys.argv[i + 1] for i, a in enumerate(sys.argv[:-1]) if a == '--neu']
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--neu']
story_path = args[0]
story = json.load(open(story_path))
name = os.path.splitext(os.path.basename(story_path))[0]
out = os.path.join(ROOT, 'build', name); os.makedirs(os.path.join(out, 'voice'), exist_ok=True)
FPS = story.get('fps', 30)
API = 'https://api.elevenlabs.io/v1'

_voices = None
def voice_id(v):
    global _voices
    if re.fullmatch(r'[A-Za-z0-9]{20}', v): return v
    if _voices is None:
        _voices = json.load(urllib.request.urlopen(urllib.request.Request(API + '/voices', headers={}), timeout=60))['voices']
    for x in _voices:
        if x['name'].lower().startswith(v.lower()): return x['voice_id']
    raise SystemExit(f'Stimme "{v}" nicht gefunden')


def load_wav(fn):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def tts(text, spec, regie=None):
    """Stimme erzeugen. spec['stimme'] = 'gemini:Leda' (Standard: Gemini) oder 'elevenlabs:Laura'."""
    prov, _, v = spec['stimme'].partition(':')
    if not v: prov, v = 'gemini', prov
    regie = regie or spec.get('regie', '')
    key = hashlib.sha1(json.dumps([prov, v, text, regie, spec.get('stimme_einstellungen'), spec.get('tempo')]).encode()).hexdigest()[:16]
    fn = os.path.join(out, 'voice', key + ('.wav' if prov == 'gemini' else '.mp3'))
    if os.path.exists(fn) and any(x in text for x in NEU): os.remove(fn)
    if not os.path.exists(fn):
        if prov == 'gemini':
            # kurzes Format, sonst liest Gemini die Anweisung mit vor
            prompt = (f"### DIRECTOR'S NOTES\nStyle: {regie}. Speak only the transcript, in German.\n\n### TRANSCRIPT\n{text}"
                      if regie else f"### DIRECTOR'S NOTES\nSpeak only the transcript, in German.\n\n### TRANSCRIPT\n{text}")
            body = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseModalities': ['AUDIO'],
                    'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': v}}}}}
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{spec.get("modell", "gemini-3.8-flash-tts")}:generateContent',
                data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': os.environ['GEMINI_API_KEY']})
            for tries in range(8):
                try:
                    r = json.load(urllib.request.urlopen(req, timeout=300)); break
                except urllib.error.HTTPError as e:
                    if e.code not in (429, 500, 503) or tries == 7: raise
                    wait = 15 * (tries + 1); print(f'  (Gemini ausgelastet, warte {wait}s …)'); time.sleep(wait)
            p = r['candidates'][0]['content']['parts'][0]['inlineData']; data = base64.b64decode(p['data'])
            if 'wav' not in p['mimeType']:  # rohes PCM (L16, 24 kHz)
                rate = int(re.search(r'rate=(\d+)', p['mimeType']).group(1)) if 'rate=' in p['mimeType'] else 24000
                data = subprocess.run(['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(rate), '-ac', '1', '-i', '-', '-f', 'wav', '-'], input=data, capture_output=True, check=True).stdout
            open(fn, 'wb').write(data)
        else:
            vs = spec.get('stimme_einstellungen', {'stability': 0.4, 'similarity_boost': 0.8, 'style': 0.35, 'use_speaker_boost': True})
            body = {'text': text, 'model_id': spec.get('modell', 'eleven_multilingual_v2'), 'voice_settings': {**vs, **({'speed': spec['tempo']} if spec.get('tempo') else {})}}
            req = urllib.request.Request(f'{API}/text-to-speech/{voice_id(v)}?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                         headers={'Content-Type': 'application/json'})
            open(fn, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
        print('  Stimme:', who_now, '–', text)
    a = load_wav(fn)
    if spec.get('tempo') and prov == 'gemini' and spec['tempo'] != 1:
        a = load_wav_tempo(fn, spec['tempo'])
    # Stille am Anfang/Ende abschneiden
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz): a = a[max(0, nz[0] - 600): nz[-1] + 1500]
    return kurze_pausen(a, story.get('max_pause', 0.45))


def kurze_pausen(a, maxp):
    """lange Sprechpausen innerhalb eines Satzes auf maxp Sekunden kürzen"""
    hop = int(0.02 * SR); n = len(a) // hop
    if n < 3: return a
    rms = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, 1)); quiet = rms < max(0.004, rms.max() * 0.03)
    keep = np.ones(len(a), bool); i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * hop > maxp * SR: keep[(i * hop + int(maxp * SR / 2)):(j * hop - int(maxp * SR / 2))] = False
            i = j
        else: i += 1
    return a[keep]


def load_wav_tempo(fn, tempo):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-filter:a', f'atempo={tempo}', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def chunks(text, maxlen=28):
    """Untertitel in kurze Häppchen teilen (an Satzzeichen bevorzugt)."""
    words = text.split(); res = []; cur = ''
    for w in words:
        n = (cur + ' ' + w).strip()
        if len(n) > maxlen and cur: res.append(cur); cur = w
        else: cur = n
        if cur.endswith(('.', '!', '?', '…')) and len(cur) > maxlen * 0.55: res.append(cur); cur = ''
    if cur: res.append(cur)
    return res


def envelope(a, n):
    hop = SR / FPS; env = []
    for i in range(n):
        s = a[int(i * hop): int((i + 1) * hop)]
        env.append(float(np.sqrt(np.mean(s ** 2))) if len(s) else 0.0)
    env = np.array(env)
    ref = np.percentile(env, 90) if env.max() > 0 else 1
    env = np.clip(env / (ref + 1e-6), 0, 1.2)
    # leicht glätten, damit der Mund nicht flackert
    env = np.convolve(env, [0.25, 0.5, 0.25], mode='same')
    return [round(float(x), 3) for x in env]


cast = story.get('cast', {})
who_now = ''
t = 0.0; beats = []; lines = []; voice = []
for b in story['beats']:
    b = dict(b); b['t0'] = round(t, 3)
    dur = float(b.get('dauer', 0))
    if b.get('sagt'):
        who = b.get('wer', 'ich'); spec = cast.get(who, {})
        start = t + b.get('pause_vor', 0.12)
        if NO_TTS or not spec.get('stimme'):
            n = max(0.9, len(b['sagt']) * 0.065); a = None
        else:
            who_now = who; a = tts(b['sagt'], spec, b.get('wie')); n = len(a) / SR; voice.append((start, a, b.get('lautstaerke', 1.0), 'funk' if b.get('funk') else b.get('telefon', False)))
        parts = chunks(b['sagt']); L = [len(p) + 4 for p in parts]; ct = start; caps = []
        for p, l in zip(parts, L):
            d = n * l / sum(L); caps.append({'text': p, 't0': round(ct, 3), 't1': round(ct + d + (0.25 if p == parts[-1] else 0), 3)}); ct += d
        nf = int(n * FPS) + 1
        env = envelope(a, nf) if a is not None else [round(0.5 + 0.4 * np.sin(i * 1.7), 3) for i in range(nf)]
        lines.append({'who': who, 't0': round(start, 3), 't1': round(start + n, 3), 'caps': caps, 'env': env, 'color': b.get('farbe')})
        dur = max(dur, (start - t) + n + b.get('pause', 0.3))
    # Hintergrund-Sätze: laufen parallel (ohne Einfluss aufs Timing), standardmäßig ohne Untertitel
    for h in b.get('hintergrund', []):
        hs = cast.get(h['wer'], {}); st = t + h.get('ab', 0)
        if NO_TTS or not hs.get('stimme'): continue
        who_now = h['wer']; a = tts(h['sagt'], hs, h.get('wie')); n = len(a) / SR
        voice.append((st, a, h.get('lautstaerke', 0.4), 'funk' if h.get('funk') else h.get('telefon', False)))
        caps = [{'text': p, 't0': round(st, 3), 't1': round(st + n, 3)} for p in [h['sagt']]] if h.get('untertitel') else []
        lines.append({'who': h['wer'], 't0': round(st, 3), 't1': round(st + n, 3), 'caps': caps, 'env': envelope(a, int(n * FPS) + 1), 'color': h.get('farbe'), 'bg': True})
    if dur <= 0: dur = 1.5
    t += dur; b['t1'] = round(t, 3); beats.append(b)
total = t + story.get('nachlauf', 0.5)

# ---------- Ton mischen (Stereo) ----------
def load_st(fn):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def mavg(x, k):
    """schneller gleitender Mittelwert (zentriert)"""
    k = max(1, int(k)); c = np.cumsum(np.concatenate([np.zeros(k // 2 + 1), x, np.zeros(k - k // 2)]))
    return ((c[k:] - c[:-k]) / k)[:len(x)]

def telefon(a):
    """Stimme klingt wie durchs Handy: Bandpass 300-3400 Hz + leichte Verzerrung"""
    from scipy import signal
    sos = signal.butter(4, [350, 2900], 'bandpass', fs=SR, output='sos')
    y = signal.sosfilt(sos, a) * 2.0
    return np.tanh(y * 1.15) / 1.15

def sprache(a):
    """Stimme aufbereiten: Low-Cut gegen Brummen + sanfter Kompressor für gleichmäßige Lautstärke"""
    from scipy import signal
    a = signal.sosfilt(signal.butter(2, 95, 'highpass', fs=SR, output='sos'), a)
    k = int(0.03 * SR); env = np.sqrt(np.maximum(mavg(a ** 2, k), 0)) + 1e-6
    thr = 0.08; g = np.where(env > thr, (thr / env) ** 0.45, 1.0)
    g = mavg(g, k)
    y = a * g; return y / (np.abs(y).max() + 1e-9) * 0.8

def gain_curve(points, n, ramp=1.2):
    """points: [(zeit, wert)] -> Lautstärkekurve mit weichen Übergängen"""
    g = np.zeros(n, np.float32); cur = 0.0; last = 0
    for t0, v in sorted(points):
        i = min(n, int(t0 * SR)); g[last:i] = cur
        r = min(n, i + int(ramp * SR)); g[i:r] = np.linspace(cur, v, r - i, endpoint=False) if r > i else v; cur = v; last = r
    g[last:] = cur; return g

N = int((total + 1) * SR)
sfxdir = os.path.join(ROOT, 'sfx')
voc = np.zeros(N, np.float32)
for st, a, vol, tel in voice:
    a = sprache(a) * story.get('stimme_lautstaerke', 1.0)
    if tel: a = telefon(a) * 0.9
    if tel == 'funk':  # Funkgerät: Knacken vorne/hinten + Rauschen
        kn = load_wav(os.path.join(ROOT, 'sfx', 'funk_knacken.wav')) * 0.5
        a = np.concatenate([kn, a + np.random.default_rng(1).standard_normal(len(a)) * 0.02, kn])
    i = int(st * SR); voc[i:i + len(a)] += a[:N - i] * vol
mix = np.stack([voc, voc], 1)

# Atmo-Spuren: laufen durch, Lautstärke pro Beat über "atmo": {"datei": wert} änderbar
spuren = story.get('atmo_spuren', [])
for sp in spuren:
    fn = os.path.join(sfxdir, sp['datei'])
    if not os.path.exists(fn): print('  (Atmo fehlt:', sp['datei'], ')'); continue
    a = load_st(fn); reps = int(np.ceil(N / len(a))); a = np.tile(a, (reps, 1))[:N]
    pts = [(0, sp.get('lautstaerke', 0.3))] + [(bb['t0'] + bb.get('atmo_ab', 0), bb['atmo'][sp['datei']]) for bb in beats if sp['datei'] in bb.get('atmo', {})]
    g = gain_curve(pts, N, sp.get('rampe', 1.5)); g[:int(1.0 * SR)] *= np.linspace(0, 1, int(1.0 * SR))
    mix += a * g[:, None]

# Musik: "musik": {"datei", "lautstaerke", "einblenden"} startet ab dem Beat (Kreuzblende), "musik": null stoppt
mus_ev = [(bb['t0'], bb['musik']) for bb in beats if 'musik' in bb]
music = np.zeros((N, 2), np.float32)
for k, (t0, m) in enumerate(mus_ev):
    if not m: continue
    t1 = mus_ev[k + 1][0] if k + 1 < len(mus_ev) else total + 1
    fi, fo = m.get('einblenden', 2.0), m.get('ausblenden', 2.5)
    fn = os.path.join(sfxdir, m['datei'])
    if not os.path.exists(fn): print('  (Musik fehlt:', m['datei'], ')'); continue
    a = load_st(fn)[int(m.get('start', 0) * SR):]
    i0 = int(t0 * SR); i1 = min(N, int((t1 + fo) * SR)); L = i1 - i0
    if len(a) < L:  # verlängern: Ende in den Anfang überblenden
        xf = int(3 * SR); b2 = a.copy()
        while len(b2) < L:
            w = np.linspace(0, 1, xf)[:, None]; seam = b2[-xf:] * (1 - w) + a[:xf] * w
            b2 = np.concatenate([b2[:-xf], seam, a[xf:]])
        a = b2
    seg = a[:L] * m.get('lautstaerke', 0.25)
    env = np.ones(L); nfi = min(L, int(fi * SR)); env[:nfi] = np.linspace(0, 1, nfi)
    nfo = min(L, int(fo * SR)); env[-nfo:] = np.minimum(env[-nfo:], np.linspace(1, 0, nfo))
    music[i0:i1] += seg * env[:, None]
# Ducking: Musik unter Sprache leiser
vabs = np.abs(voc); k = int(0.05 * SR)
vl = mavg(vabs, k); vl = mavg((vl > 0.02).astype(np.float32), 0.4 * SR)
duck = 1 - story.get('ducking', 0.6) * np.clip(vl, 0, 1)
mix += music * duck[:, None]

for bb in beats:
    for s in ([bb['sfx']] if isinstance(bb.get('sfx'), (str, dict)) else bb.get('sfx', [])):
        s = {'datei': s} if isinstance(s, str) else s
        fn = os.path.join(sfxdir, s['datei'])
        if not os.path.exists(fn): print('  (Geräusch fehlt:', s['datei'], ')'); continue
        a = load_st(fn) * s.get('lautstaerke', 0.6)
        if s.get('dauer'):
            a = a[:int(s['dauer'] * SR)].copy(); f = min(len(a), int(0.4 * SR)); a[-f:] *= np.linspace(1, 0, f)[:, None]
        i = int((bb['t0'] + s.get('ab', 0)) * SR)
        if i < 0: a = a[-i:]; i = 0
        mix[i:i + len(a)] += a[:N - i]
for bb in beats:
    for au in ([bb['auto']] if isinstance(bb.get('auto'), dict) else bb.get('auto', [])):
        a = load_st(os.path.join(sfxdir, 'auto_vorbei.wav')) * au.get('lautstaerke', 0.45)
        if au.get('spur', 1) == 2: a = a[:, ::-1]
        i = int((bb['t0'] + au.get('ab', 0) - 3.5) * SR)
        if i < 0: a = a[-i:]; i = 0
        mix[i:i + len(a)] += a[:N - i]
# sanfter Limiter
peak = np.abs(mix).max()
mix = np.tanh(mix / max(peak, 1e-6) * 1.6) / np.tanh(1.6) * 0.93 if peak > 0.9 else mix
pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', os.path.join(out, 'mix.wav')], input=pcm, check=True)

story_out = {k: v for k, v in story.items() if k != 'beats'}
json.dump({'fps': FPS, 'total': round(total, 3), 'story': story_out, 'beats': beats, 'lines': lines}, open(os.path.join(out, 'timeline.json'), 'w'), ensure_ascii=False)
print(f'{name}: {total:.1f}s, {len(beats)} Beats, {len(lines)} Sätze -> build/{name}/')
