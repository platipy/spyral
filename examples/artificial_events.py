'''
This example demonstrates how you can send out fake events. Spyral's event
system is actually fairly straightforward, and it is easy to send out new
events. Not only does this include custom events, but even system events.

The ReplayEventHandler is a much more sophisticated version of this, allowing
you to record and replay sequences of events in a file. However, I never got
around to checking if it still worked. The method demonstrated below should
be perfectly reliable however.

When building up fake events, you may want to refer to Event List in the docs.
http://platipy.readthedocs.org/en/latest/refs/events.html
'''

try:
    import _path
except NameError:
    pass
import spyral

# Constants
RESOLUTION = (640, 480)

# State variables - there are other ways to handle this, but this should
#   probably be sufficient
PLACES_TO_PRESS = [(5,5), (55, 55), (105, 105)]
i = 0
def touch_screen():
    '''
    Walk through PLACES_TO_PRESS, triggering each one (one per tick), and then
    exiting. You will probably use this pattern to walk through a list of
    events that you want to handle. A more sophisticated approach would be
    to build up a list of runnable event handles:
    
    EVENTS_TO_RUN = [
        lambda : spyral.event.handle('input.mouse.down', spyral.Event(pos=(5, 5), button='left'), my_scene),
        lambda : spyral.event.handle('input.mouse.up', spyral.Event(pos=(5, 5), button='left'), my_scene),
        lambda : spyral.event.handle('input.mouse.down', spyral.Event(pos=(55, 55), button='right'), my_scene),
        lambda : spyral.event.handle('input.mouse.up', spyral.Event(pos=(55, 55), button='right'), my_scene),
        ...
        lambda : spyral.event.handle('system.quit', spyral.Event(), my_scene),
    ]
    '''
    global i
    if i < len(PLACES_TO_PRESS):
        trigger_fake_mouse_click(PLACES_TO_PRESS[i])
    elif i > len(PLACES_TO_PRESS):
        # We wait an extra frame before exiting so that we handle all the
        #   triggered events
        spyral.director.quit()
    i += 1
    
        
def trigger_fake_mouse_click(pos):
    '''
    Build up a fake mouse event and then send it to be handled.
    '''
    mouse_press_event = spyral.Event(pos=pos, button=1)
    spyral.event.handle('input.mouse.down', mouse_press_event, my_scene)
    
    ### Similar:
    ##keyboard_press_event = spyral.Event(unicode=, key=, mod=)
    ##spyral.event.handle('input.keyboard.down', keyboard_press_event, my_scene)
        
def mouse_clicked(pos):
    '''
    React to a mouse click.
    '''
    print "Woah, I was clicked at", pos
    
def button_clicked(widget):
    '''
    React to button click
    '''
    print "Clicked the following button:", widget.text

# Build scene with background, register window exit button
spyral.director.init(RESOLUTION)
my_scene = spyral.Scene(RESOLUTION)
my_scene.background = spyral.Image(size=RESOLUTION).fill((0,0,0))
spyral.event.register("system.quit", spyral.director.quit, scene=my_scene)

# Build up some buttons to make things interesting
class SimpleForm(spyral.Form):
    first = spyral.widgets.Button("First Button")
    second = spyral.widgets.Button("Second Button")
    third = spyral.widgets.Button("Third Button")
my_form = SimpleForm(my_scene)
my_form.focus()
my_form.first.pos = (0,0)
my_form.second.pos = (50,50)
my_form.third.pos = (100,100)

# Register something to tell us that the mouse was clicked
spyral.event.register("input.mouse.down", mouse_clicked, scene=my_scene)
# We use changed for the buttons - clicked requires a down and an up event :)
spyral.event.register("form.SimpleForm.first.changed", button_clicked, scene=my_scene)
spyral.event.register("form.SimpleForm.second.changed", button_clicked, scene=my_scene)
spyral.event.register("form.SimpleForm.third.changed", button_clicked, scene=my_scene)

# Register our event spoofer
spyral.event.register("director.update", touch_screen, scene=my_scene)

# And run our game
spyral.director.run(scene=my_scene)