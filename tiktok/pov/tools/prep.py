#!/usr/bin/env python3
"""Bereitet eine Story fürs Rendern vor.

  python3 tools/prep.py stories/<name>.json [--ohne-stimmen]

- erzeugt die Stimmen mit Gemini-TTS (oder ElevenLabs), zwischengespeichert: nur neue/geänderte Sätze werden neu erzeugt
- berechnet das Timing jedes Beats, Untertitel-Häppchen und die Mundbewegung (Lautstärke pro Frame)
- mischt Stimmen + Atmo + Geräusche zu build/<name>/mix.wav
- schreibt build/<name>/timeline.json für die Render-Engine
"""
import base64, hashlib, json, os, re, subprocess, sys, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
args = [a for a in sys.argv[1:] if not a.startswith('--')]
NO_TTS = '--ohne-stimmen' in sys.argv
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
    if not os.path.exists(fn):
        if prov == 'gemini':
            # kurzes Format, sonst liest Gemini die Anweisung mit vor
            prompt = (f"### DIRECTOR'S NOTES\nStyle: {regie}. Speak only the transcript, in German.\n\n### TRANSCRIPT\n{text}"
                      if regie else f"### DIRECTOR'S NOTES\nSpeak only the transcript, in German.\n\n### TRANSCRIPT\n{text}")
            body = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseModalities': ['AUDIO'],
                    'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': v}}}}}
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{spec.get("modell", "gemini-3.8-flash-tts")}:generateContent',
                data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': os.environ['GEMINI_API_KEY']})
            r = json.load(urllib.request.urlopen(req, timeout=300))
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
    return a


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
            who_now = who; a = tts(b['sagt'], spec, b.get('wie')); n = len(a) / SR; voice.append((start, a, b.get('lautstaerke', 1.0)))
        parts = chunks(b['sagt']); L = [len(p) + 4 for p in parts]; ct = start; caps = []
        for p, l in zip(parts, L):
            d = n * l / sum(L); caps.append({'text': p, 't0': round(ct, 3), 't1': round(ct + d + (0.25 if p == parts[-1] else 0), 3)}); ct += d
        nf = int(n * FPS) + 1
        env = envelope(a, nf) if a is not None else [round(0.5 + 0.4 * np.sin(i * 1.7), 3) for i in range(nf)]
        lines.append({'who': who, 't0': round(start, 3), 't1': round(start + n, 3), 'caps': caps, 'env': env, 'color': b.get('farbe')})
        dur = max(dur, (start - t) + n + b.get('pause', 0.3))
    if dur <= 0: dur = 1.5
    t += dur; b['t1'] = round(t, 3); beats.append(b)
total = t + story.get('nachlauf', 0.5)

# ---------- Ton mischen ----------
N = int((total + 1) * SR)
mix = np.zeros(N, np.float32)
for st, a, vol in voice:
    i = int(st * SR); mix[i:i + len(a)] += a[:N - i] * vol
rng = np.random.default_rng(1)
amb = story.get('atmo', 'stadt')
if amb:
    # Wind/Stadtrauschen: gefiltertes braunes Rauschen + langsames Pulsieren
    w = np.cumsum(rng.standard_normal(N).astype(np.float32)); w -= np.convolve(w, np.ones(4410) / 4410, mode='same'); w /= np.abs(w).max() + 1e-9
    lfo = 0.6 + 0.4 * np.sin(np.arange(N) / SR * 0.35)
    mix += w * lfo * story.get('atmo_lautstaerke', 0.05)
sfxdir = os.path.join(ROOT, 'sfx')
for b in beats:
    for s in ([b['sfx']] if isinstance(b.get('sfx'), (str, dict)) else b.get('sfx', [])):
        s = {'datei': s} if isinstance(s, str) else s
        fn = os.path.join(sfxdir, s['datei'])
        if not os.path.exists(fn): print('  (Geräusch fehlt:', s['datei'], ')'); continue
        a = load_wav(fn) * s.get('lautstaerke', 0.6); i = int((b['t0'] + s.get('ab', 0)) * SR); mix[i:i + len(a)] += a[:N - i]
peak = np.abs(mix).max()
if peak > 0.95: mix *= 0.95 / peak
pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', os.path.join(out, 'mix.wav')], input=pcm, check=True)

story_out = {k: v for k, v in story.items() if k != 'beats'}
json.dump({'fps': FPS, 'total': round(total, 3), 'story': story_out, 'beats': beats, 'lines': lines}, open(os.path.join(out, 'timeline.json'), 'w'), ensure_ascii=False)
print(f'{name}: {total:.1f}s, {len(beats)} Beats, {len(lines)} Sätze -> build/{name}/')
