"""Sucht echte Tonaufnahmen auf Wikimedia Commons und zeigt Lizenz, Autor und Dauer.

Aufruf:
  python3 commons_sfx.py search "tire screech" [n]
  python3 commons_sfx.py get "File:Name.ogg" zielordner/name
"""
import json
import os
import urllib.error
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "SoundFetcher/1.0 (generic research client)"


def api(params):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    err = None
    for attempt in range(8):
        try:
            time.sleep(1.5)
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            r = json.load(urllib.request.urlopen(req, timeout=30))
            if "error" in r:
                raise RuntimeError(r["error"])
            return r
        except Exception as e:  # Ratenlimit: warten und erneut versuchen
            time.sleep(5 + attempt * 6)
            err = e
    raise err


def clean(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def info(titles):
    r = api({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
             "iiprop": "url|size|extmetadata|mediatype|metadata"})
    out = []
    for p in r["query"]["pages"].values():
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mediatype") != "AUDIO":
            continue
        md = ii.get("extmetadata", {})
        length = None
        for m in ii.get("metadata") or []:
            if m.get("name") in ("length", "playtime_seconds"):
                length = m.get("value")
        out.append({
            "title": p["title"], "url": ii.get("url"), "size": ii.get("size"),
            "license": clean(md.get("LicenseShortName", {}).get("value")),
            "artist": clean(md.get("Artist", {}).get("value"))[:60],
            "length": length,
        })
    return out


def search(q, n=12):
    r = api({"action": "query", "list": "search", "srsearch": q + " filetype:audio",
             "srnamespace": 6, "srlimit": n})
    titles = [x["title"] for x in r["query"]["search"]]
    return info(titles) if titles else []


def get(title, dest):
    meta = info([title])[0]
    url = meta["url"].split("?")[0]
    raw = dest + ".orig"
    for attempt in range(8):  # Datei-Server drosselt: geduldig wiederholen
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=180).read()
            break
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(20 + attempt * 20)
    else:
        raise RuntimeError("429 dauerhaft")
    with open(raw, "wb") as f:
        f.write(data)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ac", "2", "-ar", "48000", dest + ".wav"], check=True)
    os.remove(raw)
    with open(dest + ".json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print("ok", dest, meta["license"], meta["artist"], flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for m in search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12):
            L = m["length"]
            L = f"{float(L):6.1f}s" if L else "   ?  "
            print(f"{L} {m['size']//1024:6d}KB {m['license'][:14]:14s} {m['title'][5:70]}")
    else:
        get(sys.argv[2], sys.argv[3])
