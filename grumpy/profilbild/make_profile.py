"""TikTok-Profilbild von Clara: genervt auf der Insel (quadratisch, Gesicht mittig für den runden Zuschnitt).
Aufruf: python3 make_profile.py [zoom] [x] [y]"""
import importlib.util, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
zoom, cx, cy = (float(a) for a in (sys.argv[1:4] if len(sys.argv) > 3 else (2.4, 560, 1050)))
tmp = Path(tempfile.mkdtemp())
sys.argv = ["make_video.py", str(tmp)]
spec = importlib.util.spec_from_file_location("mv", HERE / "../videos/folge01/make_video.py")
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)

SIZE = 1080
svg = mv.scene(3.0, profile=(zoom, cx, cy, SIZE))
(HERE / "profilbild.svg").write_text(svg)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:{SIZE},height:{SIZE}}},deviceScaleFactor:1}});
await p.goto('file://{(HERE / "profilbild.svg").resolve()}');await p.screenshot({{path:'{(HERE / "profilbild.png").resolve()}'}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("profilbild.png geschrieben")
