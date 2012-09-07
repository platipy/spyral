import pygame
import spyral
#from spyral import sgc

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
        # We cannot draw directly to the root camera, so we always make a child
        # camera for our scene with our requested virtual resolution. In this
        # case we'll use the same as the window size, but this doesn't have to be
        # the case
        self.camera = spyral.director.get_camera().make_child(SIZE)
        self.group = spyral.sprite.Group(self.camera)
        self.initialized = False
        
    def on_enter(self):
        # Some things you may wish to do every time you enter the scene
        if self.initialized:
            return
        self.initialized = True
        # Other things you may want to do only once
        bg = spyral.util.new_surface(SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
        # More setup here
        #btn = spyral.sgc.Button(label="Hello World", pos=(100, 100))
        #btn.add(0)
                
    def render(self):
        """
        The render function should call .draw() on the scene's group(s).
        Unless your game logic should be bound by framerate,
        logic should go elsewhere.
        """
        self.group.draw()
        
    def update(self, tick):
        """
        The update function should contain or call out to all the logic.
        Here is where group.update() should be called for the groups, where
        event handling should be taken care of, etc.
        """
        self.group.update()
        #spyral.sgc.event(
        for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
            #sgc.event(event)
            if event.type == QUIT:
                exit()

if __name__ == "__main__":
    spyral.init() # Always call spyral.init() first
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.push(Game()) # push means that this Game() instance is
                                 # on the stack to run
    spyral.director.run() # This will run your game. It will not return.
