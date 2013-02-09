import spyral
import time
import yaml
import collections
import operator
import itertools
import greenlet        

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
        self._greenlets = {} # Maybe need to weakref dict
        
        self.register('spyral.director.update', self.handle_events)
        self.register('spyral.director.update', self.run_actors, ('dt',))
    
    # Internal Methods
    
    def _register_actor(self, actor, greenlet):
        self._greenlets[actor] = greenlet
                    
    def _run_actors_greenlet(self, dt, _):
        for actor, greenlet in self._greenlets.iteritems():
            dt, rerun = greenlet.switch(dt)
            while rerun:
                dt, rerun = greenlet.switch(dt)
        return False

    
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
            kwargs = dict((attr, getattr(event, attr2)) for attr, attr2 in kwargs.iteritems())
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
    
    def _handle_event(self, type, event):
        for handler_info in itertools.chain.from_iterable(self._handlers[namespace] for namespace in self._get_namespaces(type)):
            if self._send_event_to_handler(event, *handler_info):
                break
                    
    # External methods

    def handle_events(self):
        self._handling_events = True
        do = True
        while do or len(self._pending) > 0:
            do = False
            for (type, event) in self._events:
                self._handle_event(type, event)
            self._events = self._pending
            self._pending = []
            
    def run_actors(self, dt):
        g = greenlet.greenlet(self._run_actors_greenlet)
        while True:
            d = g.switch(dt, False)
            if d is True:
                continue
            if d is False:
                break
            g.switch(d, True)
    
    def load_style(self, filename):
        style = yaml.load(open(filename, 'r'))
        result = self.parse(style)
        print result
    
    def parse(self, style):
        result = {}
        try:
            for k, v in style.items():
                try:
                    value = eval(v)
                    result[k] = value
                except Exception, e:
                    result[k] = self.parse(v)
            return result
        except Exception, e:
            return style
        
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
