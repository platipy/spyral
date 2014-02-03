try:
    import _path
except NameError:
    pass
import spyral
import sys

SIZE = (600, 600)
BG_COLOR = (0, 0, 0)

class DumbObject(spyral.Actor):
    def main(self, dt):
        while True:
            print "1", self.wait()
    
class StupidSprite(spyral.Sprite, spyral.Actor):
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        spyral.Actor.__init__(self)
        
        self.image = spyral.Image(size=(10, 10))
        self.image.fill((255, 255, 255))
        self.pos = (0, 0)
        self.anchor = 'center'
        
    def main(self, dt):
        right = spyral.Animation('x', spyral.easing.Linear(0, 600), duration = 1.0)
        down = spyral.Animation('y', spyral.easing.Linear(0, 600), duration = 1.0)
        left = spyral.Animation('x', spyral.easing.Linear(600, 0), duration = 1.0)
        up = spyral.Animation('y', spyral.easing.Linear(600, 0), duration = 1.0)
        while True:
            self.run_animation(right)
            self.run_animation(down)
            self.run_animation(left)
            self.run_animation(up)
         
class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.clock.max_ups = 60.
        bg = spyral.Image(size=SIZE)
        bg.fill(BG_COLOR)
        self.background = bg
        
        self.counter = DumbObject()

        def add_new_box():
            StupidSprite(self)
        add_new_box()
        
        self.register('system.quit', sys.exit)            
        self.register('input.keyboard.down', add_new_box)
        
if __name__ == "__main__":
    spyral.director.init(SIZE)
    spyral.director.run(scene=Game())
