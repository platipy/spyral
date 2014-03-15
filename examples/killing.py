try:
    import _path
except NameError:
    pass
import sys
import spyral
import random

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill(BG_COLOR)

        spyral.event.register("system.quit", sys.exit)
        spyral.event.register("input.keyboard.down.f", self.kill_sprite)
        spyral.event.register("input.keyboard.down.j", self.add_sprite)
        self.test = []
    
    def add_sprite(self):
        k = spyral.Sprite(self)
        k.image = spyral.Image(size=(50,50)).fill((255, 0, 0))
        k.x = random.randint(0, 100)
        k.y = random.randint(0, 100)
        self.test.append(k)
    def kill_sprite(self):
        #for obj in self.test:
        #    obj.kill()
        self.test.pop().kill()

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
