import math


class Particles:
    max_x, max_y = 0, 0
    px, py = [[]], [[]]
    vx, vy = [[]], [[]]
    done = [[]]

    def __init__(self, max_x, max_y):
        self.max_x = max_x
        self.max_y = max_y

        self.px = [[x for y in range(max_y)] for x in range(max_x)]
        self.py = [[y for y in range(max_y)] for x in range(max_x)]
        self.vx = [[0 for y in range(max_y)] for x in range(max_x)]
        self.vy = [[0 for y in range(max_y)] for x in range(max_x)]
        self.done = [[False for y in range(max_y)] for x in range(max_x)]

    def draw(self, arc, detail):
        for tx in range(self.max_x):
            for ty in range(self.max_y):
                if not self.done[tx][ty]:
                    if tx % detail == 0 and ty % detail == 0:
                        arc.draw_point(self.px[tx][ty], self.py[tx][ty], (255, 255, 255), 1)

    def accelerate(self, masses, bounce):
        doneList = []
        max_x = self.max_x
        max_y = self.max_y

        for tx in range(max_x):
            for ty in range(max_y):
                if not self.done[tx][ty]:
                    tpx = self.px[tx][ty]
                    tpy = self.py[tx][ty]
                    tvx = 0
                    tvy = 0

                    for p in range(masses.num):
                        disX = masses.pX[p] - tpx
                        disY = masses.pY[p] - tpy
                        dis = math.sqrt(disX * disX + disY * disY)
                        if dis == 0:
                            dis = 0.0001

                        if dis < masses.pRad[p]:
                            doneList.append((tx, ty, masses.pColor[p], False))
                            self.done[tx][ty] = True
                            break
                        else:
                            force = masses.pMag[p] / dis / dis / dis
                            tvx += force * disX
                            tvy += force * disY

                    self.vx[tx][ty] += tvx
                    self.vy[tx][ty] += tvy
                    self.px[tx][ty] += self.vx[tx][ty]
                    self.py[tx][ty] += self.vy[tx][ty]

                    tpx = self.px[tx][ty]
                    tpy = self.py[tx][ty]

                    if bounce:
                        if tpx < 0:
                            self.px[tx][ty] = -tpx
                            self.vx[tx][ty] *= -1
                        elif tpx > max_x:
                            self.px[tx][ty] = 2 * max_x - tpx
                            self.vx[tx][ty] *= -1
                        if tpy < 0:
                            self.py[tx][ty] = -tpx
                            self.vy[tx][ty] *= -1
                        elif tpy > max_y:
                            self.py[tx][ty] = 2 * max_y - tpy
                            self.vy[tx][ty] *= -1
                    elif tpx < -max_x or tpx > max_x * 2 or tpy < -max_y or tpy > max_y * 2:
                        doneList.append((tx, ty, (0, 0, 0), True))
                        self.done[tx][ty] = True

        return doneList
