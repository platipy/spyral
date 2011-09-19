import pygame
import spyral

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)
        
class Game(spyral.scene.Scene):
    def __init__(self):
        spyral.scene.Scene.__init__(self)
        self.camera = spyral.director.camera()
        self.group = spyral.sprite.Group(self.camera)
        bg = spyral.util.new_surface(SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
        # More setup here
                
    def render(self):
        self.group.draw()
        self.camera.draw()
        
    def update(self, tick):
        # Possibly some event handling in here
        self.group.update()

if __name__ == "__main__":
    spyral.init()
    spyral.director.init(SIZE)
    spyral.director.push(Game())
    spyral.director.run()
