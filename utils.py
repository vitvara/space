import math
from random import randint

from consts import *

def direction_to_dxdy(direction):
    return (math.cos(direction * math.pi / 180), 
        math.sin(direction * math.pi / 180))


def vector_len(x,y):
    return math.sqrt(x*x + y*y)


def distance(x1, y1, x2, y2):
    return vector_len(x1 - x2, y1 - y2)


def normalize_vector(dx, dy):
    l = vector_len(dx, dy)
    if l > 0.01:
        return (dx / l, dy / l)
    else:
        return (0, 0)


def random_edge_position():
    l = randint(0, CANVAS_HEIGHT * 2 + CANVAS_WIDTH * 2)
    if l > CANVAS_WIDTH * 2 + CANVAS_HEIGHT:
        x = 0
        y = l - CANVAS_WIDTH * 2 + CANVAS_HEIGHT
    elif l > CANVAS_WIDTH + CANVAS_HEIGHT:
        x = l - CANVAS_WIDTH + CANVAS_HEIGHT
        y = CANVAS_HEIGHT
    elif l > CANVAS_WIDTH:
        x = CANVAS_WIDTH
        y = l - CANVAS_WIDTH
    else:
        x = l
        y = 0
    return (x, y)