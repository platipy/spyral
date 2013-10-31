try:
    import _path
except NameError:
    pass
import spyral
from spyral.animation import Animation, DelayAnimation
import spyral.animator as animator
import sys
import math
import itertools

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 255, 0)
GREEN = (0, 0, 255)
SMALL = (40, 40)

a1 = spyral.Animation('y', animator.Sine(amplitude = 20.0), duration = 3.0, shift= 240)
a2 = spyral.Animation('x', animator.Linear(280, 360), duration = 3.0)
a3 = spyral.Animation('x', animator.Linear(360, 280), duration = 3.0)
a4 = spyral.Animation('y', animator.Sine(amplitude = -20.0), duration = 3.0, shift= 240)
for a in [a1,a2,a3,a4]: a.loop = True

class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill(BG_COLOR)
        
        top_view = spyral.View(self)
        bottom_view = spyral.View(top_view)
        self.red_block = spyral.Sprite(bottom_view)
        self.red_block.image = spyral.Image(size=SMALL).fill(RED)
        self.red_block.pos = (320, 240)
        
        self.blue_block = spyral.Sprite(bottom_view)
        self.blue_block.image = spyral.Image(size=SMALL).fill(BLUE)
        self.blue_block.pos = (320, 260)
        
        self.green_block = spyral.Sprite(top_view)
        self.green_block.image = spyral.Image(size=SMALL).fill(GREEN)
        self.green_block.pos = (320, 260)
        
        self.yellow_block = spyral.Sprite(self)
        self.yellow_block.image = spyral.Image(size=SMALL).fill(YELLOW)
        self.yellow_block.pos = (320, 260)
        
        blocks = {self.red_block : a1, 
                  self.blue_block: a2, 
                  self.green_block: a3, 
                  self.yellow_block: a4}
        self.paused = itertools.cycle(blocks.keys())
        def advance_pauser(event):
            skip = next(self.paused)
            for block, animation in blocks.iteritems():
                block.stop_all_animations()
                if block is not skip:
                    block.animate(animation)
        
        def key_down(event): top_view.y += 10
        def key_up(event): top_view.y -= 10
        def key_left(event): top_view.x -= 10
        def key_right(event): top_view.x += 10
    
        self.register("input.keyboard.down.down", key_down)
        self.register("input.keyboard.down.up", key_up)
        self.register("input.keyboard.down.left", key_left)
        self.register("input.keyboard.down.right", key_right)
        self.register("input.keyboard.down.space", advance_pauser)
        self.register("system.quit", sys.exit)

if __name__ == "__main__":
    spyral.director.init((640, 480))
    spyral.director.run(scene=Game())
