import os
import subprocess
import sys

launcher_dir = os.path.dirname(os.path.abspath(__file__))
pending_file = os.path.join(launcher_dir, ".pending_game")
wrapper = os.path.join(launcher_dir, "run_fullscreen.py")

while True:
    if os.path.exists(pending_file):
        os.remove(pending_file)

    subprocess.run(["uv", "run", "main.py"], cwd=launcher_dir)

    if os.path.exists(pending_file):
        with open(pending_file) as f:
            game_path = f.read().strip()
        os.remove(pending_file)
        subprocess.run(["uv", "run", wrapper, game_path], cwd=launcher_dir)
    else:
        break
