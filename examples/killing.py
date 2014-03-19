try:
    import _path
except NameError:
    pass
import sys
import spyral
import random
import objgraph
import types

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

def global_simple():
    return 5
def global_bound(param, second, *objs, **obj):
    return lambda : (param, second, objs, obj)

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
        spyral.event.register("#.global.simple", global_simple)
        spyral.event.register("#.builtin.bound", lambda : sys.exit(k))
        spyral.event.register("#.global.bound", global_bound(k.image, k.rect, k, k, p=k.image, j=k))
        def local_simple():
            return 5
        def local_bound(obj):
            return lambda : obj
        def local_self():
            return lambda : k
        spyral.event.register("#.local.bound", local_bound(k))
        spyral.event.register("#.local.self", local_self)
        spyral.event.register("#.local.simple", local_simple)
        spyral.event.register("#.class.simple", k.kill)
        self.test.append(k)
    def kill_sprite(self):
        k = self.test.pop()
        k.kill()
        objgraph.show_backrefs([k], filename='killing-self.png', filter= lambda x: not isinstance(x, types.FrameType), extra_ignore = [id(locals()), id(globals())], max_depth=7)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
