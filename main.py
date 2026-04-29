import os
import subprocess
import pyxel

# ---- 画面設定 ----
W = 256
H = 192
HEADER_H = 18
FOOTER_H = 13
ITEM_H = 11

LIST_TOP = HEADER_H + 3
LIST_H = H - HEADER_H - FOOTER_H - 6
LIST_VISIBLE = LIST_H // ITEM_H  # 表示できる最大行数

# ---- カラー定数 ----
C_BG = 0         # 黒背景
C_HEADER = 1     # ネイビー: ヘッダー/フッター背景
C_ACCENT = 12    # シアン: アクセントライン・選択バー左端
C_SEL_BG = 5     # ダークブルー: 選択行背景
C_SEL_TEXT = 7   # 白: 選択行テキスト
C_SEL_MARK = 12  # シアン: 選択行 ">" マーク
C_NORMAL = 7     # 白: 通常テキスト
C_DIM = 13       # グレー: 補助テキスト
C_SCROLL = 6     # 水色: スクロールバー


class Launcher:
    def __init__(self):
        pyxel.init(W, H, title="My Gameboy Launcher", fps=30,
                   quit_key=pyxel.KEY_ESCAPE, display_scale=3)
        pyxel.fullscreen(True)
        self.games = _scan_games()
        self.selected = 0
        self.scroll = 0
        pyxel.run(self.update, self.draw)

    # ---------------------------------------------------------------- update
    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if not self.games:
            return

        if pyxel.btnp(pyxel.KEY_UP, hold=20, repeat=5):
            self._move(-1)
        if pyxel.btnp(pyxel.KEY_DOWN, hold=20, repeat=5):
            self._move(1)

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_Z):
            _launch(self.games[self.selected]["path"])

    def _move(self, delta):
        self.selected = (self.selected + delta) % len(self.games)
        # スクロール追従
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + LIST_VISIBLE:
            self.scroll = self.selected - LIST_VISIBLE + 1

    # ----------------------------------------------------------------- draw
    def draw(self):
        pyxel.cls(C_BG)
        _draw_header()
        _draw_list(self.games, self.selected, self.scroll)
        _draw_footer()

    # ----------------------------------------------------------------


def _scan_games():
    # main.py のある場所を基準にしたローカル games/ を優先し、~/games/ を追加
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        os.path.join(launcher_dir, "games"),
        os.path.expanduser("~/games"),
    ]
    seen: set[str] = set()
    result = []
    for games_dir in search_dirs:
        if not os.path.isdir(games_dir):
            continue
        for entry in sorted(os.listdir(games_dir)):
            full = os.path.join(games_dir, entry)
            if entry.endswith(".py") and os.path.isfile(full):
                key = os.path.abspath(full)
                if key not in seen:
                    seen.add(key)
                    result.append({"name": entry[:-3], "path": full})
            elif os.path.isdir(full):
                candidate = os.path.join(full, "main.py")
                if os.path.isfile(candidate):
                    key = os.path.abspath(candidate)
                    if key not in seen:
                        seen.add(key)
                        result.append({"name": entry, "path": candidate})
    return result


def _launch(path):
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    wrapper = os.path.join(launcher_dir, "run_fullscreen.py")
    subprocess.Popen(["uv", "run", wrapper, path])
    pyxel.quit()


def _draw_header():
    pyxel.rect(0, 0, W, HEADER_H, C_HEADER)
    pyxel.line(0, HEADER_H, W - 1, HEADER_H, C_ACCENT)
    title = "MY GAMEBOY"
    pyxel.text((W - len(title) * 4) // 2, (HEADER_H - 5) // 2, title, C_NORMAL)


def _draw_list(games, selected, scroll):
    if not games:
        msg = "No games found in ~/games/"
        pyxel.text((W - len(msg) * 4) // 2, H // 2 - 3, msg, C_DIM)
        return

    max_chars = (W - 20) // 4  # 表示できる最大文字数

    for i in range(LIST_VISIBLE):
        idx = scroll + i
        if idx >= len(games):
            break

        y = LIST_TOP + i * ITEM_H
        name = games[idx]["name"]
        if len(name) > max_chars:
            name = name[:max_chars - 2] + ".."

        if idx == selected:
            # 選択行: ハイライト背景
            pyxel.rect(0, y, W - 8, ITEM_H - 1, C_SEL_BG)
            # 左端アクセントバー
            pyxel.rect(0, y, 3, ITEM_H - 1, C_ACCENT)
            pyxel.text(7, y + 2, ">" , C_SEL_MARK)
            pyxel.text(14, y + 2, name, C_SEL_TEXT)
        else:
            pyxel.text(14, y + 2, name, C_NORMAL)

    _draw_scrollbar(len(games), selected, scroll)


def _draw_scrollbar(total, selected, scroll):
    if total <= LIST_VISIBLE:
        return

    sb_x = W - 5
    sb_h = LIST_H
    thumb_h = max(4, sb_h * LIST_VISIBLE // total)
    thumb_y = LIST_TOP + (sb_h - thumb_h) * scroll // max(1, total - LIST_VISIBLE)

    pyxel.rect(sb_x, LIST_TOP, 3, sb_h, C_HEADER)
    pyxel.rect(sb_x, thumb_y, 3, thumb_h, C_SCROLL)


def _draw_footer():
    fy = H - FOOTER_H
    pyxel.rect(0, fy, W, FOOTER_H, C_HEADER)
    pyxel.line(0, fy, W - 1, fy, C_ACCENT)
    hint = "UP/DOWN Select   Z/ENTER Launch   ESC Quit"
    pyxel.text(4, fy + (FOOTER_H - 5) // 2, hint, C_DIM)


def main():
    Launcher()


if __name__ == "__main__":
    main()
