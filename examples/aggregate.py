try:
    import _path
except NameError:
    pass
import spyral
import sys
import math

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Game(spyral.Scene):
    def __init__(self, color):
        spyral.Scene.__init__(self)
        self.camera = self.parent_camera.make_child(SIZE)
        bg = spyral.Image(size=SIZE)
        bg.fill(color)
        self.camera.set_background(bg)

        self.register("system.quit", sys.exit)
        
        s = spyral.AggregateSprite()
        s.image = spyral.Image(size=(10,10)).draw_circle((255, 255, 255), (5,5), 5)
        s.pos = 300, 200
        
        a = spyral.Animation('pos', spyral.animator.Polar(center = (320, 240),
                                           radius = lambda theta: 100.0+25.0*math.sin(5.0*theta)),
                                           duration = 3.0,
                                           loop = True)
        s.animate(a)
        
        c = spyral.Sprite()
        c.image = spyral.Image(size=(10,10)).draw_circle((0, 0, 255), (5,5), 5)
        a = spyral.Animation('pos', spyral.animator.Polar(center = (0, 0),
                                            radius = lambda theta: 30),
                                            duration = 0.5,
                                            loop = True)
        c.animate(a)
        s.add_child(c)
        
        

        
if __name__ == "__main__":
    spyral.init() # Always call spyral.init() first
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game((100, 100, 100))) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
