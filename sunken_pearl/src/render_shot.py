import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import reset, render_settings
import shots
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
name, mode = argv[0], argv[1]
OUT = os.environ.get('SP_OUT', '/home/user/Stories/sunken_pearl/frames')
reset()
up = shots.SHOTS[name]()
t0, t1 = shots.shot_range(name)
sc = bpy.context.scene
if mode == 'preview':
    render_settings(270, 480, 6, bounces=3)
    sc.cycles.diffuse_bounces = 1; sc.cycles.glossy_bounces = 1
    d = OUT + '/preview'; os.makedirs(d, exist_ok=True)
    fr = [float(x) for x in argv[2:]] if len(argv) > 2 else [0.0, 0.5, 0.98]
    for k in fr:
        t = (t1 - t0) * k
        up(t)
        sc.render.filepath = f'{d}/{name}_{int(k*100):02d}.png'
        bpy.ops.render.render(write_still=True)
else:
    render_settings(540, 960, int(os.environ.get('SP_SPP', 8)), bounces=3)
    sc.cycles.diffuse_bounces = 1; sc.cycles.glossy_bounces = 1
    d = f'{OUT}/{name}'; os.makedirs(d, exist_ok=True)
    g0, g1 = round(t0 * shots.FPS), round(t1 * shots.FPS)
    for g in range(g0, g1):
        fn = f'{d}/f{g:04d}.png'
        if os.path.exists(fn):
            continue
        t = g / shots.FPS - t0
        up(t)
        sc.render.filepath = fn
        st = time.time()
        bpy.ops.render.render(write_still=True)
        print(f'FRAME {name} {g} {time.time()-st:.1f}s', flush=True)
print('DONE', name, flush=True)
