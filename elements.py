import math
from random import randint

from gamelib import Sprite, GameApp, Text

from consts import *

from utils import direction_to_dxdy, distance

class FixedDirectionSprite(Sprite):
    def __init__(self, app, image_filename, x, y, vx, vy):
        super().__init__(app, image_filename, x, y)
        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if (self.x < 0) or (self.y < 0) or (self.x > CANVAS_WIDTH) or (self.y > CANVAS_HEIGHT):
            self.to_be_deleted = True


class Bullet(FixedDirectionSprite):
    def __init__(self, app, x, y, vx, vy):
        super().__init__(app, 'images/bullet1.png', x, y, vx, vy)

    def is_colliding_with_enemy(self, enemy):
        return self.is_within_distance(enemy, BULLET_ENEMY_HIT_RADIUS)


class Enemy(FixedDirectionSprite):
    def __init__(self, app, x, y, vx, vy):
        super().__init__(app, 'images/enemy1.png', x, y, vx, vy)


class Ship(Sprite):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/ship.png', x, y)

        self.app = app

        self.direction = 0
        self.is_turning_left = False
        self.is_turning_right = False

    def update(self):
        dx,dy = direction_to_dxdy(self.direction)

        self.x += dx * SHIP_SPEED
        self.y += dy * SHIP_SPEED

        if self.is_turning_left:
            self.turn_left()
        elif self.is_turning_right:
            self.turn_right()

    def start_turn(self, dir):
        if dir.upper() == 'LEFT':
            self.is_turning_left = True
            self.is_turning_right = False
        else:
            self.is_turning_right = True
            self.is_turning_left = False

    def stop_turn(self, dir=None):
        if (dir == None) or (dir.upper() == 'LEFT'):
            self.is_turning_left = False
        if (dir == None) or (dir.upper() == 'RIGHT'):
            self.is_turning_right = False

    def turn_left(self):
        self.direction -= SHIP_TURN_ANGLE

    def turn_right(self):
        self.direction += SHIP_TURN_ANGLE

    def is_colliding_with_enemy(self, enemy):
        return self.is_within_distance(enemy, SHIP_ENEMY_HIT_RADIUS)

    def fire(self):
        if self.app.bullet_count() >= MAX_NUM_BULLETS:
            return

        dx,dy = direction_to_dxdy(self.direction)

        bullet = Bullet(self.app, self.x, self.y, dx * BULLET_BASE_SPEED, dy * BULLET_BASE_SPEED)

        self.app.add_bullet(bullet)

