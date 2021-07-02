import math
import colorsys
import arcade

MAX_X = round(640 * 1)
MAX_Y = round(640 * 1)
detail = 14

testPosX = [[x for y in range(MAX_Y)] for x in range(MAX_X)]
testPosY = [[y for y in range(MAX_Y)] for x in range(MAX_X)]
testVelX = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
testVelY = [[1 for y in range(MAX_Y)] for x in range(MAX_X)]
testDone = [[False for y in range(MAX_Y)] for x in range(MAX_X)]
testTime = 0

pNum = 1
pRad = 32
pX = [MAX_X / 2 + pRad * math.cos(i / pNum * 2 * math.pi) for i in range(pNum + 1)]
pY = [MAX_Y / 2 + pRad * math.sin(i / pNum * 2 * math.pi) for i in range(pNum + 1)]
pMag = [1000 for i in range(pNum + 1)]
pRad = [10 for i in range(pNum + 1)]
pColor = [colorsys.hsv_to_rgb(i / pNum, 1.0, 255) for i in range(pNum + 1)]

mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
maxTime = 0
minTime = 100000

toDrawMap = False


class Canvas(arcade.Window):
    def __init__(self):
        super().__init__(MAX_X, MAX_Y, "Chart")
        arcade.set_background_color((0, 0, 0))

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()
        if toDrawMap:
            drawMap(arcade)
        else:
            drawWorld(arcade)

    def update(self, delta_time):
        mainLoop()

    def on_key_press(self, key, modifiers):
        global toDrawMap
        if key == arcade.key.SPACE:
            toDrawMap = not toDrawMap

    def on_key_release(self, key, modifiers):
        if key == arcade.key.SPACE:
            pass


def drawWorld(arc):
    for tx in range(MAX_X):
        for ty in range(MAX_Y):
            if not testDone[tx][ty]:
                if tx % detail == 0 and ty % detail == 0:
                    arc.draw_point(testPosX[tx][ty], testPosY[tx][ty], (255, 255, 255), 1)

    for p in range(pNum):
        arc.draw_circle_filled(pX[p], pY[p], pRad[p], pColor[p])


def drawMap(arc):
    for mapX in range(MAX_X):
        for mapY in range(MAX_Y):
            if mapColor[mapX][mapY] != (0, 0, 0):
                clr = mapColor[mapX][mapY]
                time = mapTime[mapX][mapY]
                factor = 1 - (time - minTime) / (maxTime - minTime) if maxTime != minTime else 1

                clr = (clr[0] * factor, clr[1] * factor, clr[2] * factor)
                arc.draw_point(mapX, mapY, clr, 1)


def mainLoop():
    global testPosX, testPosY, testVelX, testVelY, testTime

    for tx in range(MAX_X):
        for ty in range(MAX_Y):
            if not testDone[tx][ty]:
                tpx = testPosX[tx][ty]
                tpy = testPosY[tx][ty]
                tvx = 0
                tvy = 0

                for p in range(pNum):
                    disX = pX[p] - tpx
                    disY = pY[p] - tpy
                    dis = math.sqrt(disX * disX + disY * disY)
                    if dis == 0:
                        dis = 0.0001

                    if dis < pRad[p]:
                        endTest(tx, ty, pColor[p])
                        break
                    else:
                        force = pMag[p] / dis / dis / dis
                        tvx += force * disX
                        tvy += force * disY

                testVelX[tx][ty] += tvx
                testVelY[tx][ty] += tvy
                testPosX[tx][ty] += testVelX[tx][ty]
                testPosY[tx][ty] += testVelY[tx][ty]

                tpx = testPosX[tx][ty]
                tpy = testPosY[tx][ty]
                if tpx < -MAX_X or tpx > MAX_X * 2 or tpy < -MAX_Y or tpy > MAX_Y * 2:
                    endTest(tx, ty, (0, 0, 0))

    testTime += 1


def endTest(tx, ty, clr):
    global testPosX, testPosY, testVelX, testVelY
    global testTime, maxTime, minTime

    mapColor[tx][ty] = clr
    mapTime[tx][ty] = testTime
    testDone[tx][ty] = True

    if testTime > maxTime:
        maxTime = testTime
    if testTime < minTime:
        minTime = testTime


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
