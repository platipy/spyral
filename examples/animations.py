try:
    import _path
except NameError:
    pass
import spyral
from spyral.sprite import Sprite
from spyral.animation import Animation, DelayAnimation
from spyral.scene import Scene
import spyral.easing as easing
import math
import sys

SIZE = (640, 480)
FONT_SIZE = 42
BG_COLOR = (0, 0, 0)
FG_COLOR = (255, 255, 255)

DELAY = DelayAnimation(1.5)

ANIMATIONS = [
    ('Linear', Animation('x', easing.Linear(0, 600), duration = 3.0)),
    ('QuadraticIn', Animation('x', easing.QuadraticIn(0, 600), duration = 3.0)),
    ('QuadraticOut', Animation('x', easing.QuadraticOut(0, 600), duration = 3.0)),
    ('QuadraticInOut', Animation('x', easing.QuadraticInOut(0, 600), duration = 3.0)),
    ('CubicIn', Animation('x', easing.CubicIn(0, 600), duration = 3.0)),
    ('CubicOut', Animation('x', easing.CubicOut(0, 600), duration = 3.0)),
    ('CubicInOut', Animation('x', easing.CubicInOut(0, 600), duration = 3.0)),
    ('Custom (Using Polar)', Animation('pos', easing.Polar(center = (320, 240),
                                                           radius = lambda theta: 100.0+25.0*math.sin(5.0*theta)),
                                                           duration = 3.0)),
    ('Sine', Animation('x', easing.Sine(amplitude = 100.0), duration=3.0, shift=300)),
    ('Arc', Animation('pos', easing.Arc(center = (320, 240), radius = 100.0, theta_end = 1.4*math.pi))),
    ('Scale', Animation('scale', easing.LinearTuple((1.0, 1.0), (0.0, 2.0)), duration = 3.0)),
    ('Rotate', Animation('angle', easing.Linear(0, 2.0*math.pi), duration = 3.0))
]

class TextSprite(Sprite):
    def __init__(self, scene, font):
        Sprite.__init__(self, scene)
        self.font = font
        
    def render(self, text):
        self.image = self.font.render(text)

class AnimationExamples(Scene):
    def __init__(self):
        Scene.__init__(self, SIZE)
        bg = spyral.Image(size=SIZE)
        bg.fill(BG_COLOR)
        self.background = bg
        
        font = spyral.Font(None, FONT_SIZE, FG_COLOR)
        
        self.title = TextSprite(self, font)
        self.title.anchor = 'center'
        self.title.pos = (SIZE[0] / 2, 30)
        self.title.render("N")
        
        self.block = Sprite(self)
        self.block.image = spyral.Image(size=(40,40))
        self.block.image.fill(FG_COLOR)
        self.block.y = 300
        
        self.index = 0
        
        self.set_animation()
        
        instructions = TextSprite(self, font)
        instructions.anchor = 'midbottom'
        instructions.x = 320
        instructions.y = 470
        instructions.render("n: next example  p: previous example  q: quit")
        
        # Register all event handlers
        self.register('system.quit', sys.exit)
        self.register('input.keyboard.down.p', self.previous)
        self.register('input.keyboard.down.n', self.next)
        self.register('input.keyboard.down.q', sys.exit)
        self.register('input.keyboard.down.escape', sys.exit)

                                
    def set_animation(self):
        self.title.render(ANIMATIONS[self.index][0])
        self.block.stop_all_animations()
        self.block.y = 300 # Reset the y-coordinate.
        a = ANIMATIONS[self.index][1] + DELAY
        a.loop = True
        self.block.animate(a)
        
    def next(self):
        self.index += 1
        self.index %= len(ANIMATIONS)
        self.set_animation()
        
    def previous(self):
        self.index -= 1
        self.index %= len(ANIMATIONS)
        self.set_animation()

if __name__ == "__main__":
    spyral.init()
    spyral.director.init(SIZE)
    spyral.director.run(scene=AnimationExamples())
