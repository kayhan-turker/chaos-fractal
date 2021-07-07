import math
import colorsys
import arcade
import numpy
from PIL import Image

preview = True
MAX_X = round(512 / (2 if preview else 1))
MAX_Y = round(512 / (2 if preview else 1))

testMag = 16
testRad = 4
defMass = 16
defRad = 4
numMass = 3
ringRad = 32
alternateMass = False

wallBounce = False
wallWrap = False
circleWall = False
wallRadius = min(MAX_X, MAX_Y) / 2

testPX = [[x for y in range(MAX_Y)] for x in range(MAX_X)]
testPY = [[y for y in range(MAX_Y)] for x in range(MAX_X)]
testVX = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
testVY = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
testRun = [[True for y in range(MAX_Y)] for x in range(MAX_X)]

massPX = [[[MAX_X / 2 + ringRad * math.cos(i / numMass * 2 * math.pi)
            for y in range(MAX_Y)] for x in range(MAX_X)] for i in range(numMass + 1)]
massPY = [[[MAX_Y / 2 + ringRad * math.sin(i / numMass * 2 * math.pi)
            for y in range(MAX_Y)] for x in range(MAX_X)] for i in range(numMass + 1)]
massVX = [[[0 for i in range(numMass + 1)
            for y in range(MAX_Y)] for x in range(MAX_X)] for i in range(numMass + 1)]
massVY = [[[0 for i in range(numMass + 1)
            for y in range(MAX_Y)] for x in range(MAX_X)] for i in range(numMass + 1)]
massMag = [defMass * math.cos((1 if alternateMass else 2) * math.pi * i) for i in range(numMass + 1)]
massRad = [defRad for i in range(numMass + 1)]
massClr = [colorsys.hsv_to_rgb(i / numMass, 1.0, 255) for i in range(numMass + 1)]

testTime = 0
maxTime = 0
minTime = 100000
mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0.0 for y in range(MAX_Y)] for x in range(MAX_X)]

mapArray = numpy.empty((MAX_Y, MAX_X, 3), dtype=numpy.uint8)
mapImage = Image.fromarray(mapArray, 'RGB')

testMax = MAX_X * MAX_Y
testLeft = testMax
testDone = 0

frameTimer = 0
frameInterval = 10
typeName = ""


class Canvas(arcade.Window):
    def __init__(self):
        super().__init__(MAX_X, MAX_Y, "Chart")
        arcade.set_background_color((0, 0, 0))

    def setup(self):
        if preview:
            halfDimensions()
        checkDone()
        if not preview:
            getTypeName()

    def on_draw(self):
        arcade.start_render()
        drawWorld(arcade)

    def update(self, delta_time):
        mainLoop()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            getImage()


def mainLoop():
    global testTime, testLeft, frameTimer, frameInterval

    accTest()
    accMass()

    if testLeft > 0:
        testTime += 1

    if not preview:
        if frameTimer % frameInterval == 0:
            getImage(False)
        frameTimer += 1


def halfDimensions():
    global ringRad, wallRadius, testMag, testRad, massMag, massRad
    ringRad = round(ringRad / 2)
    wallRadius = round(wallRadius / 2)
    testRad = round(testRad / 2)
    for p in range(numMass):
        massRad[p] = round(massRad[p] / 2)


def checkDone():
    for x in range(MAX_X):
        for y in range(MAX_Y):
            if circleWall:
                disX = testPX[x][y] - MAX_X / 2
                disY = testPY[x][y] - MAX_Y / 2
                dis = math.sqrt(disX * disX + disY * disY)
                if dis > wallRadius:
                    endTest(x, y, (0, 0, 0))


def drawWorld(arc):
    if testLeft > 0:
        for x in range(MAX_X):
            for y in range(MAX_Y):
                if testRun[x][y]:
                    arc.draw_circle_filled(testPX[x][y], testPY[x][y], testRad, (255, 255, 255))
                    for p in range(numMass):
                        arc.draw_circle_filled(massPX[p][x][y], massPY[p][x][y], massRad[p], massClr[p])
                    return


def getImage(display=True):
    getMap()
    if not preview:
        doneRatio = testDone / (testLeft + testDone)
        fileName = 'chaos-fractal-%s-%0.2f-%i.png' % (typeName, doneRatio, frameTimer / frameInterval) \
            if frameTimer % frameInterval == 0 else \
            'chaos-fractal-%s-%0.2f-%0.2f.png' % (typeName, doneRatio, frameTimer / frameInterval)
        mapImage.save(fileName)
    if display:
        mapImage.show()


def getMap():
    global mapArray, mapImage

    mapArray = numpy.empty((MAX_Y, MAX_X, 3), dtype=numpy.uint8)
    for mapX in range(MAX_X):
        for mapY in range(MAX_Y):
            clr = mapColor[mapX][mapY]
            time = mapTime[mapX][mapY]
            factor = 1 - (time - minTime) / (maxTime - minTime) if maxTime != minTime else 1
            clr = (clr[0] * factor, clr[1] * factor, clr[2] * factor)

            mapArray[MAX_Y - mapY - 1, mapX] = [clr[0], clr[1], clr[2]]

    mapImage = Image.fromarray(mapArray, 'RGB')


def getTypeName():
    global typeName
    typeName += 'C' if circleWall else 'S'
    typeName += 'R' if wallWrap else 'B' if wallBounce else ''
    numPos = 0
    for p in range(numMass):
        if massMag[p] >= 0:
            numPos += 1
    typeName += str(numPos)
    typeName += str((numMass - numPos))
    if testMag < 0:
        typeName += 'R'


def accTest():
    global testPX, testPY, testVX, testVY

    for x in range(MAX_X):
        for y in range(MAX_Y):
            if testRun[x][y]:
                spx, spy, svx, svy = testPX[x][y], testPY[x][y], testVX[x][y], testVY[x][y]
                fpx, fpy, fvx, fvy = spx, spy, svx, svy

                for p in range(numMass):
                    dvx, dvy = accelerate(spx, spy, massPX[p][x][y], massPY[p][x][y],
                                          massRad[p] + testRad, massMag[p])
                    if dvx == 0 and dvy == 0:
                        endTest(x, y, massClr[p])
                        break
                    else:
                        fvx += dvx
                        fvy += dvy

                fpx += fvx
                fpy += fvy

                testPX[x][y], testPY[x][y], testVX[x][y], testVY[x][y] = collide(fpx, fpy, fvx, fvy)


def accMass():
    for x in range(MAX_X):
        for y in range(MAX_Y):
            if testRun[x][y]:
                for q in range(numMass):
                    fpx, fpy, fvx, fvy = massPX[q][x][y], massPY[q][x][y], massVX[q][x][y], massVY[q][x][y]

                    radQ = massRad[q]
                    for p in range(numMass):
                        if p != q:
                            dvx, dvy = accelerate(fpx, fpy, massPX[p][x][y], massPY[p][x][y],
                                                  radQ + massRad[p], massMag[p])
                            fvx += dvx
                            fvy += dvy

                    dvx, dvy = accelerate(fpx, fpy, testPX[x][y], testPY[x][y],
                                          radQ + testRad, testMag)
                    fvx += dvx
                    fvy += dvy

                    massVX[q][x][y], massVY[q][x][y] = fvx, fvy

                for q in range(numMass):
                    fpx, fpy, fvx, fvy = massPX[q][x][y], massPY[q][x][y], massVX[q][x][y], massVY[q][x][y]

                    fpx += fvx
                    fpy += fvy

                    massPX[q][x][y], massPY[q][x][y], massVX[q][x][y], massVY[q][x][y] = collide(fpx, fpy, fvx, fvy)


def accelerate(px, py, qx, qy, rad, mass):
    disX = qx - px
    disY = qy - py
    dis = math.sqrt(disX * disX + disY * disY)
    if dis == 0:
        dis = 0.000001

    if dis > rad:
        force = mass / (dis * dis * dis)
        return force * disX, force * disY
    return 0, 0


def collide(px, py, vx, vy):
    if wallBounce:
        if px < 0:
            px *= -1
            vx *= -1
        elif px > MAX_X:
            px = 2 * MAX_X - px
            vx *= -1
        if py < 0:
            py *= -1
            vy *= -1
        elif py > MAX_Y:
            py = 2 * MAX_Y - py
            vy *= -1
    elif wallWrap:
        if circleWall:
            disX = px - MAX_X / 2
            disY = py - MAX_Y / 2
            dis = math.sqrt(disX * disX + disY * disY)
            if dis > wallRadius:
                px += -disX / dis * wallRadius * 2
                py += -disY / dis * wallRadius * 2
        else:
            if px < 0:
                px = MAX_X
            elif px > MAX_X:
                px = 0
            if py < 0:
                py = MAX_Y
            elif py > MAX_Y:
                py = 0

    return px, py, vx, vy


def endTest(x, y, clr):
    global testPX, testPY, testVX, testVY
    global massPX, massPY, massVX, massVY
    global testTime, maxTime, minTime, testDone, testLeft, frameTimer, frameInterval

    mapColor[x][y] = clr
    endTime = math.log(testTime + 1)
    mapTime[x][y] = endTime

    if endTime > maxTime:
        maxTime = endTime
    if endTime < minTime:
        minTime = endTime

    testRun[x][y] = False
    testLeft -= 1
    testDone += 1

    if testLeft % 100 == 0:
        print("test left vs done:", testLeft, testDone, round(testDone / (testDone + testLeft) * 100) / 100,
              "\tframe timer:", frameTimer, frameInterval, frameTimer / frameInterval)


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
