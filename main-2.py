import math
import colorsys
import arcade

MAX_X = 512
MAX_Y = 512

defMass = 16
defRad = 4
numMass = 6
ringRad = 128

testSX = round(MAX_X / 2)
testSY = round(MAX_Y / 2)

testPX = testSX
testPY = testSY
testVX = 0
testVY = 0
testMag = defMass
testRad = defRad

massPX = [MAX_X / 2 + ringRad * math.cos(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
massPY = [MAX_Y / 2 + ringRad * math.sin(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
massVX = [0 for i in range(numMass + 1)]
massVY = [0 for i in range(numMass + 1)]
massMag = [defMass * math.cos(math.pi * i) for i in range(numMass + 1)]
massRad = [defRad for i in range(numMass + 1)]
massClr = [colorsys.hsv_to_rgb(i / numMass, 1.0, 255) for i in range(numMass + 1)]

testTime = 0
maxTime = 0
minTime = 100000
mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]

wallBounce = False
wallWrap = True
circleWall = True
wallRadius = min(MAX_X, MAX_Y) / 2

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
    disX = testSX - MAX_X / 2
    disY = testSY - MAX_Y / 2
    dis = math.sqrt(disX * disX + disY * disY)
    if dis > wallRadius:
        endTest((0, 0, 0))


def drawWorld(arc):
    arc.draw_point(testPX, testPY, (255, 255, 255), testRad)
    for p in range(numMass):
        arc.draw_circle_filled(massPX[p], massPY[p], massRad[p], massClr[p])


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
    global testTime

    accTest()
    accMass()

    testTime += 1


def accTest():
    global testPX, testPY, testVX, testVY
    spx, spy, svx, svy = testPX, testPY, testVX, testVY
    fpx, fpy, fvx, fvy = spx, spy, svx, svy

    for p in range(numMass):
        disX = massPX[p] - spx
        disY = massPY[p] - spy
        dis = math.sqrt(disX * disX + disY * disY)
        if dis == 0:
            dis = 0.000001

        if dis < massRad[p] + testRad:
            endTest(massClr[p])
            return
        else:
            force = massMag[p] / (dis * dis * dis)
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
        if circleWall:
            disX = fpx - MAX_X / 2
            disY = fpy - MAX_Y / 2
            dis = math.sqrt(disX * disX + disY * disY)
            if dis > wallRadius:
                fpx += -disX / dis * wallRadius * 2
                fpy += -disY / dis * wallRadius * 2
        else:
            if fpx < 0:
                fpx = MAX_X
            elif fpx > MAX_X:
                fpx = 0
            if fpy < 0:
                fpy = MAX_Y
            elif fpy > MAX_Y:
                fpy = 0

    testPX, testPY, testVX, testVY = fpx, fpy, fvx, fvy


def accMass():
    for q in range(numMass):
        fvx, fvy = massVX[q], massVY[q]

        radQ = massRad[q]
        # mass to mass acceleration
        for p in range(numMass):
            if p != q:
                disX = massPX[p] - massPX[q]
                disY = massPY[p] - massPY[q]
                dis = math.sqrt(disX * disX + disY * disY)
                if dis == 0:
                    dis = 0.000001

                if dis > radQ + massRad[p]:
                    force = massMag[p] / (dis * dis * dis)
                    fvx += force * disX
                    fvy += force * disY

        # mass to test acceleration
        disX = testPX - massPX[q]
        disY = testPY - massPY[q]
        dis = math.sqrt(disX * disX + disY * disY)
        if dis == 0:
            dis = 0.000001

        if dis > radQ + testRad:
            force = testMag / (dis * dis * dis)
            fvx += force * disX
            fvy += force * disY

        # sum forces
        massVX[q], massVY[q] = fvx, fvy

    for q in range(numMass):
        fpx, fpy = massPX[q], massPY[q]

        fpx += massVX[q]
        fpy += massVY[q]

        if wallBounce:
            if fpx < 0:
                fpx *= -1
                massVX[q] *= -1
            elif fpx > MAX_X:
                fpx = 2 * MAX_X - fpx
                massVX[q] *= -1
            if fpy < 0:
                fpy *= -1
                massVY[q] *= -1
            elif fpy > MAX_Y:
                fpy = 2 * MAX_Y - fpy
                massVY[q] *= -1
        elif wallWrap:
            disX = fpx - MAX_X / 2
            disY = fpy - MAX_Y / 2
            dis = math.sqrt(disX * disX + disY * disY)
            if dis > wallRadius:
                fpx += -disX / dis * wallRadius * 2
                fpy += -disY / dis * wallRadius * 2

        massPX[q], massPY[q] = fpx, fpy


def endTest(clr):
    global testSX, testSY
    global testPX, testPY, testVX, testVY
    global massPX, massPY, massVX, massVY
    global testTime, maxTime, minTime

    print(testSX, testSY, "DONE")

    mapColor[testSX][testSY] = clr
    testTime = math.log(testTime + 1)
    mapTime[testSX][testSY] = testTime

    if testTime > maxTime:
        maxTime = testTime
    if testTime < minTime:
        minTime = testTime

    testTime = 0

    massPX = [MAX_X / 2 + ringRad * math.cos(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
    massPY = [MAX_Y / 2 + ringRad * math.sin(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
    massVX = [0 for i in range(numMass + 1)]
    massVY = [0 for i in range(numMass + 1)]

    testSX += 2
    if testSX >= MAX_X:
        testSX = 0
        testSY += 2
        if testSX >= MAX_X:
            testSY = 0

    testPX = testSX
    testPY = testSY
    testVX = 0
    testVY = 0

    checkDone()


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
