try:
    import _path
except NameError:
    pass
import pygame
import spyral
from spyral.sprite import Sprite
from spyral.anim import AnimationSprite, AnimationGroup, Animation, DelayAnimation
from spyral.scene import Scene
import spyral.animations as animations
import math
import sys

SIZE = (640, 480)
FONT_SIZE = 42
BG_COLOR = (0, 0, 0)
FG_COLOR = (255, 255, 255)

DELAY = DelayAnimation(1.5)

ANIMATIONS = [
    ('Linear', Animation('x', animations.Linear(0, 600), duration = 3.0)),
    ('QuadraticIn', Animation('x', animations.QuadraticIn(0, 600), duration = 3.0)),
    ('QuadraticOut', Animation('x', animations.QuadraticOut(0, 600), duration = 3.0)),
    ('QuadraticInOut', Animation('x', animations.QuadraticInOut(0, 600), duration = 3.0)),
    ('CubicIn', Animation('x', animations.CubicIn(0, 600), duration = 3.0)),
    ('CubicOut', Animation('x', animations.CubicOut(0, 600), duration = 3.0)),
    ('CubicInOut', Animation('x', animations.CubicInOut(0, 600), duration = 3.0)),
    ('Custom (Using Polar)', Animation('pos', animations.Polar(center = (320, 240),
                                                               radius = lambda theta: 100.0+25.0*math.sin(5.0*theta)),
                                                               duration = 3.0)),
    ('Sine', Animation('x', animations.Sine(amplitude = 100.0), duration=3.0, shift=300)),
]

class TextSprite(Sprite):
    def __init__(self, group, font):
        Sprite.__init__(self, group)
        self.font = font
        
    def render(self, text):
        self.image = self.font.render(text, True, FG_COLOR).convert_alpha()


class AnimationExamples(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.camera = self.parent_camera.make_child(SIZE)
        self.group = AnimationGroup(self.camera)
        
        font = pygame.font.SysFont(None, FONT_SIZE)
        
        self.title = TextSprite(self.group, font)
        self.title.anchor = 'center'
        self.title.pos = (SIZE[0] / 2, 30)
        self.title.render("N")
        
        self.block = AnimationSprite(self.group)
        self.block.image = spyral.util.new_surface((40, 40))
        self.block.image.fill(FG_COLOR)
        self.block.y = 300
        
        self.index = 0
        
        self.set_animation()
                
    def on_enter(self):
        bg = spyral.util.new_surface(SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
                
    def render(self):
        self.group.draw()
        
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
        
    def update(self, dt):
        for event in self.event_handler.get():
            if event['type'] == 'QUIT':
                spyral.quit()
                sys.exit()
            if event['type'] == 'KEYDOWN':
                if event['ascii'] == 'p':
                    self.previous()
                elif event['ascii'] == 'n':
                    self.next()
                elif event['ascii'] == 'q':
                    spyral.quit()
                    
        self.group.update(dt)

if __name__ == "__main__":
    spyral.init()
    spyral.director.init(SIZE)
    spyral.director.push(AnimationExamples())
    spyral.director.run()