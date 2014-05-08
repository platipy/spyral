import spyral
import pygame

_initialized = False
_stack = []
_screen = None
_tick = 0
_max_fps = 30
_max_ups = 30

def quit():
    """
    Cleanly quits out of spyral by emptying the stack.
    """
    spyral._quit()

def init(size=(0, 0),
         max_ups=30,
         max_fps=30,
         fullscreen=False,
         caption="My Spyral Game"):
    """
    Initializes the director. This should be called at the very beginning of
    your game.

    :param size: The resolution of the display window. (0,0) uses the screen
                 resolution
    :type size: :class:`Vec2D <spyral.Vec2D>`
    :param max_fps: The maximum number of times that the 
                    :func:`director.render` event will occur per second, i.e.,
                    the number of times your game will be rendered per second.
    :type max_fps: ``int``
    :param max_ups: The maximum number of times that the 
                    :func:`director.update` event will occur per second.
                    This will remain the same, even
                    if fps drops.
    :type max_ups: ``int``
    :param fullscreen: Whether your game should start in fullscreen mode.
    :type fullscreen: ``bool``
    :param caption: The caption that will be displayed in the window.
                    Typically the name of your game.
    :type caption: ``str``
    """
    global _initialized
    global _screen
    global _max_fps
    global _max_ups

    if _initialized:
        print 'Warning: Tried to initialize the director twice. Ignoring.'
    spyral._init()

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
    Returns the currently running scene; this will be the Scene on the top of
    the director's stack.

    :rtype: :class:`Scene <spyral.Scene>`
    :returns: The currently running Scene, or `None`.
    """
    try:
        return _stack[-1]
    except IndexError:
        return None

def get_tick():
    """
    Returns the current tick number, where ticks happen on each update,
    not on each frame. A tick is a "tick of the clock", and will happen many
    (usually 30) times per second.

    :rtype: int
    :returns: The current number of ticks since the start of the game.
    """
    return _tick

def replace(scene):
    """
    Replace the currently running scene on the stack with *scene*.
    Execution will continue after this is called, so make sure you return;
    otherwise you may find unexpected behavior::

        spyral.director.replace(Scene())
        print "This will be printed!"
        return

    :param scene: The new scene.
    :type scene: :class:`Scene <spyral.Scene>`
    """
    if _stack:
        spyral.event.handle('director.scene.exit', scene=_stack[-1])
        old = _stack.pop()
        spyral.sprite._switch_scene()
    _stack.append(scene)
    spyral.event.handle('director.scene.enter',
                        event=spyral.Event(scene=scene),
                        scene=scene)
    # Empty all events!
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
    spyral.event.handle('director.scene.exit', scene=_stack[-1])
    scene = _stack.pop()
    spyral.sprite._switch_scene()
    if _stack:
        scene = _stack[-1]
        spyral.event.handle('director.scene.enter', scene=scene)
    else:
        exit(0)
    pygame.event.get()

def push(scene):
    """
    Place *scene* on the top of the stack, and move control to it. This does 
    return control, so remember to return immediately after calling it. 

    :param scene: The new scene.
    :type scene: :class:`Scene <spyral.Scene>`
    """
    if _stack:
        spyral.event.handle('director.scene.exit', scene=_stack[-1])
        old = _stack[-1]
        spyral.sprite._switch_scene()
    _stack.append(scene)
    spyral.event.handle('director.scene.enter', scene=scene)
    # Empty all events!
    pygame.event.get()

def run(sugar=False, profiling=False, scene=None):
    """
    Begins running the game, starting with the scene on top of the stack. You
    can also pass in a *scene* to push that scene on top of the stack. This
    function will run until your game ends, at which point execution will end
    too.

    :param bool sugar: Whether to run the game for Sugar. This is only
                       to the special XO Launcher; it is safe to ignore.
    :param bool profiling: Whether to enable profiling mode, where this function
                           will return on every scene change so that scenes can
                           be profiled independently.
    :param scene: The first scene.
    :type scene: :class:`Scene <spyral.Scene>`
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
    try:
        while True:
            scene = stack[-1]
            if scene is not old_scene:
                if profiling and old_scene is not None:
                    return
                clock = scene.clock
                old_scene = scene

                def frame_callback(interpolation):
                    """
                    A closure for handling drawing, which includes forcing the
                    rendering-related events to be fired.
                    """
                    scene._handle_event("director.pre_render")
                    scene._handle_event("director.render")
                    scene._draw()
                    scene._handle_event("director.post_render")

                def update_callback(delta):
                    """
                    A closure for handling events, which includes firing the update
                    related events (e.g., pre_update, update, and post_update).
                    """
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
                    scene._handle_event("director.update",
                                        spyral.Event(delta=delta))
                    _tick += 1
                    scene._handle_event("director.post_update")
                clock.frame_callback = frame_callback
                clock.update_callback = update_callback
            clock.tick()
    except spyral.exceptions.GameEndException:
        pass
