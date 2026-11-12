"""Thumbnail Tag 2 (9:16) im Design von Tag 1: Clara auf der veränderten Insel + sarkastischer Titel."""
import importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.argv = ["make_video.py", tempfile.mkdtemp()]
spec = importlib.util.spec_from_file_location("v2", HERE / "../videos/folge02/make_video.py")
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)

W, H = 1080, 1920
t = v2.EV["krabbe"] + 1.0          # Vulkan, Haus, Toilette, Döner, Steg, Zelt – vor der Villa
scene = v2.scene(t, cam=(0.62, 1050, 600), hud_on=False, show_clara=False)
# Clara groß im Vordergrund (Thumbnail-Perspektive: sie steht näher an der Kamera)
clara = v2.clara(t, 0.0, False, -3.0, 0.0, False)
scene = scene[: scene.rindex("</svg>")] + (
    '<ellipse cx="540" cy="1562" rx="150" ry="22" fill="#000" opacity="0.25"/>'
    f'<g transform="translate(540 1560) scale(0.55) translate(-540 -1550)">{clara}</g>') + "</svg>"
F = 'font-family="DejaVu Sans, Noto Color Emoji, sans-serif" font-weight="900" text-anchor="middle"'
overlay = f'''
<defs><filter id="tsh" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="0" flood-color="#000" flood-opacity="1"/></filter></defs>
<g filter="url(#tsh)">
  <rect x="330" y="300" width="420" height="96" rx="48" fill="#E8102E"/>
  <text x="540" y="368" {F} font-size="58" fill="#FFFFFF" letter-spacing="3">TAG 2</text>
  <text x="540" y="545" {F} font-size="138" fill="#FFE600" stroke="#111" stroke-width="20" stroke-linejoin="round" paint-order="stroke">IHR SEID</text>
  <text x="540" y="695" {F} font-size="122" fill="#FFE600" stroke="#111" stroke-width="20" stroke-linejoin="round" paint-order="stroke">RESPEKTLOS.</text>
  <text x="540" y="795" {F} font-size="52" fill="#FFFFFF" stroke="#111" stroke-width="12" stroke-linejoin="round" paint-order="stroke">Vulkan, Tsunami, Döner 🙃</text>
</g>
<g {F}>
  <text x="540" y="1650" font-size="50" fill="#FFFFFF" stroke="#111" stroke-width="11" stroke-linejoin="round" paint-order="stroke">Alles aus euren Kommentaren 👇</text>
</g>'''
svg = scene[: scene.rindex("</svg>")] + overlay + "</svg>"
(HERE / "tag2_thumbnail.svg").write_text(svg)
out = (HERE / "tag2_thumbnail.png").resolve()
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});await p.goto('file://{(HERE / "tag2_thumbnail.svg").resolve()}');
await p.screenshot({{path:'{out}'}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print(out)
