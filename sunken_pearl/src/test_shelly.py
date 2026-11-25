import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, math
from lib import *
from shelly import Shelly
R = math.radians
outfit = sys.argv[sys.argv.index('--') + 1]
reset()
world((0.25, 0.22, 0.25), 1.0)
sh = Shelly(outfit=outfit)
sh.pose({'shoulderL': (0, -10, 0), 'shoulderR': (0, 10, 0), 'neck': (0, 0, 0)})
sh.set_face(sys.argv[-1] if len(sys.argv) > sys.argv.index('--') + 2 else 'smile', look=(0, 0))
prim('plane', 'fl', (0, 0, 0), scale=(10, 10, 1), mat=principled('flm', (0.5, 0.45, 0.45), 0.6))
k = add_light('AREA', 'key', (-1.5, -2.5, 2.5), 300, (1, 0.95, 0.9), 1.5); look_at(k, (0, 0, 1.3))
f = add_light('AREA', 'fill', (2, -2, 1.5), 100, (0.8, 0.9, 1.0), 2.0); look_at(f, (0, 0, 1.3))
r_ = add_light('AREA', 'rim', (0.5, 2, 2.5), 200, (1, 0.9, 0.95), 1.0); look_at(r_, (0, 0, 1.4))
cam = camera(lens=35)
render_settings(540, 960, 24, bounces=4)
d = '/home/user/Stories/sunken_pearl/frames/test'; os.makedirs(d, exist_ok=True)
hw = sh.head_world()
for nm, loc, tgt, lens in [('body', (0.9, -3.6, 1.0), (0, 0, 0.85), 40), ('face', (0.15, -0.9, hw.z + 0.02), (0, 0, hw.z), 55),
                            ('face34', (-0.55, -0.7, hw.z + 0.05), (0, 0, hw.z), 55)]:
    cam.location = loc; look_at(cam, tgt); cam.data.lens = lens
    bpy.context.scene.render.filepath = f'{d}/{outfit}_{nm}.png'
    bpy.ops.render.render(write_still=True)
