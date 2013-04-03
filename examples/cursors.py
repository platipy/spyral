try:
    import _path
except NameError:
    pass
import pygame
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 128, 64)

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        back = spyral.Image(size=SIZE)
        back.fill(BG_COLOR)
        self.set_background(back)
        try:
            spyral.cursor.set_cursor(spyral.cursor.MonochromeCursor("external_cursor.xbm"))
        except ValueError, error:
            print "Correctly failed to load the bad cursor (%s)" % (error,)
        spyral.cursor.set_cursor(spyral.cursor.MonochromeCursor("valid_cursor.xbm"))
        self.register("system.quit", sys.exit)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
