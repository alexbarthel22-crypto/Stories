"""Mischt Video + Stimme + Meeresrauschen + Sound-Effekte + Musik (Musik duckt unter der Stimme).
Aufruf: python3 mix.py <jpg-ordner> <ausgabe.mp4>"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
frames, out = sys.argv[1], sys.argv[2]
tl = json.loads((HERE / "timeline.json").read_text())
dur = tl["duration"] + 0.8
music = HERE / "../../sounds/clara_theme.wav"
subprocess.run(["python3", str(HERE / "../../sounds/make_music.py"), str(dur + 1), str(music)], check=True, capture_output=True)

inputs = ["-framerate", "25", "-i", f"{frames}/f%05d.jpg", "-i", "voice.wav",
          "-f", "lavfi", "-i", "anoisesrc=color=brown:amplitude=0.5:sample_rate=44100,lowpass=f=900,"
                               "volume='0.08+0.05*sin(2*PI*t/5)':eval=frame",
          "-i", str(music)]
filt = ["[1:a]aresample=44100,apad,asplit=2[v][vsc]",
        # Musik: hörbar, aber deutlich leiser; duckt zusätzlich, sobald Clara spricht
        "[3:a]volume=0.13[mus]",
        "[mus][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350:makeup=1[md]"]
mix, n = ["[v]", "[2:a]", "[md]"], 3
for sfx in tl.get("sfx", []):
    n += 1
    inputs += ["-i", sfx["file"]]
    ln = sfx["to"] - sfx["from"]
    ms = int(sfx["at"] * 1000)
    # weich rein/raus + kurzer Nachhall -> klingt nicht „eingefügt“
    filt.append(f"[{n}:a]atrim={sfx['from']}:{sfx['to']},asetpts=PTS-STARTPTS,aresample=44100,"
                f"afade=t=in:d=0.04,afade=t=out:st={ln-0.28:.2f}:d=0.28,"
                f"aecho=0.8:0.6:70|140:0.25|0.12,adelay={ms}|{ms},volume=1.2[s{n}]")
    mix.append(f"[s{n}]")
filt.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,volume=0.9,atrim=0:{dur}[a]")
cmd = ["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(filt),
       "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-t", str(dur), "-movflags", "+faststart", out]
subprocess.run(cmd, check=True, cwd=HERE)
print("fertig:", out)
