import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, math
from lib import *
from sets import fog_all
from sets_lux import *
from shelly import Shelly
R = math.radians
argv = sys.argv[sys.argv.index('--') + 1:]
reset()
world((0.02, 0.06, 0.08), 1.0)
A = LuxApartment()
sh = Shelly()
c = A.chair
sh.pose({'root_loc': (c.location.x, c.location.y, 0.0), 'root_rot': (0, 0, math.degrees(c.rotation_euler.z)),
         'hips_loc': (0, 0.02, 0.5), 'hipL': (-84, 0, -6), 'hipR': (-84, 0, 6), 'kneeL': (88, 0, 0), 'kneeR': (88, 0, 0),
         'spine': (-6, 0, 0), 'shoulderL': (-25, -18, 0), 'shoulderR': (-25, 18, 0), 'elbowL': (-55, 0, 10), 'elbowR': (-55, 0, -10), 'fingers': 0.4})
fog_all(0.05, (0.02, 0.2, 0.28), skip=set(m.name for m in D.materials) - set(A.out_mats))
for s_ in A.schools: s_.update(2.0)
cam = camera(lens=24)
bpy.context.scene.view_settings.exposure = float(os.environ.get('EXPO', '-0.8'))
render_settings(270, 480, int(argv[0]) if argv else 8, bounces=3)
sc = bpy.context.scene; sc.cycles.diffuse_bounces = 1; sc.cycles.glossy_bounces = 1
d = '/home/user/Stories/sunken_pearl/frames/test'
for nm, loc, tgt, lens in [('wide', (3.6, -3.6, 1.7), (-0.8, 1.6, 1.3), 20), ('win', (0.4, -2.5, 1.3), (0, 3.6, 1.7), 22),
                           ('chand', (1.4, -2.2, 2.2), (0.3, -0.4, 2.9), 40), ('sofa', (0.6, -0.6, 1.2), (-1.35, 0.9, 0.9), 30),
                           ('back', (-2.0, 2.6, 1.6), (2.0, -3.0, 1.2), 20), ('reef', (0.6, 2.6, 1.5), (0.0, 12, 0.6), 24)]:
    cam.location = loc; look_at(cam, tgt); cam.data.lens = lens
    sc.render.filepath = f'{d}/lux_{nm}.png'
    bpy.ops.render.render(write_still=True)
