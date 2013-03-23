try:
    import _path
except NameError:
    pass
import spyral
import sys
from functools import partial

SIZE = (640, 480)

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
        spyral.Scene.__init__(self)
        self.load_style("style.spys")
        self.load_style("../spyral/resources/form_defaults.spys")

        class RegisterForm(spyral.Form):
            name = spyral.widgets.TextInput(50, "Name")
            password = spyral.widgets.TextInput(50, "Pass")
        #     user_type = spyral.RadioGroup(self, map(partial(spyral.RadioButtonWidget, self), ["Admin", "User", "Guest"]))
        #     remember_me = spyral.CheckboxWidget(self)
        #     okay = spyral.ButtonWidget(self, "Okay")
        #     cancel = spyral.ButtonWidget(self, "Cancel")
        #     def submit(self):
        #         print name.value, password.value
        #     def reset(self):
        #         print "Cancelled"
        my_form = RegisterForm(self)
        my_form.focus()
        
        self.register("system.quit", sys.exit)
        
if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
