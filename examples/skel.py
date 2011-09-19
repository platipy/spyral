import pygame
import spyral

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Game(spyral.scene.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    
    A Scene should define two methods, update and render.
    """
    def __init__(self):
        """
        The __init__ message for a scene should set up the camera(s) for the
        scene, and setup groups and other structures which are needed for the
        scene.
        """
        spyral.scene.Scene.__init__(self)
        self.camera = spyral.director.camera()
        self.group = spyral.sprite.Group(self.camera)
        bg = spyral.util.new_surface(SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
        # More setup here
                
    def render(self):
        """
        The render function should call .draw() on the scene's group(s) and
        camera(s). Unless your game logic should be bound by framerate,
        logic should go elsewhere.
        """
        self.group.draw()
        self.camera.draw()
        
    def update(self, tick):
        """
        The update function should contain or call out to all the logic.
        Here is where group.update() should be called for the groups, where
        event handling should be taken care of, etc.
        """
        self.group.update()

if __name__ == "__main__":
    spyral.init() # Always call spyral.init() first
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game()) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
