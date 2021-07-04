import math
import colorsys
import arcade

MAX_X = 512
MAX_Y = 512

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
pMag = [16, -16, 16, -16, 16, -16]
pRad = [4 for i in range(pNum + 1)]
pColor = [colorsys.hsv_to_rgb(i / pNum, 1.0, 255) for i in range(pNum + 1)]

mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
maxTime = 0
minTime = 100000

maxTesting = MAX_X * MAX_Y
numTesting = maxTesting
numDone = 0

wallBounce = False
wallWrap = True
circleWall = True
wallRadius = min(MAX_X, MAX_Y) / 2

drawParticles = 256
detail = 1

toDrawMap = False


class Canvas(arcade.Window):
    def __init__(self):
        super().__init__(MAX_X, MAX_Y, "Chart")
        arcade.set_background_color((0, 0, 0))

    def setup(self):
        checkDone()

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


def checkDone():
    for tx in range(MAX_X):
        for ty in range(MAX_Y):
            disX = testPosX[tx][ty] - MAX_X / 2
            disY = testPosY[tx][ty] - MAX_Y / 2
            dis = math.sqrt(disX * disX + disY * disY)
            if dis > wallRadius:
                endTest(tx, ty, (0, 0, 0))


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

    accPart()
    accMass()

    if numTesting > 1:
        testTime += 1


def accPart():
    for tx in range(MAX_X):
        for ty in range(MAX_Y):
            if not testDone[tx][ty]:
                spx, spy, svx, svy = testPosX[tx][ty], testPosY[tx][ty], testVelX[tx][ty], testVelY[tx][ty]
                fpx, fpy, fvx, fvy = spx, spy, svx, svy

                for p in range(pNum):
                    disX = pX[p] - spx
                    disY = pY[p] - spy
                    dis = math.sqrt(disX * disX + disY * disY)
                    if dis == 0:
                        dis = 0.000001

                    if dis < pRad[p]:
                        endTest(tx, ty, pColor[p])
                        break
                    else:
                        force = pMag[p] / (dis * dis * dis)
                        fvx += force * disX
                        fvy += force * disY

                fpx += fvx
                fpy += fvy

                if wallBounce:
                    if fpx < 0:
                        fpx *= -1
                        fvx *= -1
                    elif fpx > MAX_X:
                        fpx = 2 * MAX_X - fpx
                        fvx *= -1
                    if fpy < 0:
                        fpy *= -1
                        fvy *= -1
                    elif fpy > MAX_Y:
                        fpy = 2 * MAX_Y - fpy
                        fvy *= -1
                elif wallWrap:
                    disX = fpx - MAX_X / 2
                    disY = fpy - MAX_Y / 2
                    dis = math.sqrt(disX * disX + disY * disY)
                    if dis > wallRadius:
                        fpx += -disX / dis * wallRadius * 2
                        fpy += -disY / dis * wallRadius * 2
                elif fpx < -MAX_X or fpx > MAX_X * 2 or fpy < -MAX_Y or fpy > MAX_Y * 2:
                    endTest(tx, ty, (0, 0, 0))

                testPosX[tx][ty], testPosY[tx][ty], testVelX[tx][ty], testVelY[tx][ty] = fpx, fpy, fvx, fvy


def endTest(tx, ty, clr):
    global testPosX, testPosY, testVelX, testVelY
    global testTime, maxTime, minTime
    global numTesting, numDone, detail

    mapColor[tx][ty] = clr
    endTime = math.log(testTime + 1)
    mapTime[tx][ty] = endTime
    testDone[tx][ty] = True

    if endTime > maxTime:
        maxTime = endTime
    if endTime < minTime:
        minTime = endTime

    numTesting -= 1
    numDone += 1

    if numTesting % 1000 == 0:
        detail = max(1, round(1 / math.sqrt(drawParticles / numTesting)))

    if numTesting % 100 == 0:
        print (numTesting, numDone, detail)


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
