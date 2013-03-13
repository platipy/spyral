try:
    import _path
except NameError:
    pass
import spyral
import sys

class CustomSprite(spyral.Sprite):
    pass

class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self)
        self.load_style("style.spys")

        CustomSprite(self)

        self.register("system.quit", sys.exit)


if __name__ == "__main__":
    SIZE = (640, 480)
    spyral.init() # Always call spyral.init() first
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game()) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
