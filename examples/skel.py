try:
    import _path
except NameError:
    pass
import pygame
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    
    A Scene should define two methods, update and render.
    """
    def __init__(self):
        """
        The __init__ message for a scene should set up the camera(s) for the
        scene, and other structures which are needed for the scene
        """
        spyral.Scene.__init__(self, SIZE)
        # We cannot draw directly to the root camera, so we always make a child
        # camera for our scene with our requested virtual resolution. In this
        # case we'll use the same as the window size, but this doesn't have to be
        # the case
        bg = spyral.Image(size=SIZE)
        bg.fill(BG_COLOR)
        self.set_background(bg)
        
        self.register("system.quit", sys.exit)
        
    def update(self, dt):
        """
        The update function should contain or call out to all the logic.
        Here is where group.update() should be called for the groups, ...
        [FILL IN SOME STUFF HERE]
        """
        self.camera.update(dt)

if __name__ == "__main__":
    spyral.init() # Always call spyral.init() first
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game()) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
