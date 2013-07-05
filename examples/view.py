try:
    import _path
except NameError:
    pass
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)

        v1 = spyral.View(self)
        
        self.register("system.quit", sys.exit)

if __name__ == "__main__":
    spyral.director.init((640, 480))
    spyral.director.run(scene=Game())
