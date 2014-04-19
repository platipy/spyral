try:
    import _path
except NameError:
    pass
import objgraph
import gc
import types
from weakref import ref as _wref
import pygame
import spyral

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

first_scene = None
old_sprite = None
class Level2(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill(BG_COLOR)        
        test = Sprite(self)
        test.image = spyral.Image(size=(32,32)).fill((255, 255, 255))
        test.pos = (32, 32)
        
        spyral.event.register("input.keyboard.down.j", self.check_first)
        spyral.event.register("system.quit", spyral.director.quit)

    def check_first(self):
        global first_scene
        global old_sprite
        #first_scene.clear_all_events()
        gc.collect()
        objgraph.show_backrefs([old_sprite], filename='sprite-old.png', filter= lambda x: not isinstance(x, types.FrameType), extra_ignore = [id(locals()), id(globals())], max_depth=7)
        old_sprite.kill()
        objgraph.show_backrefs([old_sprite], filename='sprite-dead.png', filter= lambda x: not isinstance(x, types.FrameType), extra_ignore = [id(locals()), id(globals())], max_depth=7)


    def advance(self):
        spyral.director.replace(Game())

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        global first_scene
        global old_sprite
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill(BG_COLOR)
        first_scene = self

        v_top = spyral.View(self)
        v_bottom = spyral.View(v_top)

        over = spyral.Sprite(v_bottom)
        over.image = spyral.Image(size=(50,50)).fill((255, 0, 0))
        over.should_be_dead = lambda :  10
        old_sprite = over

        self.khan = over.should_be_dead
        spyral.event.register("system.quit", spyral.director.quit)
        spyral.event.register("input.keyboard.down.k", over.should_be_dead)
        spyral.event.register("input.keyboard.down.e", over._get_mask)
        spyral.event.register("input.keyboard.down.j", self.advance)

        objgraph.show_backrefs([old_sprite], filename='sprite-alive.png', filter= lambda x: not isinstance(x, types.FrameType), extra_ignore = [id(locals()), id(globals())], max_depth=7)

    def advance(self):
        spyral.director.push(Level2())

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
