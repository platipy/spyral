try:
    import _path
except NameError:
    pass
import spyral
from spyral.animation import Animation, DelayAnimation
import spyral.easing as easing
import math
import itertools

SIZE = (480, 480)
BG_COLOR = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 255, 0)
GREEN = (0, 0, 255)
SMALL = (40, 40)

go_down = spyral.Animation('y', easing.Linear(0, 80), duration = 1.0)
go_down += spyral.Animation('y', easing.Linear(80, 0), duration = 1.0)
go_down.loop = True

go_up = spyral.Animation('y', easing.Linear(160, 0), duration = 2.0)
go_left = spyral.Animation('x', easing.Linear(0, 160), duration = 2.0)
go_right = spyral.Animation('x', easing.Linear(160, 0), duration = 2.0)

# Object inside View
# Object shifted by View
# Object cropped by View
# Object scaled by View
# Object shifted and scaled by View
# Object shifted, scaled and cropped by View

# Object <- View <- View <- Scene
# Object <- View (Shifted) <- View <- Scene
# Object <- View (Shifted) <- View (Shifted) <- Scene
# Object <- View (Scaled up) <- View (Scaled up) <- Scene
# Object <- View (Cropped) <- View (Cropped) <- Scene
# Object <- View (Scaled) <- View (Cropped) <- Scene
# Object <- View (Cropped) <- View (Scaled) <- Scene

class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill(BG_COLOR)
        screen = self.rect

        debug = spyral.DebugText(self, "1) Red square in middle of room", BLUE)
        debug.anchor = 'midbottom'
        debug.pos = self.rect.midbottom

        self.top_view = spyral.View(self)
        self.top_view.label = "TopV"
        self.top_view.pos = (0, 0)
        # TODO: To see it flip out, try commenting out the next line.
        self.top_view.crop = False
        self.top_view.crop_size = (40, 40)

        self.bottom_view = spyral.View(self.top_view)
        self.bottom_view.label = "BottomV"
        self.bottom_view.pos = (0,0)
        self.bottom_view.crop = False
        self.bottom_view.crop_size = (20, 20)

        self.red_block = spyral.Sprite(self.bottom_view)
        self.red_block.image = spyral.Image(size=SMALL).fill(RED)
        self.red_block.pos = screen.center
        self.red_block.anchor = "center"

        def tester():
            debug.text = "2) Red square partially offscreen"
            self.red_block.pos = screen.midtop
            yield
            debug.text = "3) Red square doubled in size"
            self.red_block.pos = screen.center
            self.red_block.scale = 2
            yield
            debug.text = "4) Red square angled .1 radians"
            self.red_block.angle = .1
            yield
            debug.text = "5) Red square shifted by bottom view 16px diagonal"
            self.bottom_view.pos = (16, 16)
            yield
            debug.text = "6) Red square half scaled by bottom view"
            self.bottom_view.scale = .5
            yield
            debug.text = "7) Red square doubled by top view"
            self.top_view.scale = 2
            yield
            debug.text = "8) Red square shifted by top view in other direction 8x"
            self.top_view.pos = (-8, -8)
            yield
            debug.text = "9) Bottom view cropping 16x16 pixels, no scaling"
            self.red_block.scale = 1
            self.bottom_view.scale = 1
            self.top_view.scale = 1
            self.bottom_view.crop = True
            self.bottom_view.crop_size = (16, 16)
            yield
            debug.text = "9) Top view cropping 16x16 pixels, no bottom crop"
            self.bottom_view.crop = False
            self.top_view.crop = True
            self.top_view.crop_size = (16, 16)
            yield
            debug.text = "9) Top crops 20px, bottom crops 10px"
            self.bottom_view.crop = True
            self.top_view.crop = True
            self.bottom_view.crop_size = (10, 10)
            self.top_view.crop_size = (20, 20)
            yield
            debug.text = "9) Top crops 10px, bottom crops 20px"
            self.bottom_view.crop_size = (20, 20)
            self.top_view.crop_size = (10, 10)
            yield

        #self.blue_block = spyral.Sprite(self)
        #self.blue_block.image = spyral.Image(size=SMALL).fill(BLUE)
        #self.blue_block.pos = (40, 40)

        #self.green_block = spyral.Sprite(top_view)
        #self.green_block.image = spyral.Image(size=SMALL).fill(GREEN)
        #self.green_block.pos = (0, 10)

        #self.yellow_block = spyral.Sprite(self)
        #self.yellow_block.image = spyral.Image(size=SMALL).fill(YELLOW)
        #self.yellow_block.pos = (0, 0)

        #self.red_block.animate(go_down)
        #blocks = {self.red_block : go_down,
         #         self.blue_block: go_down,
          #        self.green_block: go_down,
           #       self.yellow_block: go_down & go_right}
        #self.paused = itertools.cycle(blocks.keys())
        #def advance_pauser(event):
        #    skip = next(self.paused)


        def key_down(event):
            self.top_view.crop_height += 10
        def key_up(event):
            self.top_view.crop_height -= 10
        def key_left(event):
            self.top_view.crop_width -= 10
        def key_right(event):
            self.top_view.crop_width += 10
        def notify(event):
            pass
            #print self.blue_block.x

        spyral.event.register("input.keyboard.down.down", key_down)
        spyral.event.register("input.keyboard.down.up", key_up)
        spyral.event.register("input.keyboard.down.left", key_left)
        spyral.event.register("input.keyboard.down.right", key_right)
        tests = tester()
        def next_test():
            try:
                next(tests)
            except StopIteration:
                spyral.director.quit()
        spyral.event.register("input.keyboard.down.space", next_test)
        #self.register("director.update", )
        spyral.event.register("system.quit", spyral.director.quit)

if __name__ == "__main__":
    spyral.director.init(SIZE)
    spyral.director.run(scene=Game())
