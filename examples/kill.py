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
        
        v_top = spyral.View(self)
        v_bottom = spyral.View(v_top)
        
        import objgraph
        over = spyral.Sprite(v_bottom)
        self.pos = (0, 0)
        over.image = i
        #over.kill()
        v_top.kill()
        del over
        objgraph.show_backrefs([v_top], filename='sample-graph.png')
        
        self.register("system.quit", sys.exit)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
