"""Lädt alle Einträge aus sfx_list.txt (name|File:Titel) von Wikimedia Commons."""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import commons_sfx as C

lst, out = sys.argv[1], sys.argv[2]
for line in open(lst):
    if not line.strip(): continue
    name, title = line.strip().split('|', 1)
    if os.path.exists(f"{out}/{name}.wav"): continue
    try:
        meta = C.info([title])
        if not meta:  # Titel war gekürzt: über die Suche auflösen
            pref = title[5:60]
            hits = [m for m in C.search(pref, 10) if m['title'].startswith(title[:60])]
            if not hits: print('NICHT GEFUNDEN', name, title); continue
            title = hits[0]['title']
        C.get(title, f"{out}/{name}")
    except Exception as e:
        print('FEHLER', name, e)
    time.sleep(8)
