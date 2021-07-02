import math
import colorsys
import arcade

MAX_X = round(640 * 1)
MAX_Y = round(640 * 1)

testStartX = 0
testStartY = 0
testTime = 0
timeOut = 0
timeLimit = 500

testPosX = testStartX
testPosY = testStartY
testVelX = 0
testVelY = 0

pNum = 3
pRad = 128
pX = [MAX_X / 2 + pRad * math.cos(i / pNum * 2 * math.pi) for i in range(pNum + 1)]
pY = [MAX_Y / 2 + pRad * math.sin(i / pNum * 2 * math.pi) for i in range(pNum + 1)]
pMag = [1000 for i in range(pNum + 1)]
pRad = [10 for i in range(pNum + 1)]
pColor = [colorsys.hsv_to_rgb(i / pNum, 1.0, 255) for i in range(pNum + 1)]

mapColor = [[(0, 0, 0) for x in range(MAX_X)] for y in range(MAX_Y)]
mapTime = [[0 for x in range(MAX_X)] for y in range(MAX_Y)]
maxTime = 0
minTime = 10000

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
        global toDrawMap, toDraw
        if key == arcade.key.SPACE:
            toDrawMap = not toDrawMap

    def on_key_release(self, key, modifiers):
        if key == arcade.key.SPACE:
            pass


def drawWorld(arc):
    arc.draw_point(testPosX, testPosY, (255, 255, 255), 1)
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
    global testPosX, testPosY, testVelX, testVelY, testTime, timeOut

    for p in range(pNum):
        disX = pX[p] - testPosX
        disY = pY[p] - testPosY
        dis = math.sqrt(disX * disX + disY * disY)
        if dis == 0:
            dis = 0.001

        if dis < pRad[p]:
            nextTest(pColor[p])
            break

        if dis > pRad[p]:
            dis = math.sqrt(disX * disX + disY * disY)
            force = pMag[p] / dis / dis / dis
            testVelX += force * disX
            testVelY += force * disY

    testPosX += testVelX
    testPosY += testVelY

    testTime += 1
    if testPosX < 0 or testPosX > MAX_X or testPosY < 0 or testPosY > MAX_Y:
        timeOut += 1
    if timeOut > timeLimit:
        nextTest((0, 0, 0), True)


def getForce(disX, disY, mag):
    dis = math.sqrt(disX * disX + disY * disY)
    force = mag / dis / dis / dis
    return force * disX, force * disY


def nextTest(clr, out=False):
    global testPosX, testPosY, testVelX, testVelY
    global testStartX, testStartY, testTime, timeOut, maxTime, minTime

    print("done", testStartX, testStartY)

    if out:
        testTime -= timeOut
    mapColor[testStartX][testStartY] = clr
    mapTime[testStartX][testStartY] = testTime

    testStartX += 2
    if testStartX >= MAX_X:
        testStartX = 0
        testStartY += 2
        if testStartY >= MAX_Y:
            testStartX = 0
            testStartY = 0

    if testTime > maxTime:
        maxTime = testTime
    if testTime < minTime:
        minTime = testTime
    testTime = 0
    timeOut = 0

    testPosX = testStartX
    testPosY = testStartY
    testVelX = 0
    testVelY = 0


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
