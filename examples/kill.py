try:
    import _path
except NameError:
    pass
import pygame
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        
        i = spyral.Image(size=(50,50))
        i.fill((255, 255, 255))
        
        for x in xrange(5):
            over = spyral.Sprite(self)
            self.pos = (0, 0)
            over.image = i
            over.kill()
        
        self.register("system.quit", sys.exit)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
