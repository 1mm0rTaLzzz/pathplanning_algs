import utils


def collision(src, dst, obstacles):
    vx, vy = utils.normalize(dst.x - src.x, dst.y - src.y)
    curr = [src.x, src.y]
    while utils.dist(curr, dst) > 1:
        intCurr = int(curr[0]), int(curr[1])
        try:
            if obstacles.get_at(intCurr) == (0, 255, 255):
                return True
        except Exception:
            pass
        curr[0] += vx
        curr[1] += vy
    return False