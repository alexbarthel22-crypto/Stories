"""python transcribe.py prefix -> prefix_words.json"""
import json, subprocess, sys, os
os.environ['HF_HUB_DISABLE_XET'] = '1'
import numpy as np
from faster_whisper import WhisperModel
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1] + '.wav', '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.float32)
m = WhisperModel('small', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language='de', word_timestamps=True)
ws = [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for s in segs for w in s.words]
json.dump(ws, open(sys.argv[1] + '_words.json', 'w'), ensure_ascii=False)
print(' '.join(f'{w[0]}@{w[1]:.1f}' for w in ws))
