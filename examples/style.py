try:
    import _path
except NameError:
    pass
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)


class CustomSprite(spyral.Sprite):
    def __init__(self):
        spyral.Sprite.__init__(self)
        self.image = spyral.Image(size=(30, 30))
        self.image.fill((255, 0, 0))


class Game(spyral.Scene):
    def __init__(self, color):
        spyral.Scene.__init__(self)
        self.camera = self.parent_camera.make_child(SIZE)
        bg = spyral.Image(size=SIZE)
        bg.fill(color)
        self.camera.set_background(bg)

        self.load_style("style.spys")

        CustomSprite()

        self.register("system.quit", sys.exit)


if __name__ == "__main__":
    spyral.init() # Always call spyral.init() first
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game((100, 100, 100))) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
