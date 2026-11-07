"""Visuals über den Baukasten (tools/kit.py)."""
from kit import *
import importlib.util, os
_sp = importlib.util.spec_from_file_location("_s", os.path.join(os.path.dirname(__file__), "script.py"))
_s = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_s)
INTRO, draw_intro = make_intro(dict(_s.INTRO_CFG, spec=_s.AL))
SCENE_DRAW = make_scenes(_s.SCENES, _s.AL)
