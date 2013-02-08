import spyral
import time
<<<<<<< HEAD
import yaml


class Director(object):
    """
    The director, accessible at *spyral.director*, runs the game.
    It is used to switch between scenes and call scenes' render and update 
    methods as necessary.
        """
    def __init__(self):
        self._initialized = False
        pass

    def init(self,
             size=(0, 0),
             max_ups = 30,
             max_fps = 30,
             fullscreen = False,
             caption = "spyral"):
        """
        Initializes the director.

        | *size* is the resolution of the display. (0,0) uses the screen resolution
        | *max_ups* sets the number of times scene.update() should be
           called per frame. This will remain the same, even if fps drops.
        | *max_fps* sets the fps cap on the game.
        | *fullscreen* determines whether the display starts fullscreen
        | *caption* is the window caption
        """
        if self._initialized:
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
        self._screen = pygame.display.set_mode(size, flags)

        self._initialized = True

        self._camera = spyral.camera.Camera(virtual_size=size, root=True)
        pygame.display.set_caption(caption)

        self._stack = []
        self._tick = 0

        self._max_ups = max_ups
        self._max_fps = max_fps

    def get_camera(self):
        """
        Returns the root camera for the display.
        """
        return self._camera

    def get_scene(self):
        """
        Returns the currently running scene.
        """
        try:
            return self._stack[-1]
        except IndexError:
            return None

    def get_tick(self):
        """
        Returns the current tick number, where ticks happen on each update,
        not on each frame.
        """
        return self._tick

    def replace(self, scene):
        """
        Replace the currently running scene on the stack with *scene*.
        This does return control, so remember to return immediately after 
        calling it.
        """
        if self._stack:
            old = self._stack.pop()
            old.on_exit()
            spyral.sprite._switch_scene()
            self._camera._exit_scene(old)
        self._stack.append(scene)
        self._camera._enter_scene(scene)
        scene.on_enter()
        pygame.event.get()

    def pop(self):
        """
        Pop the top scene off the stack, returning control to the next scene
        on the stack. If the stack is empty, the program will quit.

        This does return control, so remember to return immediately after 
        calling it.
        """
        if len(self._stack) < 1:
            return
        scene = self._stack.pop()
        scene.on_exit()
        spyral.sprite._switch_scene()
        self._camera._exit_scene(scene)
        if self._stack:
            scene = self._stack[-1]
            self._camera._enter_scene(scene)
            scene.on_enter()
        else:
            exit(0)
        pygame.event.get()

    def push(self, scene):
        """
        Place *scene* on the top of the stack, and move control to it.

        This does return control, so remember to return immediately after 
        calling it.
        """
        if self._stack:
            old = self._stack[-1]
            old.on_exit()
            spyral.sprite._switch_scene()
            self._camera._exit_scene(old)
        self._stack.append(scene)
        self._camera._enter_scene(scene)
        scene.on_enter()
        pygame.event.get()

    def run(self, sugar=False, profiling=False):
        """
        Runs the scene as dictated by the stack.

        If profiling is enabled, this function will return on every
        scene change so that scenes can be profiled independently.
        """
        if sugar:
            import gtk
        if not self._stack:
            return
        old_scene = None
        scene = self.get_scene()
        camera = self._camera
        clock = scene.clock
        stack = self._stack
        while True:
            scene = stack[-1]
            if scene is not old_scene:
                if profiling and old_scene is not None:
                    return
                clock = scene.clock
                old_scene = scene

                def frame_callback(interpolation):
                    scene.render()
                    camera._draw()

                def update_callback(dt):
                    if sugar:
                        while gtk.events_pending():
                            gtk.main_iteration()
                    if len(pygame.event.get([pygame.VIDEOEXPOSE])) > 0:
                        camera.redraw()
                        scene.redraw()
                    scene.event_handler.tick()
                    scene.update(dt)
                    self._tick += 1
                clock.frame_callback = frame_callback
                clock.update_callback = update_callback
            clock.tick()

=======
import collections
import operator
import itertools
>>>>>>> e956241814be7f503602ab2981b5a1557e0390d9

class Scene(object):
    """
    Represents a state of the game as it runs.

    *self.clock* will contain an instance of GameClock which can be replaced
    or changed as is needed.
    *self.parent_camera* will contain a Camera object that this scene should
    use as the basis for all of it's cameras.
    """
    def __init__(self, parent_camera=None, max_ups=None, max_fps=None):
        """
        By default, max_ups and max_fps are pulled from the director.
        """
        time_source = time.time
        self.clock = spyral.GameClock(
            time_source=time_source,
            max_fps=max_fps or spyral.director._max_fps,
            max_ups=max_ups or spyral.director._max_ups)
        self.clock.use_wait = True
        if parent_camera is None:
            parent_camera = spyral.director.get_camera()

        self.parent_camera = parent_camera
        self._handlers = collections.defaultdict(lambda: [])
        self._namespaces = set()
        self._event_source = spyral.event.LiveEventHandler() # Gotta go rename this now
        self._handling_events = False
        self._events = []
        self._pending = []
    
    # Internal Methods
    
    def _queue_event(self, type, event):
        if self._handling_events:
            self._pending.append((type, event))
        else:
            self._events.append((type, event))

    def _reg_internal(self, namespace, handlers, args, kwargs, priority, dynamic):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        self._namespaces.add(namespace)
        for handler in handlers:
            self._handlers[namespace].append((handler, args, kwargs, priority, dynamic))
        self._handlers[namespace].sort(key=operator.itemgetter(3))
        
    def _get_namespaces(self, namespace):
        return [n for n in self._namespaces if namespace.startswith(n)]
        
    def _send_event_to_handler(self, event, handler, args, kwargs, priority, dynamic):
        try:
            args = [getattr(event, attr) for attr in args]
            kwargs = {attr : getattr(event, attr2) for attr, attr2 in kwargs.iteritems()}
        except Exception:
            pass # Do some error printing
        if dynamic is True:
            h = handler
            handler = self
            for piece in h.split("."):
                handler = getattr(handler, piece, None)
                if handler is None:
                    break
        if handler is not None:
            handler(*args, **kwargs)
    
    def _handle_events(self):
        self._handling_events = True
        do = True
        while do or len(self._pending) > 0:
            do = False
            for (type, event) in self._events:
                quit = False
                for handler_info in itertools.chain.from_iterable(self._handlers[namespace] for namespace in self._get_namespaces(type)):
                    quit = self._send_event_to_handler(event, *handler_info)
                    if quit:
                        break
            self._events = self._pending
            self._pending = []
                    
    # External methods
    
    def load_style(self, filename):
        style = yaml.load(open(filename, 'r'))
        for k, v in style.items():
            try:
                value = eval(v)
                print k, value
            except Exception, e:
                print k, v
        
    def register(self, event_namespace, handler, args = None, kwargs = None, priority = 0):
        """
        I'm gonna pop some tags.
        """
        self._reg_internal(event_namespace, (handler,), args, kwargs, priority, False)

    def register_dynamic(self, event_namespace, handler_string, args = None, kwargs = None, priority = 0):
        self._reg_internal(event_namespace, (handler_string,), args, kwargs, priority, True)

    def register_multiple(self, event_namespace, handlers, args = None, kwargs = None, priority = 0):
        self._reg_internal(event_namespace, handlers, args, kwargs, priority, False)

    def register_multiple_dynamic(self, event_namespace, handler_strings, args = None, kwargs = None, priority = 0):
        self._reg_internal(event_namespace, handler_strings, args, kwargs, priority, True)
        
    def set_event_source(self, source):
        self._event_source = source

    # User Defined Methods

    def on_exit(self):
        """
        Called by the director when this scene is about to run.
        """
        pass

    def on_enter(self):
        """
        Called by the director when this scene is exiting.
        """
        pass

    def render(self):
        """
        Called by the director when a new frame needs to be rendered.
        """
        pass

    def update(self, tick):
        """
        Called by the director when a new game logic step should be taken.
        """
        pass

    def redraw(self):
        """
        Advanced: Called by the director if the scene should force redraw of non-spyral based assets, like PGU
        """
        pass
