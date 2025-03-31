import math


def normalize(vx, vy):
    norm = math.sqrt(vx * vx + vy * vy)
    if norm > 1e-6:
        vx /= norm
        vy /= norm
    return vx, vy


def dist(p1, p2):
    """Вычисляет евклидово расстояние между двумя точками"""
    if hasattr(p2, 'x') and hasattr(p2, 'y'):
        return math.hypot(p2.x - p1[0], p2.y - p1[1])
    elif hasattr(p1, 'x') and hasattr(p1, 'y') and hasattr(p2, 'x') and hasattr(p2, 'y'):
        return math.hypot(p2.x - p1.x, p2.y - p1.y)
    else:
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def cost(node):
    """Вычисляет стоимость пути от корня до данного узла"""
    cost = 0
    current = node
    while current.parent is not None:
        cost += math.hypot(current.x - current.parent.x, current.y - current.parent.y)
        current = current.parent
    return cost 