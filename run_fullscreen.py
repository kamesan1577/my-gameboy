import sys
import importlib.util
import pyxel

_original_run = pyxel.run

def _patched_run(update, draw):
    pyxel.fullscreen(True)
    _original_run(update, draw)

pyxel.run = _patched_run

path = sys.argv[1]
spec = importlib.util.spec_from_file_location("game", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
