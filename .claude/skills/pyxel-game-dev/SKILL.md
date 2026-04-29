---
name: pyxel-game-dev
description: >
  Pyxelを使ったゲーム・アプリ開発の支援スキル。Raspberry Pi 4B向けハンドヘルド機での動作を前提とする。
  ゲームループ構造の設計、スプライト描画、入力処理（キーボード/GPIO）、サウンド、タイルマップなど
  Pyxelの全機能をカバーする。Pyxelで何かを作りたい・Pyxelのコードを書きたい・Pyxelアプリを改良したい
  といった場面では必ずこのスキルを参照すること。GPIO入力マッピング、Pi向けパフォーマンス最適化、
  systemd連携なども扱う。
---

# Pyxel Game Dev Skill

Pyxelを使ったゲーム/アプリをRaspberry Pi 4B向けハンドヘルド機で動かすための開発支援。
Windows(UV)で開発し、Piにデプロイするワークフローを想定している。

## アプリの基本構造

Pyxelアプリは必ずこのパターンに従う:

```python
import pyxel

class App:
    def __init__(self):
        pyxel.init(width, height, title="My Game", fps=30)
        # 初期化処理
        pyxel.run(self.update, self.draw)  # ブロッキング呼び出し

    def update(self):
        # 毎フレーム: 入力処理 + ゲームロジック

    def draw(self):
        # 毎フレーム: 描画のみ（ロジックを書かない）

App()
```

`pyxel.run()` はメインループを所有しブロックする。`update` と `draw` を分離することで
ロジックと描画を明確に分けられる。

## このプロジェクトのハードウェア仕様

- **ターゲット機**: Raspberry Pi 4B ハンドヘルド機
- **ボタン**: GPIO直結 8ボタン（上下左右 + A/B/X/Y相当、L/Rなし）
- **開発環境**: Windows + VS Code + UV → Piへデプロイ

## 推奨init設定（Pi向け）

```python
pyxel.init(
    160, 120,          # 小解像度はPiの処理負荷を下げる（UCTRONICSディスプレイに合わせて調整）
    title="Game",
    fps=30,            # 60fpsはPiで重い場合がある
    quit_key=pyxel.KEY_ESCAPE,
    display_scale=2,   # ウィンドウサイズ拡大（PC確認時）
)
```

## 入力API

### キーボード（PC開発時）
```python
pyxel.btn(key)         # 押下中: bool
pyxel.btnp(key, hold=None, repeat=None)  # 押した瞬間（holdms後にrepeatms間隔で繰り返し）
pyxel.btnr(key)        # 離した瞬間: bool
pyxel.btnv(key)        # アナログ値: float
```

よく使うキー定数:
```
pyxel.KEY_UP / KEY_DOWN / KEY_LEFT / KEY_RIGHT
pyxel.KEY_Z / KEY_X / KEY_C / KEY_V  (アクションボタン代替)
pyxel.KEY_RETURN / KEY_SPACE / KEY_ESCAPE
pyxel.GAMEPAD1_BUTTON_DPAD_UP/DOWN/LEFT/RIGHT
pyxel.GAMEPAD1_BUTTON_A / B / X / Y
```

### GPIO入力（Pi本番時）

GPIOボタンはPyxelのキー入力として扱う。`RPi.GPIO` または `gpiozero` で読み取り、
`pyxel.set_btn(key, state)` でPyxelのキー状態に注入する:

```python
import pyxel
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False

# GPIOピン → Pyxelキー のマッピング（実機配線に合わせて変更）
GPIO_MAP = {
    17: pyxel.KEY_UP,
    27: pyxel.KEY_DOWN,
    22: pyxel.KEY_LEFT,
    23: pyxel.KEY_RIGHT,
    5:  pyxel.KEY_Z,    # A
    6:  pyxel.KEY_X,    # B
    13: pyxel.KEY_C,    # X
    19: pyxel.KEY_V,    # Y
}

class App:
    def __init__(self):
        if HAS_GPIO:
            GPIO.setmode(GPIO.BCM)
            for pin in GPIO_MAP:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pyxel.init(160, 120, title="Game", fps=30)
        pyxel.run(self.update, self.draw)

    def update(self):
        if HAS_GPIO:
            for pin, key in GPIO_MAP.items():
                # プルアップ抵抗: 押下でLOW
                pyxel.set_btn(key, not GPIO.input(pin))
        # 以降は通常通り pyxel.btn() / pyxel.btnp() を使う
```

`HAS_GPIO` フラグでWindows開発時とPi本番時を自動切替できる。

## 描画API

```python
pyxel.cls(col)                      # 画面クリア（必ずdrawの先頭で呼ぶ）
pyxel.pset(x, y, col)               # 点
pyxel.line(x1, y1, x2, y2, col)     # 直線
pyxel.rect(x, y, w, h, col)         # 塗り矩形
pyxel.rectb(x, y, w, h, col)        # 枠矩形
pyxel.circ(x, y, r, col)            # 塗り円
pyxel.circb(x, y, r, col)           # 枠円
pyxel.elli(x, y, w, h, col)         # 塗り楕円
pyxel.tri(x1,y1, x2,y2, x3,y3, col) # 塗り三角
pyxel.fill(x, y, col)               # バケツ塗り
pyxel.text(x, y, s, col)            # テキスト（4×6px固定フォント）
pyxel.clip(x, y, w, h)             # 描画クリッピング領域設定
pyxel.camera(x, y)                  # カメラオフセット（スクロール）
pyxel.pal(col1, col2)               # 色パレット置換
pyxel.dither(alpha)                 # ディザ透過（0.0〜1.0）
```

### スプライト/イメージバンク

```python
pyxel.load("assets.pyxres")         # .pyxresからイメージ・サウンドを読み込む
pyxel.blt(x, y, img, u, v, w, h, colkey=None, rotate=None, scale=None)
# img: イメージバンク番号(0-2)
# u,v: ソース座標, w,h: サイズ（負値で反転）
# colkey: 透明色インデックス

img = pyxel.image(0)               # Imageオブジェクト取得
img.set(x, y, data)                # ピクセルデータをセット
img.load(x, y, "file.png")         # 画像ファイルを読み込んでイメージバンクに貼り付け
```

### タイルマップ

```python
pyxel.bltm(x, y, tm, u, v, w, h, colkey=None)
# tm: タイルマップ番号(0-7)

tm = pyxel.tilemap(0)
tm.set(x, y, data)                 # タイルデータをセット
tile = tm.pget(x, y)               # タイル取得 (img_idx, tile_u, tile_v)
```

## カラーパレット（16色）

```
pyxel.COLOR_BLACK=0    pyxel.COLOR_NAVY=1     pyxel.COLOR_PURPLE=2
pyxel.COLOR_GREEN=3    pyxel.COLOR_BROWN=4    pyxel.COLOR_DARK_BLUE=5
pyxel.COLOR_LIGHT_BLUE=6  pyxel.COLOR_WHITE=7   pyxel.COLOR_RED=8
pyxel.COLOR_ORANGE=9   pyxel.COLOR_YELLOW=10  pyxel.COLOR_LIME=11
pyxel.COLOR_CYAN=12    pyxel.COLOR_GRAY=13    pyxel.COLOR_PINK=14
pyxel.COLOR_PEACH=15
```

実際には整数(0-15)で指定するのが慣習。

## サウンドAPI

```python
pyxel.play(ch, snd, loop=False)     # ch: チャンネル(0-3), snd: サウンド番号(0-63)
pyxel.playm(msc, loop=False)        # ミュージック再生
pyxel.stop(ch=None)                 # 停止（Noneで全チャンネル）
pyxel.play_pos(ch)                  # 再生位置取得

snd = pyxel.sound(0)               # Soundオブジェクト取得
snd.set("e2e2c2g1 g1g1_2", "p", "6", "s", 20)
# notes, tones, volumes, effects, speed

pyxel.gen_bgm(preset, transp, instr, seed)  # BGM自動生成
```

サウンドは `.pyxres` ファイルに保存・管理するのが最もシンプル。
`uv run pyxel edit assets.pyxres` でGUIエディタが開く。

## システム情報

```python
pyxel.width / pyxel.height         # 画面サイズ
pyxel.frame_count                  # 経過フレーム数
pyxel.mouse_x / pyxel.mouse_y      # マウス座標
pyxel.mouse_wheel                  # ホイール量
pyxel.fps                          # 現在のFPS（存在する場合）
```

## ゲームループの典型パターン

```python
import pyxel

class Game:
    SCREEN_W = 160
    SCREEN_H = 120

    def __init__(self):
        pyxel.init(self.SCREEN_W, self.SCREEN_H, title="Game", fps=30)
        pyxel.load("assets.pyxres")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player_x = self.SCREEN_W // 2
        self.player_y = self.SCREEN_H // 2
        self.score = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        spd = 2
        if pyxel.btn(pyxel.KEY_LEFT):  self.player_x -= spd
        if pyxel.btn(pyxel.KEY_RIGHT): self.player_x += spd
        if pyxel.btn(pyxel.KEY_UP):    self.player_y -= spd
        if pyxel.btn(pyxel.KEY_DOWN):  self.player_y += spd

        # 画面端クランプ
        self.player_x = pyxel.clamp(self.player_x, 0, self.SCREEN_W - 8)
        self.player_y = pyxel.clamp(self.player_y, 0, self.SCREEN_H - 8)

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(self.player_x, self.player_y, 0, 0, 0, 8, 8, 0)
        pyxel.text(1, 1, f"SCORE:{self.score}", 7)

Game()
```

## Pi向けパフォーマンスのポイント

- **解像度は小さく**: 160×120 や 256×192 程度が安全。大きいほど重い
- **fps=30**: 60fpsはPi 4でも厳しい場合がある
- **`perf_monitor(True)`**: 開発時に有効にしてFPSを監視
- **描画の最小化**: `draw()` でパーティクルや大量のpsetは避ける
- **pyxres活用**: スプライトは事前に `.pyxres` に焼いて `blt()` で描く

## ランチャーとの連携（このプロジェクト固有）

このプロジェクトのランチャー (`main.py`) は `~/games/` にあるゲームを
`subprocess.Popen(["uv", "run", game_path])` で起動する。
ゲーム側は `uv run` で単独起動できる構成にしておく（`pyproject.toml` に依存関係を記載）。

ゲーム終了時はランチャーに制御が戻るか、systemdが再起動する。

## 開発コマンド

```bash
uv run main.py                              # ランチャー起動
uv run my_game.py                           # ゲーム単体起動
uv run pyxel edit assets.pyxres             # アセットエディタ
uv run pyxel play examples/02_jump_game.py  # サンプル参照
```
