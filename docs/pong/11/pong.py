import spyral
import random
import math

WIDTH = 1200
HEIGHT = 900
SIZE = (WIDTH, HEIGHT)

model = {"left": 0, "right": 0}

class Ball(spyral.Sprite):
    def __init__(self, scene):
        super(Ball, self).__init__()
        
        self.image = spyral.Image(size=(20, 20))
        self.image.draw_circle((255, 255, 255), (10, 10), 10)
        self.anchor = 'center'
        
        spyral.event.register('director.update', self.update)
        spyral.event.register('pong.score', self.reset)
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
        if r.left < 0:
            spyral.event.queue("pong.score", spyral.Event(scorer="left"))
        if r.right > WIDTH:
            spyral.event.queue("pong.score", spyral.Event(scorer="right"))
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
        self.reset()
        
        self.side = side
        self.moving = False
        
        if self.side == 'left':
            scene.register("input.keyboard.down.w", self.move_up)
            scene.register("input.keyboard.down.s", self.move_down)
            scene.register("input.keyboard.up.w", self.stop_move)
            scene.register("input.keyboard.up.s", self.stop_move)
        else:
            scene.register("input.keyboard.down.up", self.move_up)
            scene.register("input.keyboard.down.down", self.move_down)
            scene.register("input.keyboard.up.up", self.stop_move)
            scene.register("input.keyboard.up.down", self.stop_move)
        scene.register("director.update", self.update)
        spyral.event.register('pong.score', self.reset)
    
    def move_up(self):
        self.moving = 'up'
        
    def move_down(self):
        self.moving = 'down'
        
    def stop_move(self):
        self.moving = False
        
    def reset(self):
        if self.side == 'left':
            self.x = 20
        else:
            self.x = WIDTH - 20
        self.y = HEIGHT/2
        
    def update(self, dt):
        paddle_velocity = 250
        
        if self.moving == 'up':
            self.y -= paddle_velocity * dt
            
        elif self.moving == 'down':
            self.y += paddle_velocity * dt
                
        r = self.get_rect()
        if r.top < 0:
            r.top = 0
        if r.bottom > HEIGHT:
            r.bottom = HEIGHT
        self.pos = r.center


class Pong(spyral.Scene):
    def __init__(self):
        super(Pong, self).__init__(SIZE)
        
        self.background = spyral.Image(size=SIZE)
        self.background.fill( (0, 0, 0) )

        self.left_paddle = Paddle(self, 'left')
        self.right_paddle = Paddle(self, 'right')
        self.ball = Ball(self)

        self.register("director.update", self.update)
        self.register("system.quit", spyral.director.pop)
        self.register("pong.score", increase_score)
    
    def increase_score(self, scorer):
        model[scorer] += 1
    
    def update(self, dt):
        if (self.collide_sprites(self.ball, self.left_paddle) or
            self.collide_sprites(self.ball, self.right_paddle)):
            self.ball.bounce()
