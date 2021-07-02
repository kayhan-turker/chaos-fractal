import math
import colorsys


class Mass:
    num = 0
    px, py = [], []
    pMag, pRad, pColor = [], [], []

    def __init__(self, max_x, max_y, num):
        self.num = num
        radius = 128

        self.pX = [max_x / 2 + radius * math.cos(i / num * 2 * math.pi) for i in range(num + 1)]
        self.pY = [max_y / 2 + radius * math.sin(i / num * 2 * math.pi) for i in range(num + 1)]
        self.pMag = [2, -2, 2, -2, 2, -2]
        self.pRad = [2 for i in range(num + 1)]
        self.pColor = [colorsys.hsv_to_rgb(i / num, 1.0, 255) for i in range(num + 1)]

    def draw(self, arc):
        for p in range(self.num):
            arc.draw_circle_filled(self.pX[p], self.pY[p], self.pRad[p], self.pColor[p])

