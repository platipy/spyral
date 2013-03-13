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
        spyral.Scene.__init__(self, SIZE)
        bg = spyral.Image(size=SIZE)
        bg.fill(color)
        k =spyral.Rect(160,160,640-320,480-240)
        bg.draw_rect( (0, 100, 0), k.topleft, k.size)
        self.set_background(bg)
        
        s = spyral.AggregateSprite(self)
        s.image = spyral.Image(size=(20,20)).draw_circle((255, 255, 255), (10,10), 10)
        s.pos = 300, 200
        
        a = spyral.Animation('pos', spyral.animator.Polar(center = (320, 240),
                                           radius = lambda theta: 150.0+25.0*math.sin(5.0*theta)),
                                           duration = 15.0,
                                           loop = True)
        s.animate(a)
        
        c = spyral.Sprite(self)
        c.image = spyral.Image(size=(20,20)).draw_circle((0, 0, 255), (10,10), 10)
        a = spyral.Animation('pos', spyral.animator.Polar(center = (0, 0),
                                            radius = lambda theta: 30),
                                            duration = 0.5,
                                            loop = True)
        s.add_child(c)
        c.animate(a)
        
        v = spyral.ViewPort(self)
        v.crop = k
        v.add(s)
        
        self.register("system.quit", sys.exit)


        
if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game((100, 100, 100))) # This will run your game. It will not return.
