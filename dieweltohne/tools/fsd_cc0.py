"""Suche und Export in der CC0-Teilmenge von FSD50K (echte Freesound-Aufnahmen, Lizenz CC0).

Datensatz: Hugging Face "Atotti/fsd50k-cc0-Qwen3-Omni-captioned" + FSD50K-Labels (labels/dev.csv, eval.csv).
Erwartet die Dateien in $FSD_DIR (Standard /home/user/fsd_cc0), siehe Kommentar unten zum Laden.

  python3 fsd_cc0.py search LABEL[,LABEL2] [stichwort,stichwort] [anzahl]
  python3 fsd_cc0.py get NAME ziel.wav
"""
import io
import json
import os
import subprocess
import sys

DIR = os.environ.get('FSD_DIR', '/home/user/fsd_cc0')


def index():
    return json.load(open(os.path.join(DIR, 'index.json')))


def search(labels, kws, n=10):
    labs = [l for l in labels.split(',') if l]
    kws = [k.lower() for k in kws.split(',') if k]
    out = []
    for r in index():
        rl = r['labels'].split(',')
        if labs and not all(l in rl for l in labs):
            continue
        cap = r['caption'].lower()
        head = cap[:600]
        score = sum(3 if k in head else (1 if k in cap else 0) for k in kws)
        if kws and score == 0:
            continue
        out.append((score, r))
    out.sort(key=lambda x: -x[0])
    return out[:n]


def get(name, dest):
    import pyarrow.parquet as pq
    r = next(x for x in index() if x['name'] == name)
    pf = pq.ParquetFile(os.path.join(DIR, f"train-0000{r['shard']}-of-00003.parquet"))
    row = r['row']
    for g in range(pf.num_row_groups):
        n = pf.metadata.row_group(g).num_rows
        if row < n:
            t = pf.read_row_group(g, columns=['name', 'audio'])
            assert t['name'][row].as_py() == name
            data = t['audio'][row].as_py()['bytes']
            break
        row -= n
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '-', '-ac', '2', '-ar', '48000', dest], input=data, check=True)
    return r


if __name__ == '__main__':
    if sys.argv[1] == 'search':
        for s, r in search(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '', int(sys.argv[4]) if len(sys.argv) > 4 else 10):
            print(f"[{s}] {r['name']:>7} | {r['labels'][:60]}\n        {r['caption'][:260].replace(chr(10), ' ')}")
    else:
        r = get(sys.argv[2], sys.argv[3]); print('ok', r['name'], r['labels'])
