try:
    import _path
except NameError:
    pass
import spyral
import sys

class CustomSprite(spyral.Sprite):
    def __init__(self, scene, style):
        self.__style__ = style
        spyral.Sprite.__init__(self, scene)

def make_box(color):
    return spyral.Image(size=(32,32)).fill(color)

class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self)
        self.add_style_function("make_box", make_box)
        self.load_style("style.spys")

        CustomSprite(self, "Red")
        CustomSprite(self, "Blue")
        CustomSprite(self, "Green")

        spyral.event.register("system.quit", sys.exit)


if __name__ == "__main__":
    SIZE = (640+140, 480+120)
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game()) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
