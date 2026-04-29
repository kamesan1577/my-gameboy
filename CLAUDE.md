# CLAUDE.md
日本語で応答すること
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Pyxel-based game launcher for a custom Raspberry Pi 4B handheld console. The launcher runs fullscreen on boot (via systemd), lists games from `~/games/`, and launches them via `subprocess.Popen()`. UI style targets SteamOS-like aesthetics.

**Development is done on Windows (VS Code + UV). Pi deployment is a later phase.**

## Commands

```bash
# Run the launcher
uv run main.py

# Add a dependency
uv add <package>

# Run Pyxel editor (for sprite/sound assets)
uv run pyxel edit <file.pyxres>

# Run a Pyxel example for reference
uv run pyxel play .venv/Lib/site-packages/pyxel/examples/02_jump_game.py
```

## Architecture

### Pyxel app structure

Every Pyxel app follows this pattern:

```python
import pyxel

class App:
    def __init__(self):
        pyxel.init(width, height, title=..., fps=...)
        pyxel.run(self.update, self.draw)

    def update(self):
        # input + logic, called every frame

    def draw(self):
        # rendering only, called every frame
```

`pyxel.run()` blocks — it owns the main loop.

### Input model

On PC: keyboard/mouse via `pyxel.btn()` / `pyxel.btnp()`.  
On Pi: 8 GPIO buttons (4 directional + 4 action, no L/R) wired directly to GPIO pins. GPIO input must be mapped to Pyxel's key constants or handled in `update()` alongside `pyxel.btn()`.

### Launcher responsibilities

- Scan `~/games/` for launchable game entries
- Render a scrollable game list (SteamOS-like)
- On confirm: `subprocess.Popen(["uv", "run", game_path])` and suspend or exit the launcher
- On game exit: launcher resumes (or restarts via systemd)

### Pi deployment notes

- systemd unit targets the launcher as the login shell replacement or a user service
- Display and audio configuration TBD
