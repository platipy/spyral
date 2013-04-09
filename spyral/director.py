import spyral
import pygame

_initialized = False
_stack = []
_screen = None
_tick = 0
_max_fps = None
_max_ups = None

def init(size=(0, 0),
         max_ups = 30,
         max_fps = 30,
         fullscreen = False,
         caption = "spyral"):
    global _initialized
    global _screen
    global _max_fps
    global _max_ups
    
    """
    Initializes the director.

    | *size* is the resolution of the display. (0,0) uses the screen resolution
    | *max_ups* sets the number of times scene.update() should be
       called per frame. This will remain the same, even if fps drops.
    | *max_fps* sets the fps cap on the game.
    | *fullscreen* determines whether the display starts fullscreen
    | *caption* is the window caption
    """
    if _initialized:
        print('Warning: Tried to initialize the director twice. Ignoring.')
    spyral.init()

    flags = 0
    # These flags are going to be managed better or elsewhere later
    resizable = False
    noframe = False

    if resizable:
        flags |= pygame.RESIZABLE
    if noframe:
        flags |= pygame.NOFRAME
    if fullscreen:
        flags |= pygame.FULLSCREEN
    _screen = pygame.display.set_mode(size, flags)

    _initialized = True
    pygame.display.set_caption(caption)

    _max_ups = max_ups
    _max_fps = max_fps

def get_scene():
    """
    Returns the currently running scene.
    """
    try:
        return _stack[-1]
    except IndexError:
        return None

def get_tick():
    """
    Returns the current tick number, where ticks happen on each update,
    not on each frame.
    
    A tick is a "tick of the clock", and will happen many (usually 30) times
    per second. TODO: Do I know what I'm talking about?
    """
    return _tick

def replace(scene):
    """
    Replace the currently running scene on the stack with *scene*.
    
    Execution will continue after this is called, so make sure you return::
        spyral.director.replace(Scene())
        print "This will be printed!"
        return
    TODO: Do I know what I'm talking about?
    """
    if _stack:
        spyral.event.handle('director.scene.exit', _scene = _stack[-1])
        old = _stack.pop()
        spyral.sprite._switch_scene()
    _stack.append(scene)
    spyral.event.handle('director.scene.enter', _scene = scene)
    pygame.event.get()

def pop():
    """
    Pop the top scene off the stack, returning control to the next scene
    on the stack. If the stack is empty, the program will quit.

    This does return control, so remember to return immediately after 
    calling it.
    """
    if len(_stack) < 1:
        return
    spyral.event.handle('director.scene.exit', _scene = _stack[-1])
    scene = _stack.pop()
    spyral.sprite._switch_scene()
    if _stack:
        scene = _stack[-1]
        spyral.event.handle('director.scene.enter', _scene = scene)
    else:
        exit(0)
    pygame.event.get()

def push(scene):
    """
    Place *scene* on the top of the stack, and move control to it.

    This does return control, so remember to return immediately after 
    calling it.
    """
    if _stack:
        spyral.event.handle('director.scene.exit', _scene = _stack[-1])
        old = _stack[-1]
        spyral.sprite._switch_scene()
    _stack.append(scene)
    spyral.event.handle('director.scene.enter', _scene = scene)
    pygame.event.get()

def run(sugar=False, profiling=False, scene=None):
    """
    Begins running the game, starting with the scene on top of the stack. You
    can also pass in a *scene* to push that scene on top of the stack.

    If *profiling* is enabled, this function will return on every
    scene change so that scenes can be profiled independently.
    
    The *sugar* argument is used by the Launcher, it can be safely ignored.
    """
    if scene is not None:
        push(scene)
    if sugar:
        import gtk
    if not _stack:
        return
    old_scene = None
    scene = get_scene()
    clock = scene.clock
    stack = _stack
    while True:
        scene = stack[-1]
        if scene is not old_scene:
            if profiling and old_scene is not None:
                return
            clock = scene.clock
            old_scene = scene

            def frame_callback(interpolation):
                scene._handle_event("director.pre_render")
                scene._handle_event("director.render")
                scene._draw()
                scene._handle_event("director.post_render")

            def update_callback(dt):
                global _tick
                if sugar:
                    while gtk.events_pending():
                        gtk.main_iteration()
                if len(pygame.event.get([pygame.VIDEOEXPOSE])) > 0:
                    scene.redraw()
                    scene._handle_event("director.redraw")

                scene._event_source.tick()
                events = scene._event_source.get()
                for event in events:
                    scene._queue_event(*spyral.event._pygame_to_spyral(event))
                scene._handle_event("director.pre_update")
                scene._handle_event("director.update", spyral.Event(dt=dt))
                _tick += 1
                scene._handle_event("director.post_update")
            clock.frame_callback = frame_callback
            clock.update_callback = update_callback
        clock.tick()
