try:
    import _path
except NameError:
    pass
import spyral
import sys
from functools import partial

SIZE = (640, 480)

class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self)
        self.load_style("style.spys")

        class RegisterForm(spyral.Form):
            name = spyral.widgets.TextInput(100, "Current Name")
            password = spyral.widgets.TextInput(50, "*Pass*")
            remember_me = spyral.widgets.Checkbox()
            togglodyte = spyral.widgets.ToggleButton("Toggle me!")
            okay = spyral.widgets.Button("Okay Button")
        my_form = RegisterForm(self)
        my_form.focus()

        def test_print(event):
            if event.value == "down":
                print "Pressed!", event.widget.name

        spyral.event.register("system.quit", sys.exit)
        spyral.event.register("form.RegisterForm.okay.changed", test_print)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.keyboard.repeat = True
    spyral.keyboard.delay = 800
    spyral.keyboard.interval = 50
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
