try:
    import _path
except NameError:
    pass
import objgraph
import gc
import sys
import types
from weakref import ref as _wref
import pygame
import spyral

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

first_scene = None
class Level2(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.register("input.keyboard.down.j", self.check_first)
        self.register("system.quit", sys.exit)
    
    def check_first(self):
        global first_scene
        #first_scene.clear_all_events()
        gc.collect()
        objgraph.show_backrefs([first_scene], filename='scene.png', filter= lambda x: not isinstance(x, types.FrameType), extra_ignore = [id(locals()), id(globals())], max_depth=7)
        
class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        global first_scene
        spyral.Scene.__init__(self, SIZE)
        first_scene = self
        
        v_top = spyral.View(self)
        v_bottom = spyral.View(v_top)
        
        over = spyral.Sprite(v_bottom)
        over.image = spyral.Image(size=(50,50)).fill((255, 255, 255))
        over.should_be_dead = lambda :  10
        
        self.khan = over.should_be_dead
        self.register("system.quit", sys.exit)
        self.register("input.keyboard.down.k", over.should_be_dead)
        self.register("input.keyboard.down.j", self.advance)
    
    def advance(self):
        spyral.director.replace(Level2())

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
