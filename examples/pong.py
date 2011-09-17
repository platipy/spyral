# This is an example of a simple pong implementation.
# Written in under an hour (57 minutes)
import pygame
import spyral
import random
import math

TICKS_PER_SECOND = 60

colors = {}
images = {}
geom = {}
fonts = {}

class Score(spyral.sprite.Sprite):
    def __init__(self):
        spyral.sprite.Sprite.__init__(self)
        self.l = 0
        self.r = 0
        self.render()
        
    def render(self):
        self.image = fonts['score'].render("%d  %d" % (self.l, self.r),
                                           True,
                                           colors['score'])
        self.rect.midtop = (geom['width']/2, geom['score_in_height'])
        

class Paddle(spyral.sprite.Sprite):
    def __init__(self):
        spyral.sprite.Sprite.__init__(self)
        self.image = images['paddle']
        self.moving_up = False
        self.moving_down = False
        
    def update(self, camera):
        if self.moving_up and self.moving_down:
            return
        if self.moving_up:
            self.pos = spyral.point.sub(self.pos, (0, geom['paddle_speed']))
        elif self.moving_down:
            self.pos = spyral.point.add(self.pos, (0, geom['paddle_speed']))
        if self.rect.bottom > geom['height']:
            self.rect.bottom = geom['height']
        elif self.rect.top < 0:
            self.rect.top = 0
            
class Ball(spyral.sprite.Sprite):
    def __init__(self):
        spyral.sprite.Sprite.__init__(self)
        self.image = images['ball']
        # Let's bias the direction so it is at a paddle to start
        x = random.random()*2*math.pi
        while ((x > math.pi/4 and x < 3*math.pi/4) or
               (x > 5*math.pi/4 and x < 7*math.pi/4)):
            x = random.random()*2*math.pi            
        self.vel = spyral.point.rectangular(geom['ball_speed'], x)
        self.rect.center = (geom['width']/2, geom['height']/2)
    
    def update(self, camera):
        self.pos = spyral.point.add(self.vel, self.pos)
        if self.rect.bottom > geom['height']:
            self.rect.bottom = geom['height']
            self.vel = (self.vel[0], -self.vel[1])
        elif self.rect.top < 0:
            self.rect.top = 0
            self.vel = (self.vel[0], -self.vel[1])
    
    def bounce_left(self, rect):
        if (rect.right > self.rect.left and
                rect.top < self.rect.bottom and
                rect.bottom > self.rect.bottom):
            self.rect.left = rect.right
            self.vel = (-self.vel[0], self.vel[1])
        return self.rect.left < 0
    def bounce_right(self, rect):
        if (self.rect.right > rect.left and
                rect.top < self.rect.bottom and
                rect.bottom > self.rect.bottom):
            self.rect.right = rect.left
            self.vel = (-self.vel[0], self.vel[1])
        return self.rect.right > geom['width']
        
class Pong(spyral.scene.Scene):
    def __init__(self):
        spyral.scene.Scene.__init__(self)
        self.camera = spyral.director.camera()
        self.group = spyral.sprite.Group(self.camera)
        bg = spyral.util.new_surface(geom['size'])
        bg.fill(colors['bg'])
        self.camera.set_background(bg)
        
        self.left_paddle = Paddle()
        self.right_paddle = Paddle()
        self.left_paddle.rect.center = (geom['paddle_in_width'], geom['height']/2)
        self.right_paddle.rect.midright = (geom['width'] - geom['paddle_in_width'],
                                          geom['height']/2)
        self.ball = Ball()
        self.score = Score()
        self.group.add(self.left_paddle, self.right_paddle, self.ball, self.score)
        
    def render(self):
        self.group.draw()
        self.camera.draw()
        
    def update(self, tick):
        for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.left_paddle.moving_up = True
                elif event.key == pygame.K_s:
                    self.left_paddle.moving_down = True
                elif event.key == pygame.K_UP:
                    self.right_paddle.moving_up = True
                elif event.key == pygame.K_DOWN:
                    self.right_paddle.moving_down = True
            else:
                if event.key == pygame.K_w:
                    self.left_paddle.moving_up = False
                elif event.key == pygame.K_s:
                    self.left_paddle.moving_down = False
                elif event.key == pygame.K_UP:
                    self.right_paddle.moving_up = False
                elif event.key == pygame.K_DOWN:
                    self.right_paddle.moving_down = False
        self.group.update()
        if self.ball.bounce_left(self.left_paddle.rect):
            self.score.l += 1
            self.score.render()
            self.ball.kill()
            self.ball = Ball()
            self.left_paddle.rect.center = (geom['paddle_in_width'], geom['height']/2)
            self.right_paddle.rect.midright = (geom['width'] - geom['paddle_in_width'],
                                              geom['height']/2)
            self.group.add(self.ball)
        if self.ball.bounce_right(self.right_paddle.rect):
            self.ball.kill()
            self.ball = Ball()
            self.score.r += 1
            self.score.render()
            self.left_paddle.rect.center = (geom['paddle_in_width'], geom['height']/2)
            self.right_paddle.rect.midright = (geom['width'] - geom['paddle_in_width'],
                                              geom['height']/2)
            self.group.add(self.ball)
if __name__ == "__main__":
    spyral.init()
    colors['bg'] = (0, 0, 0)
    colors['paddle'] = (255, 255, 255)
    colors['ball'] = (255, 255, 255)
    colors['score'] = (255, 255, 255)
    
    geom['size'] = (640, 480)
    geom['width'] = 640
    geom['height'] = 480
    geom['paddle'] = (.02*geom['width'], .3*geom['height'])
    geom['paddle_in_width'] = .03*geom['width']
    geom['paddle_speed'] = geom['height'] / (TICKS_PER_SECOND * 1.5)
    geom['ball'] = .02*geom['width']
    geom['ball_speed'] = geom['paddle_speed'] / 1.5
    geom['score_in_height'] = .03*geom['height']
    geom['score_font_size'] = .08*geom['height']
        
    images['paddle'] = spyral.util.new_surface(geom['paddle'])
    images['paddle'].fill(colors['paddle'])
    images['ball'] = spyral.util.new_surface(geom['ball'], geom['ball'])
    pygame.draw.circle(images['ball'],
                       colors['ball'],
                       (geom['ball']/2, geom['ball']/2),
                       int(geom['ball']/2),
                       0)
                       
    fonts['score'] = pygame.font.SysFont(None, geom['score_font_size'])
    
    
    spyral.director.init(geom['size'], ticks_per_second=TICKS_PER_SECOND)
    spyral.director.push(Pong())
    spyral.director.clock.use_wait = False
    spyral.director.run()