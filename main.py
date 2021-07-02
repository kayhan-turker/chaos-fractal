import math
import colorsys
import arcade

MAX_X = 640
MAX_Y = 640

testPosX = [[x for y in range(MAX_Y)] for x in range(MAX_X)]
testPosY = [[y for y in range(MAX_Y)] for x in range(MAX_X)]
testVelX = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
testVelY = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
testDone = [[False for y in range(MAX_Y)] for x in range(MAX_X)]
testTime = 0

pNum = 6
pRad = 128
pX = [MAX_X / 2 + pRad * math.cos(i / pNum * 2 * math.pi) for i in range(pNum + 1)]
pY = [MAX_Y / 2 + pRad * math.sin(i / pNum * 2 * math.pi) for i in range(pNum + 1)]
pMag = [2, -2, 2, -2, 2, -2]
pRad = [2 for i in range(pNum + 1)]
pColor = [colorsys.hsv_to_rgb(i / pNum, 1.0, 255) for i in range(pNum + 1)]

mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
maxTime = 0
minTime = 100000

maxTesting = (MAX_X - 1) * (MAX_Y - 1)
numTesting = maxTesting
numCollide = 0
numOut = 0
wallBounce = True

drawParticles = 1200
detail = max(1, round(math.sqrt(numTesting / maxTesting * numTesting / drawParticles)))

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

                if wallBounce:
                    if tpx < 0:
                        testPosX[tx][ty] = -tpx
                        testVelX[tx][ty] *= -1
                    elif tpx > MAX_X:
                        testPosX[tx][ty] = 2 * MAX_X - tpx
                        testVelX[tx][ty] *= -1
                    if tpy < 0:
                        testPosY[tx][ty] = -tpx
                        testVelY[tx][ty] *= -1
                    elif tpy > MAX_Y:
                        testPosY[tx][ty] = 2 * MAX_Y - tpy
                        testVelY[tx][ty] *= -1
                elif tpx < -MAX_X or tpx > MAX_X * 2 or tpy < -MAX_Y or tpy > MAX_Y * 2:
                    endTest(tx, ty, (0, 0, 0), True)

    testTime += 1


def endTest(tx, ty, clr, out=False):
    global testPosX, testPosY, testVelX, testVelY
    global testTime, maxTime, minTime
    global numTesting, numCollide, numOut, detail

    endTime = math.log(testTime + 1)

    mapColor[tx][ty] = clr
    mapTime[tx][ty] = endTime
    testDone[tx][ty] = True

    if endTime > maxTime:
        maxTime = endTime
    if endTime < minTime:
        minTime = endTime

    numTesting -= 1
    if out:
        numOut += 1
    else:
        numCollide += 1

    if numTesting % 1000 == 0:
        print(detail, numTesting, numCollide, numOut)

    if numTesting % 1000 == 0:
        detail = max(1, round(math.sqrt(numTesting / maxTesting * numTesting / drawParticles)))



def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
