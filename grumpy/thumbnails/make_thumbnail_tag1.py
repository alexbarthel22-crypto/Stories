"""Thumbnail Tag 1 (9:16): Clara genervt auf der Insel + sarkastischer Titel.
Text liegt im mittleren 3:4-Bereich (TikTok-Profilraster) und in der Sicherheitszone."""
import importlib.util, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.argv = ["make_video.py", tempfile.mkdtemp()]
spec = importlib.util.spec_from_file_location("mv", HERE / "../videos/folge01/make_video.py")
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)

W, H = 1080, 1920
scene = mv.scene(3.0, profile=(1.75, 560, 1005, W, H))
inner = scene[scene.index(">") + 1: scene.rindex("</svg>")]
F = 'font-family="DejaVu Sans, Noto Color Emoji, sans-serif" font-weight="900" text-anchor="middle"'
overlay = f'''
<defs><filter id="sh" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="0" flood-color="#000" flood-opacity="1"/></filter></defs>
<g filter="url(#sh)">
  <rect x="330" y="300" width="420" height="96" rx="48" fill="#E8102E"/>
  <text x="540" y="368" {F} font-size="58" fill="#FFFFFF" letter-spacing="3">TAG 1</text>
  <text x="540" y="545" {F} font-size="150" fill="#FFE600" stroke="#111" stroke-width="20" stroke-linejoin="round" paint-order="stroke">LÄUFT</text>
  <text x="540" y="700" {F} font-size="150" fill="#FFE600" stroke="#111" stroke-width="20" stroke-linejoin="round" paint-order="stroke">BEI MIR.</text>
  <text x="540" y="800" {F} font-size="58" fill="#FFFFFF" stroke="#111" stroke-width="12" stroke-linejoin="round" paint-order="stroke">Rave → Insel 🙃</text>
</g>
<g {F}>
  <text x="540" y="1650" font-size="52" fill="#FFFFFF" stroke="#111" stroke-width="11" stroke-linejoin="round" paint-order="stroke">Ihr entscheidet, was ich mache 👇</text>
</g>'''
svg = scene[: scene.rindex("</svg>")] + overlay + "</svg>"
(HERE / "tag1_thumbnail.svg").write_text(svg)
out = (HERE / "tag1_thumbnail.png").resolve()
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});await p.goto('file://{(HERE / "tag1_thumbnail.svg").resolve()}');
await p.screenshot({{path:'{out}'}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print(out)
