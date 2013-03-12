try:
    import _path
except NameError:
    pass
import spyral
import sys

SIZE = (640, 480)
BG_COLOR = (255, 255, 255)

class Game(spyral.Scene):
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
        spyral.Scene.__init__(self, SIZE)
        # We cannot draw directly to the root camera, so we always make a child
        # camera for our scene with our requested virtual resolution. In this
        # case we'll use the same as the window size, but this doesn't have to be
        # the case
        self.camera = self.parent_camera.make_child(SIZE)
        self.initialized = False
        
    def on_enter(self):
        # Some things you may wish to do every time you enter the scene
        if self.initialized:
            return
        self.initialized = True
        # Other things you may want to do only once
        bg = spyral.Image(size=SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
        # More setup here
        name_entry = spyral.TextInputWidget(self.camera, 500, 'is so awesome', default_value=False)
        name_entry.pos = (30,30)
        email_entry = spyral.TextInputWidget(self.camera, 200, 'acbart', default_value=True, max_length = 10)
        email_entry.pos = (30, 100)
        a_button = spyral.ButtonWidget(self.camera, "Click Me")
        a_button.pos = (30, 140)
        #checkbox = spyral.CheckboxWidget(self.camera)
        #checkbox.pos = (200, 140)
        self.manager = spyral.event.EventManager()
        form = spyral.form.Form(self.camera, 'Forms', 
                                self.manager)

        
        form.add_widget("name_entry",name_entry)
        form.add_widget("email_entry",email_entry)
        form.add_widget("a_button",a_button)
        form.focus()
        self.manager.register_listener(form, ['KEYDOWN', 'KEYUP', 'MOUSEMOTION','MOUSEBUTTONUP', 'MOUSEBUTTONDOWN'])
        
    def render(self):
        self.camera.draw()
        
    def update(self, dt):
        """
        The update function should contain or call out to all the logic.
        Here is where group.update() should be called for the groups, where
        event handling should be taken care of, etc.
        """
        events= self.event_handler.get()
        self.manager.send_events(events)
        for event in events:
            if event['type'] == 'QUIT':
                spyral.quit()
                sys.exit()

 
        self.camera.update(dt)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
