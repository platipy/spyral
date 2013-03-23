try:
    import _path
except NameError:
    pass
import spyral
import sys
from functools import partial

SIZE = (640, 480)
BG_COLOR = (128, 128, 128)

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
        self.load_style("../spyral/resources/form_defaults.spys")

        bg = spyral.Image(size=SIZE)
        bg.fill(BG_COLOR)
        self.set_background(bg)
        
        # More setup here
        # form = spyral.form.Form(self, 'Forms')
        
        # name_entry = spyral.TextInputWidget(self, 500, 'is so awesome', default_value=False)
        # name_entry.pos = (30,30)
        # form.add_widget("name_entry",name_entry)
        
        #email_entry = spyral.TextInputWidget(self, 200, 'acbart', default_value=True, max_length = 10)
        #email_entry.pos = (30, 100)
        #form.add_widget("email_entry",email_entry)
        
        class RegisterForm(spyral.Form):
            name = spyral.TextInputWidget(self, 50, "Name")
            password = spyral.TextInputWidget(self, 50, "Pass")
            user_type = spyral.RadioGroup(self, map(partial(spyral.RadioButtonWidget, self), ["Admin", "User", "Guest"]))
            remember_me = spyral.CheckboxWidget(self)
            okay = spyral.ButtonWidget(self, "Okay")
            cancel = spyral.ButtonWidget(self, "Cancel")
            def submit(self):
                print name.value, password.value
            def reset(self):
                print "Cancelled"
                
        my_form = RegisterForm(self)
        my_form.focus()
        self.register("form.RegisterForm.okay.click", my_form.submit)
        self.register("form.RegisterForm.cancel.click", my_form.cancel)
        
        # a_button = spyral.ButtonWidget(self, "A regular button")
        # a_button.pos = (30, 150)
        # form.add_widget("a_button",a_button)
        
        # a_button = spyral.ToggleButtonWidget(self, "A toggle button")
        # a_button.pos = (30, 200)
        # form.add_widget("toggle_button",a_button)
        
        # check_box = spyral.CheckboxWidget(self)
        # check_box.pos = (30, 250)
        # form.add_widget("check_box",check_box)
            
        # radio_group = spyral.RadioGroup(self)
        # for index, value in enumerate(['Easy', 'Medium', 'Hard']):
            # radio = spyral.RadioButtonWidget(self, radio_group)
            # radio.pos = (30 + 30 * index, 300)
            
            # form.add_widget("radio1",radio)
        
        self.register("system.quit", sys.exit)
        
if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
