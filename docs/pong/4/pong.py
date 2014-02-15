import spyral

WIDTH = 1200
HEIGHT = 900
SIZE = (WIDTH, HEIGHT)

class Paddle(spyral.Sprite):
    def __init__(self, scene):
        super(Sprite, self).__init__(scene)
        
        self.image = spyral.Image(size=(20, 300)).fill((255, 255, 255))


class Pong(spyral.Scene):
    def __init__(self):
        super(Pong, self).__init__(SIZE)
        
        self.background = spyral.Image(size=SIZE)
        self.background.fill( (0, 0, 0) )

        self.left_paddle = Paddle(self)
        self.right_paddle = Paddle(self)
        
        self.left_paddle.anchor = 'midleft'
        self.left_paddle.pos = (20, HEIGHT / 2)
        
        self.right_paddle.anchor = 'midright'
        self.right_paddle.pos = (WIDTH - 20, HEIGHT / 2)
        