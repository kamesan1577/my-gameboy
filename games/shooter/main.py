import random
import pyxel

W = 160
H = 120

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

    def update(self):
        self.y -= 4
        if self.y < 0:
            self.alive = False


class Enemy:
    def __init__(self):
        self.x = random.randint(4, W - 8)
        self.y = -8
        self.speed = random.uniform(0.6, 1.4)
        self.alive = True

    def update(self):
        self.y += self.speed
        if self.y > H:
            self.alive = False


class Game:
    PLAYER_SPEED = 2
    SHOOT_COOLDOWN = 10

    def __init__(self):
        pyxel.init(W, H, title="Shooter", fps=30,
                   quit_key=pyxel.KEY_ESCAPE, display_scale=3)
        self._reset()
        pyxel.run(self.update, self.draw)

    def _reset(self):
        self.px = W // 2
        self.py = H - 12
        self.bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.score = 0
        self.lives = 3
        self.shoot_timer = 0
        self.spawn_timer = 0
        self.spawn_interval = 40  # フレーム数
        self.game_over = False
        self.flash = 0  # ダメージフラッシュ

    # ---------------------------------------------------------------- update
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
                self._reset()
            return

        self._move_player()
        self._shoot()
        self._spawn_enemy()
        self._update_objects()
        self._check_collisions()

        if self.flash > 0:
            self.flash -= 1

    def _move_player(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.px = max(4, self.px - self.PLAYER_SPEED)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.px = min(W - 8, self.px + self.PLAYER_SPEED)

    def _shoot(self):
        self.shoot_timer = max(0, self.shoot_timer - 1)
        if self.shoot_timer == 0 and (
            pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_SPACE)
        ):
            self.bullets.append(Bullet(self.px + 1, self.py - 4))
            self.shoot_timer = self.SHOOT_COOLDOWN

    def _spawn_enemy(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.enemies.append(Enemy())
            # スコアが上がるほど敵が増える
            self.spawn_interval = max(15, 40 - self.score // 3)

    def _update_objects(self):
        for b in self.bullets:
            b.update()
        for e in self.enemies:
            e.update()
        self.bullets = [b for b in self.bullets if b.alive]
        self.enemies = [e for e in self.enemies if e.alive]

    def _check_collisions(self):
        # 弾 vs 敵
        for b in self.bullets:
            for e in self.enemies:
                if e.alive and abs(b.x - e.x) < 6 and abs(b.y - e.y) < 6:
                    b.alive = False
                    e.alive = False
                    self.score += 1

        # 敵 vs プレイヤー
        for e in self.enemies:
            if e.alive and abs(e.x - self.px) < 7 and abs(e.y - self.py) < 7:
                e.alive = False
                self.lives -= 1
                self.flash = 20
                if self.lives <= 0:
                    self.game_over = True

    # ----------------------------------------------------------------- draw
    def draw(self):
        pyxel.cls(0)
        self._draw_stars()

        if self.game_over:
            self._draw_gameover()
            return

        self._draw_player()
        self._draw_bullets()
        self._draw_enemies()
        self._draw_hud()

    def _draw_stars(self):
        # フレームカウントでスクロール演出
        for i in range(20):
            pyxel.pset(
                (i * 37 + 5) % W,
                (i * 19 + pyxel.frame_count // 2) % H,
                1 if i % 3 == 0 else 13,
            )

    def _draw_player(self):
        col = 8 if self.flash > 0 and pyxel.frame_count % 4 < 2 else 12
        # 機体: シンプルな三角形
        pyxel.tri(self.px + 2, self.py, self.px - 3, self.py + 7, self.px + 7, self.py + 7, col)
        pyxel.rect(self.px, self.py + 5, 4, 3, 6)

    def _draw_bullets(self):
        for b in self.bullets:
            pyxel.rect(b.x, b.y, 2, 4, 10)

    def _draw_enemies(self):
        for e in self.enemies:
            ex, ey = int(e.x), int(e.y)
            # ひし形の敵
            pyxel.tri(ex + 3, ey, ex, ey + 4, ex + 6, ey + 4, 8)
            pyxel.tri(ex, ey + 4, ex + 6, ey + 4, ex + 3, ey + 8, 9)

    def _draw_hud(self):
        pyxel.text(2, 2, f"SCORE {self.score:04d}", 7)
        # ライフ表示
        for i in range(self.lives):
            pyxel.tri(W - 6 - i * 8, 2, W - 9 - i * 8, 7, W - 3 - i * 8, 7, 11)

    def _draw_gameover(self):
        pyxel.text(W // 2 - 22, H // 2 - 10, "GAME OVER", 8)
        pyxel.text(W // 2 - 26, H // 2,     f"SCORE {self.score:04d}", 7)
        if pyxel.frame_count % 30 < 20:
            pyxel.text(W // 2 - 30, H // 2 + 12, "Z/ENTER to retry", 13)


Game()
