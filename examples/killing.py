try:
    import _path
except NameError:
    pass
import sys
import spyral
import random
import objgraph
import types
import gc

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
        k.gs = global_simple
        k.bb = lambda : sys.exit(k)
        k.gb = global_bound(k.image, k.rect, k, k, p=k.image, j=k)
        spyral.event.register("#.global.simple", k.gs)
        spyral.event.register("#.builtin.bound", k.bb)
        spyral.event.register("#.global.bound", k.gb)
        def local_simple():
            return 5
        def local_bound(obj):
            return lambda : obj
        def local_self():
            return lambda : k
        k.lsi = local_simple
        k.lb = local_bound(k)
        k.lse = local_self
        spyral.event.register("#.local.bound", k.lb)
        spyral.event.register("#.local.self", k.lse)
        spyral.event.register("#.local.simple", k.lsi)
        spyral.event.register("#.class.simple", k.kill)
        self.test.append(k)
        print "B", len(self._handlers)
        for name, handlers in self._handlers.iteritems():
            print "B", name, [h[0] for h in handlers]
        print "*" * 10
        #print "ADD", len(gc.get_objects())
    def kill_sprite(self):
        k = self.test.pop()
        k.kill()
        print "A", len(self._handlers)
        for name, handlers in self._handlers.iteritems():
            print "A", name, [h[0] for h in handlers]
        spyral.event.unregister("#.local.bound", k.lb)
        spyral.event.unregister("#.local.self", k.lse)
        spyral.event.unregister("#.local.simple", k.lsi)
        spyral.event.unregister("#.global.simple", k.gs)
        spyral.event.unregister("#.global.bound", k.gb)
        spyral.event.unregister("#.builtin.bound", k.bb)
        print "C", len(self._handlers)
        for name, handlers in self._handlers.iteritems():
            print "C", name, [h[0] for h in handlers]
        #print "KILL", len(gc.get_objects())
        #objgraph.show_backrefs([k], filename='killing-self.png', filter= lambda x: not isinstance(x, types.FrameType), extra_ignore = [id(locals()), id(globals())], max_depth=7)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
