try:
    import _path
except NameError:
    pass
import pygame
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 128, 64)

# List of cursors from documentation
cursors = ["arrow", "diamond", "x", "left", "right"]

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        back = spyral.Image(size=SIZE)
        back.fill(BG_COLOR)
        self.background = back
        self.mouse = iter(cursors) # iterator over the cursors!
        spyral.event.register("system.quit", sys.exit)
        spyral.event.register("input.mouse.down.left", self.advance_mouse)
    
    def advance_mouse(self):
        try:
            # Change the cursor
            spyral.mouse.cursor = self.mouse.next()
        except StopIteration, e:
            self.mouse = iter(cursors)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
