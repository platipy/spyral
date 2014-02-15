import spyral
import random
import math

WIDTH = 1200
HEIGHT = 900
SIZE = (WIDTH, HEIGHT)

class Ball(spyral.Sprite):
    def __init__(self, scene):
        super(Ball, self).__init__()
        
        self.image = spyral.Image(size=(20, 20))
        self.image.draw_circle((255, 255, 255), (10, 10), 10)
        self.anchor = 'center'
        self.pos = (WIDTH/2, HEIGHT/2)

class Paddle(spyral.Sprite):
    def __init__(self, scene, side):
        super(Sprite, self).__init__(scene)
        
        self.image = spyral.Image(size=(20, 300)).fill((255, 255, 255))
        
        self.anchor = 'mid' + side
        if side == 'left':
            self.x = 20
        else:
            self.x = WIDTH - 20
        self.y = HEIGHT/2


class Pong(spyral.Scene):
    def __init__(self):
        super(Pong, self).__init__(SIZE)
        
        self.background = spyral.Image(size=SIZE)
        self.background.fill( (0, 0, 0) )

        self.left_paddle = Paddle(self, 'left')
        self.right_paddle = Paddle(self, 'right')
        self.ball = Ball(self)
