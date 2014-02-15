import spyral

WIDTH = 1200
HEIGHT = 900
SIZE = (WIDTH, HEIGHT)

class Pong(spyral.Scene):
    def __init__(self):
        super(Pong, self).__init__(SIZE)
        
        self.background = spyral.Image(size=SIZE)
        self.background.fill((0, 0, 0))
