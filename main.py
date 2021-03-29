import math
from random import randint, random

import tkinter as tk

from gamelib import Sprite, GameApp, Text, EnemyGenerationStrategy, KeyboardHandler, StatusWithText
from PIL import Image, ImageTk
from consts import *
from elements import Ship, Bullet, Enemy, TieFighter, Explode
from utils import random_edge_position, normalize_vector, direction_to_dxdy, vector_len, distance


class GameKeyboardHandler(KeyboardHandler):
    def __init__(self, game_app, ship, successor=None):
        super().__init__(successor)
        self.game_app = game_app
        self.ship = ship


class BombKeyPressedHandler(GameKeyboardHandler):
    def handle(self, event):
        if event.char.upper() == 'Z':
            self.game_app.bomb()
        else:
            super().handle(event)


class ShipMovementKeyPressedHandler(GameKeyboardHandler):
    def handle(self, event):
        if event.keysym == 'Left':
            self.ship.start_turn('LEFT')
        elif event.keysym == 'Right':
            self.ship.start_turn('RIGHT')
        elif event.char == ' ':
            self.ship.fire()
        elif event.char.upper() == 'Z':
            self.bomb()


class ShipMovementKeyReleasedHandler(GameKeyboardHandler):
    def handle(self, event):
        if event.keysym == 'Left':
            self.ship.stop_turn('LEFT')
        elif event.keysym == 'Right':
            self.ship.stop_turn('RIGHT')


class StarEnemyGenerationStrategy(EnemyGenerationStrategy):
    def generate(self, space_game, ship):

        enemies = []
        x = randint(100, CANVAS_WIDTH - 100)
        y = randint(100, CANVAS_HEIGHT - 100)

        while vector_len(x - ship.x, y - ship.y) < 200:
            x = randint(100, CANVAS_WIDTH - 100)
            y = randint(100, CANVAS_HEIGHT - 100)
        for d in range(18):
            dx, dy = direction_to_dxdy(d * 20)

            enemy = Enemy(space_game, x, y, dx * ENEMY_BASE_SPEED,
                          dy * ENEMY_BASE_SPEED)
            enemies.append(enemy)

        return enemies


class TieFighterEnemyGeration(EnemyGenerationStrategy):
    def generate(self, space_game, ship):
        x, y = random_edge_position()
        vx, vy = normalize_vector(ship.x - x, ship.y - y)

        vx *= ENEMY_BASE_SPEED
        vy *= ENEMY_BASE_SPEED

        enemy = TieFighter(space_game, x, y, vx, vy)
        return [enemy]


class EdgeEnemyGenerationStrategy(EnemyGenerationStrategy):
    def generate(self, space_game, ship):
        x, y = random_edge_position()
        vx, vy = normalize_vector(ship.x - x, ship.y - y)

        vx *= ENEMY_BASE_SPEED
        vy *= ENEMY_BASE_SPEED

        enemy = Enemy(space_game, x, y, vx, vy)
        return [enemy]


class SpaceGame(GameApp):
    def init_game(self):
        self.background = Sprite(
            self, "images/background.png", CANVAS_WIDTH//2, CANVAS_HEIGHT//2)
        self.ship = Ship(self, CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)

        self.level = StatusWithText(
            self, 100, CANVAS_WIDTH-CANVAS_WIDTH*0.3, 'level: %d', 1)

        self.score_wait = 0
        self.score = StatusWithText(self, 100, 20, 'Score: %d', 0)
        self.enemy_creation_strategies = [
            (0.09, TieFighterEnemyGeration()),
            (0.03, StarEnemyGenerationStrategy()),
            (0.8, EdgeEnemyGenerationStrategy())
        ]
        self.bomb_power = StatusWithText(
            self, CANVAS_WIDTH-100, 20, 'power: %d', BOMB_FULL_POWER)
        self.bomb_wait = 0
        self.bomb_power_text = Text(self, '', 700, 20)
        self.health = StatusWithText(
            self, 700, CANVAS_WIDTH-CANVAS_WIDTH*0.3, 'health: %d', 4)
        self.elements.append(self.ship)

        self.enemies = []
        self.bullets = []
        self.init_key_handlers()

    def init_key_handlers(self):
        key_pressed_handler = ShipMovementKeyPressedHandler(self, self.ship)
        key_pressed_handler = BombKeyPressedHandler(
            self, self.ship, key_pressed_handler)
        self.key_pressed_handler = key_pressed_handler

        key_released_handler = ShipMovementKeyReleasedHandler(self, self.ship)
        self.key_released_handler = key_released_handler

    def create_enemies(self):
        p = random()

        for prob, strategy in self.enemy_creation_strategies:
            if p < prob:
                enemies = strategy.generate(self, self.ship)
                for e in enemies:
                    self.add_enemy(e)
                break

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_bullet(self, bullet):
        if self.bomb_power.value > 0:
            self.bomb_power.value -= 1
            self.bullets.append(bullet)

    def bullet_count(self):
        return len(self.bullets)

    def animate_bomb(self, i):
        if len(self.bomb_list) > 0:
            self.canvas.delete(self.bomb_list[-1])
            if i == 10:
                return
        bomb = 0+BOMB_RADIUS*(i*0.1)
        self.bomb_list.append(self.canvas.create_oval(
            self.ship.x - bomb,
            self.ship.y - bomb,
            self.ship.x + bomb,
            self.ship.y + bomb, fill="#CCFFFF"))
        self.after(50, lambda: self.animate_bomb(i+1))

    def bomb(self):
        if self.bomb_power.value == BOMB_FULL_POWER:
            self.bomb_power.value = 0
            self.bomb_list = []
            self.animate_bomb(0)
            for e in self.enemies:
                if self.ship.distance_to(e) <= BOMB_RADIUS:

                    explode = Explode(self, e.x, e.y, 50)
                    explode.update()
                    self.score.value += 1
                    e.to_be_deleted = True

    def update_level_text(self):
        self.level.value += 1

    def update_score(self):
        self.score_wait += 1
        if self.score_wait >= SCORE_WAIT:
            self.score.value += 1
            self.score_wait = 0

    def update_health(self):
        self.health_wait += 1

    def update_bomb_power(self):
        self.bomb_wait += 1
        if (self.bomb_wait >= BOMB_WAIT) and (self.bomb_power.value != BOMB_FULL_POWER):
            self.bomb_wait = 0
            self.bomb_power.value += 1

    def pre_update(self):
        if random() < 0.1:
            self.create_enemies()

    def process_bullet_enemy_collisions(self):
        for b in self.bullets:
            for e in self.enemies:
                if b.is_colliding_with_enemy(e):
                    if isinstance(e, TieFighter):
                        explode = Explode(self, e.x, e.y, 200)
                        explode.update()
                    else:
                        explode = Explode(self, e.x, e.y, 50)
                        explode.update()
                    self.score.value += 1
                    b.to_be_deleted = True
                    e.to_be_deleted = True

    def process_ship_enemy_collision(self):
        for e in self.enemies:

            if self.ship.is_colliding_with_enemy(e):
                self.health.value -= 1
                self.ship_got_hit(50)
                e.to_be_deleted = True
                if self.health.value == 0 or isinstance(e, TieFighter):
                    self.health.value = 0
                    self.ship_got_hit(200)
                    self.ship.delete()
                    self.stop_animation()

    def process_collisions(self):
        self.process_bullet_enemy_collisions()
        self.process_ship_enemy_collision()

    def ship_got_hit(self, size):
        explode = Explode(self, self.ship.x, self.ship.y, size)
        explode.update()

    def update_and_filter_deleted(self, elements):
        new_list = []
        for e in elements:
            e.update()
            e.render()
            if e.to_be_deleted:
                e.delete()
            else:
                new_list.append(e)
        return new_list

    def post_update(self):
        self.process_collisions()

        self.bullets = self.update_and_filter_deleted(self.bullets)
        self.enemies = self.update_and_filter_deleted(self.enemies)

        self.update_score()
        self.update_bomb_power()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Space Fighter")

    # do not allow window resizing
    root.resizable(False, False)
    app = SpaceGame(root, CANVAS_WIDTH, CANVAS_HEIGHT, UPDATE_DELAY)
    app.start()
    root.mainloop()
