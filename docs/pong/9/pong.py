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
        
        spyral.event.register('director.update', self.update)
        self.reset()
        
    def update(self, dt):
        self.x += dt * self.vel_x
        self.y += dt * self.vel_y
        
        r = self.rect
        if r.top < 0:
            r.top = 0
            self.vel_y = -self.vel_y
        if r.bottom > HEIGHT:
            r.bottom = HEIGHT
            self.vel_y = -self.vel_y
        # You can't change a sprite's properties by updating properties of
        # its rect; so you have to assign the rect back to the properties!
        self.pos = r.center
        
    def reset(self):
        # We'll start by picking a random angle for the ball to move
        # We repick the direction if it isn't headed for the left
        # or the right hand side
        theta = random.random()*2*math.pi
        while ((theta > math.pi/4 and theta < 3*math.pi/4) or
               (theta > 5*math.pi/4 and theta < 7*math.pi/4)):
            theta = random.random()*2*math.pi
        # In addition to an angle, we need a velocity. Let's have the
        # ball move at 300 pixels per second
        r = 300
        
        self.vel_x = r * math.cos(theta)
        self.vel_y = r * math.sin(theta)

        # We'll start the ball at the center. self.pos is actually the
        # same as accessing sprite.x and sprite.y individually
        self.pos = (WIDTH/2, HEIGHT/2)
    
    def bounce(self):
        self.vel_x = -self.vel_x

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

        self.register("director.update", self.update)
    
    def update(self, dt):
        if (self.collide_sprites(self.ball, self.left_paddle) or
            self.collide_sprites(self.ball, self.right_paddle)):
            self.ball.bounce()
