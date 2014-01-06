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

        class RegisterForm(spyral.Form):
            name = spyral.widgets.TextInput(100, "Current Name")
            password = spyral.widgets.TextInput(50, "*Pass*")
            #user_type = spyral.RadioGroup(self, map(partial(spyral.RadioButtonWidget, self), ["Admin", "User", "Guest"]))
            remember_me = spyral.widgets.Checkbox()
            togglodyte = spyral.widgets.ToggleButton("Toggle me!")
            okay = spyral.widgets.Button("Okay Button")
        my_form = RegisterForm(self)
        my_form.name.pos = (100, 100)
        my_form.focus()
        
        def test_print(event):
            if event.value == "down":
                print "Pressed!", event.widget.name
                
        debug = spyral.DebugText(self, "1) Red square in middle of room", (255, 0, 255))
        debug.anchor = 'midbottom'
        debug.position = self.rect.midbottom
        def test_react(event):
            debug.text = event.widget.value
        
        def test_tree():
            lt = self._layer_tree
            print "*" * 10
            for name, order in sorted(lt.layer_location.iteritems(), key=lambda x:x[1]):
                print name, order
            print "*" * 10
            for name, children in lt.child_views.iteritems():
                print name, ":::", map(str, children)
            print "*" * 10
        
        self.register("system.quit", sys.exit)
        self.register("form.RegisterForm.okay.changed", test_print)
        self.register("form.RegisterForm.name.changed", test_react)
        self.register("input.keyboard.down.space", test_tree)
        
if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
