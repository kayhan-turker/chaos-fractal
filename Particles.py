
class Particles:
    px, py = [[]], [[]]
    vx, vy = [[]], [[]]
    collided = [[]]

    def __init__(self, nx, ny):
        self.px = [[x for y in range(ny)] for x in range(nx)]
        self.py = [[y for y in range(ny)] for x in range(nx)]
        self.vx = [[0 for y in range(ny)] for x in range(nx)]
        self.vy = [[0 for y in range(ny)] for x in range(nx)]
        self.collided = [[False for y in range(ny)] for x in range(nx)]

