import arcade
from Particles import Particles
from Mass import Mass
from Map import Map

MAX_X = 640
MAX_Y = 640

pNum = 6
wallBounce = True

particles = Particles(MAX_X, MAX_Y)
masses = Mass(MAX_X, MAX_Y, pNum)
fieldMap = Map(MAX_X, MAX_Y)

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
            fieldMap.draw(arcade)
        else:
            particles.draw(arcade)
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


def mainLoop():
    particles.accelerate(masses, fieldMap, wallBounce)


def main():
    canv = Canvas()
    canv.setup()
    arcade.run()


if __name__ == "__main__":
    main()
