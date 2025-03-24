import math


def normalize(vx, vy):
    norm = math.sqrt(vx * vx + vy * vy)
    if norm > 1e-6:
        vx /= norm
        vy /= norm
    return vx, vy


def dist(p1, p2):
    return math.hypot(p2.x - p1[0], p2.y - p1[1])


