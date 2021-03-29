import math
from random import randint

from gamelib import Sprite, GameApp, Text

from consts import *
from math import atan, degrees, asin, cos, sin
from utils import direction_to_dxdy, distance

from PIL import Image,  ImageTk


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
        self.angle = degrees(atan(vy/vx))
        super().__init__(app, 'images/bullet1.png', x, y, vx, vy)

    def is_colliding_with_enemy(self, enemy):
        return self.is_within_distance(enemy, BULLET_ENEMY_HIT_RADIUS)

    def init_canvas_object(self):
        self.photo_image = Image.open(self.image_filename).convert("RGBA")
        self.photo_image = self.photo_image.rotate(-self.angle)
        self.photo_image = ImageTk.PhotoImage(image=self.photo_image)
        self.canvas_object_id = self.canvas.create_image(
            self.x,
            self.y,
            image=self.photo_image)


class TieBullet(FixedDirectionSprite):
    def __init__(self, app, x, y, vx, vy):
        self.angle = degrees(atan(vy/vx))
        super().__init__(app, 'images/bullet2.png', x, y, vx, vy)

    def is_colliding_with_ship(self, tie):
        return self.is_within_distance(tie, SHIP_ENEMY_HIT_RADIUS)

    def init_canvas_object(self):
        self.photo_image = Image.open(self.image_filename).convert("RGBA")
        self.photo_image = self.photo_image.rotate(-self.angle)
        self.photo_image = ImageTk.PhotoImage(image=self.photo_image)
        self.canvas_object_id = self.canvas.create_image(
            self.x,
            self.y,
            image=self.photo_image)


class Enemy(FixedDirectionSprite):
    def __init__(self, app, x, y, vx, vy):
        super().__init__(app, 'images/enemy1.png', x, y, vx, vy)


class TieFighter(FixedDirectionSprite):
    def __init__(self, app, x, y, vx, vy):
        self.angle = -degrees(atan(vy/vx))
        self.app = app
        if vx < 0:
            self.angle = -degrees(atan(vy/vx)) + 180
        super().__init__(app, "images/tie.png", x, y, vx, vy)

    def init_canvas_object(self):
        self.photo_image = Image.open(self.image_filename).convert("RGBA")
        self.photo_image = ImageTk.PhotoImage(
            image=self.photo_image.rotate(self.angle))
        self.canvas_object_id = self.canvas.create_image(
            self.x,
            self.y,
            image=self.photo_image)
        self.app.after(500, self.fire)
        self.app.after(900, self.fire)

    def fire(self):
        if self.app.bullet_count() >= MAX_NUM_BULLETS:
            return

        dx, dy = direction_to_dxdy(-self.angle)
        bullet0 = TieBullet(self.app, self.x, self.y, dx *
                            BULLET_BASE_SPEED, dy * BULLET_BASE_SPEED)
        self.app.add_enemy(bullet0)


class Ship(Sprite):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/ship.png', x, y)

        self.app = app
        self.angle = 0
        self.direction = 0
        self.is_turning_left = False
        self.is_turning_right = False

    def init_canvas_object(self):
        self.photo_image = Image.open(self.image_filename).convert("RGBA")
        self.photo_image = ImageTk.PhotoImage(
            image=self.photo_image)
        self.canvas_object_id = self.canvas.create_image(
            self.x,
            self.y,
            image=self.photo_image)

    def update(self):
        dx, dy = direction_to_dxdy(self.direction)
        self.x += dx * SHIP_SPEED
        self.y += dy * SHIP_SPEED
        if self.is_turning_left:
            self.turn_left()
        elif self.is_turning_right:
            self.turn_right()

    def update_ship(self):
        self.canvas.delete(self.canvas_object_id)
        self.photo_image = Image.open(self.image_filename).convert("RGBA")
        self.photo_image = ImageTk.PhotoImage(
            self.photo_image.rotate(self.angle))
        self.canvas_object_id = self.canvas.create_image(
            self.x,
            self.y,
            image=self.photo_image)

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
        self.angle += SHIP_TURN_ANGLE
        self.update_ship()
        self.direction -= SHIP_TURN_ANGLE

    def turn_right(self):
        self.angle -= SHIP_TURN_ANGLE
        self.update_ship()
        self.direction += SHIP_TURN_ANGLE

    def is_colliding_with_enemy(self, enemy):
        return self.is_within_distance(enemy, SHIP_ENEMY_HIT_RADIUS)

    def fire(self):
        if self.app.bullet_count() >= MAX_NUM_BULLETS:
            return

        dx, dy = direction_to_dxdy(self.direction)
        bullet0 = Bullet(self.app, self.x, self.y, dx *
                         BULLET_BASE_SPEED, dy * BULLET_BASE_SPEED)
        self.app.add_bullet(bullet0)
