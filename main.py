import math
import colorsys
import arcade

MAX_X = 512
MAX_Y = 512

partPX = [[x for y in range(MAX_Y)] for x in range(MAX_X)]
partPY = [[y for y in range(MAX_Y)] for x in range(MAX_X)]
partVX = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
partVY = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]
partDone = [[False for y in range(MAX_Y)] for x in range(MAX_X)]

numMass = 6
massRad = 128
massPX = [MAX_X / 2 + massRad * math.cos(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
massPY = [MAX_Y / 2 + massRad * math.sin(i / numMass * 2 * math.pi) for i in range(numMass + 1)]
massVX = [0 for i in range(numMass + 1)]
massVY = [0 for i in range(numMass + 1)]
massMag = [16, -16, 16, -16, 16, -16]
massRad = [4 for i in range(numMass + 1)]
massClr = [colorsys.hsv_to_rgb(i / numMass, 1.0, 255) for i in range(numMass + 1)]

testTime = 0
maxTime = 0
minTime = 100000
mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]

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
            disX = partPX[tx][ty] - MAX_X / 2
            disY = partPY[tx][ty] - MAX_Y / 2
            dis = math.sqrt(disX * disX + disY * disY)
            if dis > wallRadius:
                endTest(tx, ty, (0, 0, 0))


def drawWorld(arc):
    for tx in range(MAX_X):
        for ty in range(MAX_Y):
            if not partDone[tx][ty]:
                if tx % detail == 0 and ty % detail == 0:
                    arc.draw_point(partPX[tx][ty], partPY[tx][ty], (255, 255, 255), 1)

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
    global partPX, partPY, partVX, partVY, testTime

    accPart()
    accMass()

    if numTesting > 1:
        testTime += 1


def accPart():
    for tx in range(MAX_X):
        for ty in range(MAX_Y):
            if not partDone[tx][ty]:
                spx, spy, svx, svy = partPX[tx][ty], partPY[tx][ty], partVX[tx][ty], partVY[tx][ty]
                fpx, fpy, fvx, fvy = spx, spy, svx, svy

                for p in range(numMass):
                    disX = massPX[p] - spx
                    disY = massPY[p] - spy
                    dis = math.sqrt(disX * disX + disY * disY)
                    if dis == 0:
                        dis = 0.000001

                    if dis < massRad[p]:
                        endTest(tx, ty, massClr[p])
                        break
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
                elif fpx < -MAX_X or fpx > MAX_X * 2 or fpy < -MAX_Y or fpy > MAX_Y * 2:
                    endTest(tx, ty, (0, 0, 0))

                partPX[tx][ty], partPY[tx][ty], partVX[tx][ty], partVY[tx][ty] = fpx, fpy, fvx, fvy


def accMass():
    for q in range(numMass):
        fvx, fvy = massVX[q], massVY[q]

        for p in range(numMass):
            radQ = massRad[q]
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

        massPX[q], massPY[q] = fpx, fpy


def endTest(tx, ty, clr):
    global partPX, partPY, partVX, partVY
    global testTime, maxTime, minTime
    global numTesting, numDone, detail

    mapColor[tx][ty] = clr
    endTime = math.log(testTime + 1)
    mapTime[tx][ty] = endTime
    partDone[tx][ty] = True

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
