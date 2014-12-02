try:
    import _path
except NameError:
    pass
import spyral

WIDTH = 640
HEIGHT = 480

SIZE = (640, 480)
BG_COLOR = (128, 128, 128)
BLACK = (0,0,0)


class RectSprite(spyral.Sprite):
    def __init__(self, view):
        spyral.Sprite.__init__(self, view)
        self.image = spyral.Image(size=(50, 50))
        self.anchor = 'center'
        self.image.draw_rect(BLACK, (0, 0), (40, 40), border_width=1)


class LineSprite(spyral.Sprite):
    def __init__(self, view):
        spyral.Sprite.__init__(self, view)
        self.image = spyral.Image(size=(400, 400))
        self.anchor = 'center'
        self.image.draw_lines((0,0,0), [(0, 6),(200, 6)], 10, False)
            
class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE)
        self.background.fill(BG_COLOR)
        self.lin = LineSprite(self)
        self.lin.pos = (WIDTH/2, HEIGHT/2)
        self.rec = RectSprite(self)
        self.rec.pos = (WIDTH/2, HEIGHT/2)
        
        spyral.event.register("system.quit", spyral.director.quit, scene=self)
        
if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
