import math
import colorsys
import random

import arcade

MAX_X = 512
MAX_Y = 512

testMag = 16
testRad = 4
defMass = -16
defRad = 4
numMass = 1
ringRad = 0
altMag = True

wallBounce = False
wallWrap = True
circleWall = False
wallRadius = min(MAX_X, MAX_Y) / 2

testSX = round(MAX_X / 2)
testSY = round(MAX_Y / 2)
testPX = testSX
testPY = testSY
testVX = 0
testVY = 0

massPX = [0 for i in range(numMass + 1)]
massPY = [0 for i in range(numMass + 1)]
massVX = [0 for i in range(numMass + 1)]
massVY = [0 for i in range(numMass + 1)]
massMag = [defMass * math.cos(math.pi * i * (2 if not altMag else 1)) for i in range(numMass + 1)]
massRad = [defRad for i in range(numMass + 1)]
massClr = [colorsys.hsv_to_rgb(i / numMass, 1.0, 255) for i in range(numMass + 1)]

selectMode = True
moveSX, moveSY = 0, 0


class Canvas(arcade.Window):
    def __init__(self):
        super().__init__(MAX_X, MAX_Y, "Placement v1")
        arcade.set_background_color((0, 0, 0))

    def setup(self):
        resetWorld()

    def on_draw(self):
        arcade.start_render()
        drawWorld(arcade)

    def update(self, delta_time):
        mainLoop()
        if selectMode:
            moveStart()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE:
            if selectMode:
                startWorld()
                checkDone()
            else:
                endTest()
        if selectMode:
            checkMoveStart(arcade, key)

    def on_key_release(self, key, modifiers):
        checkMoveStart(arcade, key, True)


def resetWorld():
    global testPX, testPY, testVX, testVY
    global massPX, massPY, massVX, massVY, selectMode

    massPX = [MAX_X / 2 + ringRad * math.cos(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
    massPY = [MAX_Y / 2 + ringRad * math.sin(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
    massVX = [0 for i in range(numMass + 1)]
    massVY = [0 for i in range(numMass + 1)]

    testPX = testSX
    testPY = testSY
    testVX = 0
    testVY = 0

    selectMode = True


def startWorld():
    global testPX, testPY, testVX, testVY, selectMode

    selectMode = False


def moveStart():
    global moveSX, moveSY, testSX, testSY, testPX, testPY

    testSX += moveSX
    testSY += moveSY
    testPX = testSX
    testPY = testSY


def checkMoveStart(arc, key, release=False):
    global moveSX, moveSY

    if not release:
        if key == arc.key.D:
            moveSX = 1
        if key == arc.key.A:
            moveSX = -1
        if key == arc.key.W:
            moveSY = 1
        if key == arc.key.S:
            moveSY = -1
    else:
        if key == arc.key.D or key == arc.key.A:
            moveSX = 0
        if key == arc.key.W or key == arc.key.S:
            moveSY = 0


def checkDone():
    disX = testPX - MAX_X / 2
    disY = testPY - MAX_Y / 2
    dis = math.sqrt(disX * disX + disY * disY)
    if dis > wallRadius:
        endTest()


def drawWorld(arc):
    arc.draw_point(testPX, testPY, (255, 255, 255), testRad)
    for p in range(numMass):
        arc.draw_circle_filled(massPX[p], massPY[p], massRad[p], massClr[p])


def mainLoop():
    if not selectMode:
        accTest()
        accMass()


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
            endTest()
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


def endTest():
    global testPX, testPY, testVX, testVY
    global massPX, massPY, massVX, massVY

    resetWorld()


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
