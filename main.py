import math
from random import randint, random

import tkinter as tk

from gamelib import Sprite, GameApp, Text

from consts import *
from elements import Ship, Bullet, Enemy
from utils import random_edge_position, normalize_vector, direction_to_dxdy, vector_len, distance


class SpaceGame(GameApp):
    def init_game(self):
        self.ship = Ship(self, CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)

        self.level = 1
        self.level_text = Text(self, '', 100, 580)
        self.update_level_text()

        self.score = 0
        self.score_wait = 0
        self.score_text = Text(self, '', 100, 20)
        self.update_score_text()

        self.bomb_power = BOMB_FULL_POWER
        self.bomb_wait = 0
        self.bomb_power_text = Text(self, '', 700, 20)
        self.update_bomb_power_text()

        self.elements.append(self.ship)

        self.enemies = []
        self.bullets = []

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_bullet(self, bullet):
        self.bullets.append(bullet)

    def bullet_count(self):
        return len(self.bullets)

    def bomb(self):
        if self.bomb_power == BOMB_FULL_POWER:
            self.bomb_power = 0

            self.bomb_canvas_id = self.canvas.create_oval(
                self.ship.x - BOMB_RADIUS, 
                self.ship.y - BOMB_RADIUS,
                self.ship.x + BOMB_RADIUS, 
                self.ship.y + BOMB_RADIUS
            )

            self.after(200, lambda: self.canvas.delete(self.bomb_canvas_id))

            for e in self.enemies:
                if self.ship.distance_to(e) <= BOMB_RADIUS:
                    e.to_be_deleted = True

            self.update_bomb_power_text()

    def update_score_text(self):
        self.score_text.set_text('Score: %d' % self.score)

    def update_bomb_power_text(self):
        self.bomb_power_text.set_text('Power: %d%%' % self.bomb_power)

    def update_level_text(self):
        self.level_text.set_text('Level: %d' % self.level)

    def update_score(self):
        self.score_wait += 1
        if self.score_wait >= SCORE_WAIT:
            self.score += 1
            self.score_wait = 0
            self.update_score_text()

    def update_bomb_power(self):
        self.bomb_wait += 1
        if (self.bomb_wait >= BOMB_WAIT) and (self.bomb_power != BOMB_FULL_POWER):
            self.bomb_power += 1
            self.bomb_wait = 0
            self.update_bomb_power_text()

    def create_enemy_star(self):
        enemies = []

        x = randint(100, CANVAS_WIDTH - 100)
        y = randint(100, CANVAS_HEIGHT - 100)

        while vector_len(x - self.ship.x, y - self.ship.y) < 200:
            x = randint(100, CANVAS_WIDTH - 100)
            y = randint(100, CANVAS_HEIGHT - 100)

        for d in range(18):
            dx, dy = direction_to_dxdy(d * 20)
            enemy = Enemy(self, x, y, dx * ENEMY_BASE_SPEED, dy * ENEMY_BASE_SPEED)
            enemies.append(enemy)

        return enemies

    def create_enemy_from_edges(self):
        x, y = random_edge_position()
        vx, vy = normalize_vector(self.ship.x - x, self.ship.y - y)

        vx *= ENEMY_BASE_SPEED
        vy *= ENEMY_BASE_SPEED

        enemy = Enemy(self, x, y, vx, vy)
        return [enemy]

    def create_enemies(self):
        if random() < 0.2:
            enemies = self.create_enemy_star()
        else:
            enemies = self.create_enemy_from_edges()

        for e in enemies:
            self.add_enemy(e)

    def pre_update(self):
        if random() < 0.1:
            self.create_enemies()

    def process_bullet_enemy_collisions(self):
        for b in self.bullets:
            for e in self.enemies:
                if b.is_colliding_with_enemy(e):
                    b.to_be_deleted = True
                    e.to_be_deleted = True

    def process_ship_enemy_collision(self):
        for e in self.enemies:
            if self.ship.is_colliding_with_enemy(e):
                self.stop_animation()

    def process_collisions(self):
        self.process_bullet_enemy_collisions()
        self.process_ship_enemy_collision()

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

    def on_key_pressed(self, event):
        if event.keysym == 'Left':
            self.ship.start_turn('LEFT')
        elif event.keysym == 'Right':
            self.ship.start_turn('RIGHT')
        elif event.char == ' ':
            self.ship.fire()
        elif event.char.upper() == 'Z':
            self.bomb()

    def on_key_released(self, event):
        if event.keysym == 'Left':
            self.ship.stop_turn('LEFT')
        elif event.keysym == 'Right':
            self.ship.stop_turn('RIGHT')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Space Fighter")
 
    # do not allow window resizing
    root.resizable(False, False)
    app = SpaceGame(root, CANVAS_WIDTH, CANVAS_HEIGHT, UPDATE_DELAY)
    app.start()
    root.mainloop()
