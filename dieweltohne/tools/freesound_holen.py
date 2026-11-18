"""Lädt echte Geräusche von Freesound (nur CC0-Lizenz) und packt sie in eine ZIP-Datei.

Auf deinem eigenen Computer ausführen (Freesound sperrt Cloud-Server):
    python freesound_holen.py
Das Skript fragt nach deinem API-Schlüssel ("Client secret/Api key").
Ergebnis: die_welt_ohne_geraeusche.zip im selben Ordner -> im Chat hochladen.
Braucht nur Python 3, keine Zusatzpakete.
"""
import getpass
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import zipfile

# Name -> (Suchbegriff, minimale Dauer, maximale Dauer)
SOUNDS = {
    "rain_street":      ("rain city street", 30, 900),
    "rain_close":       ("rain on window glass close", 10, 600),
    "city_traffic":     ("city traffic ambience", 30, 900),
    "car_pass_wet":     ("car passing wet road", 3, 40),
    "clock_tick":       ("clock ticking", 5, 120),
    "thunder":          ("thunder clap close", 3, 60),
    "boom":             ("deep boom impact", 1, 15),
    "whoosh":           ("whoosh", 0.3, 4),
    "tire_screech":     ("tire screech", 1, 20),
    "metal_scrape":     ("metal scraping asphalt", 2, 40),
    "metal_grind":      ("metal grinding", 2, 40),
    "sparks":           ("angle grinder sparks", 2, 40),
    "car_crash":        ("car crash", 1, 20),
    "glass_break":      ("glass shatter", 0.5, 10),
    "electric_buzz":    ("electric buzz short circuit", 1, 20),
    "footsteps_wet":    ("footsteps wet pavement", 3, 60),
    "body_fall":        ("body fall", 0.3, 5),
    "crowd_gasp":       ("crowd gasp", 0.5, 10),
    "crowd_laugh":      ("crowd laughing", 2, 30),
    "crowd_street":     ("crowd street murmur", 10, 600),
    "balloon_deflate":  ("balloon deflate", 0.5, 10),
    "water_spray":      ("pipe burst water spray", 3, 60),
    "water_gush":       ("water gushing", 3, 60),
    "water_splash":     ("water splash floor", 1, 20),
    "plane_landing":    ("airplane landing", 10, 180),
    "jet_engine":       ("jet engine", 5, 120),
    "siren_martinshorn": ("martinshorn", 5, 90),
    "siren_ambulance":  ("ambulance siren", 5, 90),
    "car_horn":         ("car horn", 0.5, 10),
    "traffic_horns":    ("traffic jam horns", 5, 90),
    "candy_bag":        ("candy bag crinkle", 1, 20),
}
PER_QUERY = 3  # Treffer pro Geräusch, damit beim Mischen die Wahl bleibt
API = "https://freesound.org/apiv2/search/text/"


def get_json(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Token " + token, "User-Agent": "DieWeltOhne/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def main():
    token = getpass.getpass("Freesound API-Schlüssel (Eingabe bleibt unsichtbar): ").strip()
    out = "die_welt_ohne_geraeusche"
    os.makedirs(out, exist_ok=True)
    credits = []
    for name, (query, dmin, dmax) in SOUNDS.items():
        params = {
            "query": query,
            "filter": f'license:"Creative Commons 0" duration:[{dmin} TO {dmax}]',
            "sort": "rating_desc",
            "fields": "id,name,username,license,duration,previews,url",
            "page_size": PER_QUERY,
        }
        try:
            res = get_json(API + "?" + urllib.parse.urlencode(params), token)["results"]
        except Exception as e:
            print("FEHLER bei", name, e)
            if "401" in str(e):
                sys.exit("Der Schlüssel wurde abgelehnt. Bitte den Wert aus 'Client secret/Api key' nehmen.")
            continue
        if not res:
            print("nichts gefunden:", name)
        for i, s in enumerate(res, 1):
            fn = f"{name}_{i}.mp3"
            try:
                urllib.request.urlretrieve(s["previews"]["preview-hq-mp3"], os.path.join(out, fn))
                credits.append({"file": fn, "id": s["id"], "name": s["name"], "user": s["username"],
                                "license": s["license"], "duration": s["duration"], "url": s["url"]})
                print("ok", fn, "-", s["name"][:50])
            except Exception as e:
                print("FEHLER beim Laden", fn, e)
            time.sleep(0.3)
    with open(os.path.join(out, "quellen.json"), "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=1)
    zname = out + ".zip"
    with zipfile.ZipFile(zname, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(out):
            z.write(os.path.join(out, fn), fn)
    print(f"\nFertig: {len(credits)} Geräusche in {zname}. Diese Datei im Chat hochladen.")
    input("Enter drücken zum Beenden ...")


if __name__ == "__main__":
    main()
