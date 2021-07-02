import arcade
from Particles import *
from Mass import *

MAX_X = 640
MAX_Y = 640

pNum = 6
wallBounce = True

particles = Particles(MAX_X, MAX_Y)
masses = Mass(MAX_X, MAX_Y, pNum)

mapColor = [[(0, 0, 0) for y in range(MAX_Y)] for x in range(MAX_X)]
mapTime = [[0 for y in range(MAX_Y)] for x in range(MAX_X)]

testTime = 0
maxTime = 0
minTime = 100000

maxTesting = (MAX_X - 1) * (MAX_Y - 1)
numTesting = maxTesting
numCollide = 0
numOut = 0

toDrawMap = False
drawParticles = 1200
detail = max(1, round(math.sqrt(numTesting / maxTesting * numTesting / drawParticles)))


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
            particles.draw(arcade, detail)
            masses.draw(arcade)

    def update(self, delta_time):
        mainLoop()

    def on_key_press(self, key, modifiers):
        global toDrawMap
        if key == arcade.key.SPACE:
            toDrawMap = not toDrawMap

    def on_key_release(self, key, modifiers):
        if key == arcade.key.SPACE:
            pass


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

    doneList = particles.accelerate(masses, wallBounce)
    if len(doneList) > 0:
        for setP in doneList:
            setMap(setP)

    testTime += 1


def setMap(particleData):
    global testTime, maxTime, minTime
    global numTesting, numCollide, numOut, detail

    tx = particleData[0]
    ty = particleData[1]
    clr = particleData[2]
    out = particleData[3]

    mapColor[tx][ty] = clr

    endTime = math.log(testTime + 1)
    mapTime[tx][ty] = endTime
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
