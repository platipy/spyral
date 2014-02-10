try:
    import _path
except NameError:
    pass
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Square(spyral.Sprite):
    def __init__(self, scene, direction, color=(255, 0,0)):
        spyral.Sprite.__init__(self, scene)
        self.image = spyral.Image(size=(16, 16)).fill(color)
        self.direction = direction
        self.anchor = 'center'
        spyral.event.register("director.update", self.update)
    
    def update(self):
        self.x += self.direction * 4
        if not self.collide_rect(self.scene.rect):
            self.x -= self.direction * 4
            self.flip()
            
    def flip(self):
        self.direction *= -1

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill(BG_COLOR)
        
        self.left_square = Square(self, 1, (0,255,0))
        self.left_square.pos = self.rect.midleft
        self.right_square = Square(self, -1)
        self.right_square.pos = self.rect.midright
        
        spyral.event.register("system.quit", sys.exit)
        spyral.event.register("director.update", self.update)
    
    def update(self):
        if self.left_square.collide_sprite(self.right_square):
            self.right_square.flip()
            self.left_square.flip()

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
