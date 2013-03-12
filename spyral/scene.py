import spyral
import time
import collections
import operator
import itertools
import greenlet
import inspect
import sys
from collections import defaultdict

class Scene(object):
    """
    Represents a state of the game as it runs.

    *self.clock* will contain an instance of GameClock which can be replaced
    or changed as is needed.
    """
    def __init__(self, size, max_ups=None, max_fps=None):
        """
        By default, max_ups and max_fps are pulled from the director.
        """
        time_source = time.time
        self.clock = spyral.GameClock(
            time_source=time_source,
            max_fps=max_fps or spyral.director._max_fps,
            max_ups=max_ups or spyral.director._max_ups)
        self.clock.use_wait = True

        self._camera = spyral.director._get_camera().make_child(size)
        self._handlers = collections.defaultdict(lambda: [])
        self._namespaces = set()
        self._event_source = spyral.event.LiveEventHandler() # Gotta go rename this now
        self._handling_events = False
        self._events = []
        self._pending = []
        self._greenlets = {} # Maybe need to weakref dict

        self._style_symbols = {}
        self._style_classes = []
        self._style_properties = defaultdict(lambda: {})
        self._style_functions = {}

        
        self.register('director.update', self.handle_events)
        self.register('director.update', self.run_actors, ('dt',))
    
    # Internal Methods
    
    def _register_actor(self, actor, greenlet):
        self._greenlets[actor] = greenlet
                    
    def _run_actors_greenlet(self, dt, _):
        for actor, greenlet in self._greenlets.iteritems():
            dt, rerun = greenlet.switch(dt)
            while rerun:
                dt, rerun = greenlet.switch(dt)
        return False

    
    def _queue_event(self, type, event = None):
        if self._handling_events:
            self._pending.append((type, event))
        else:
            self._events.append((type, event))

    def _reg_internal(self, namespace, handlers, args, kwargs, priority, dynamic):
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        self._namespaces.add(namespace)
        for handler in handlers:
            self._handlers[namespace].append((handler, args, kwargs, priority, dynamic))
        self._handlers[namespace].sort(key=operator.itemgetter(3))
        
    def _get_namespaces(self, namespace):
        return [n for n in self._namespaces if namespace.startswith(n)]
        
    def _send_event_to_handler(self, event, handler, args, kwargs, priority, dynamic):
        fillval = "__spyral_itertools_fillvalue__"
        def _get_arg_val(arg, default = fillval):
            if arg == 'event':
                return event
            elif hasattr(event, arg):
                return getattr(event, arg)
            else:
                if default != fillval:
                    return default
                raise TypeError("Handler expects an argument of named %s, %s does not have that." % (arg, str(event)))

        if dynamic is True:
            h = handler
            handler = self
            for piece in h.split("."):
                handler = getattr(handler, piece, None)
                if handler is None:
                    return
        if handler is sys.exit and args is None and kwargs is None:
            # This is a dirty hack. If only Python's builtin functions worked better
            args = []
            kwargs = {}
        elif args is None and kwargs is None:
            # Autodetect the arguments 
            try:
                h_argspec = inspect.getargspec(handler)
            except Exception, e:
                raise Exception("Unfortunate Python Problem! %s isn't supported by Python's inspect module! Oops." % str(handler))
            h_args = h_argspec.args
            h_defaults = h_argspec.defaults or tuple()
            if len(h_args) > 0 and 'self' == h_args[0]:
                h_args.pop(0)
            d = len(h_args) - len(h_defaults)
            if d > 0:
                h_defaults = [fillval] * d + list(*h_defaults)
            args = [_get_arg_val(arg, default) for arg, default in zip(h_args, h_defaults)]
            kwargs = {}
        elif args is None:
            args = []
            kwargs = dict([(arg, _get_arg_val(arg)) for arg in kwargs])
        else:
            args = [_get_arg_val(arg) for arg in args]
            kwargs = {}
        if handler is not None:
            handler(*args, **kwargs)
    
    def _handle_event(self, type, event = None):
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
        
    def unregister(self, event_namespace, handler):
        """
        Unregisters a registered handler. Dynamic handler strings are supported as well.
        """
        if event_namespace.endswith(".*"):
            event_namespace = event_namespace[:-2]
        self._handlers[event_namespace] = [h for h in self._handlers[event_namespace] if h[0] != handler]

    def clear_namespace(self, namespace):
        """
        Clears all handlers from namespaces that are at least as specific as the provided namespace.
        """
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        ns = [n for n in self._namespaces if n.startswith(namespace)]
        for namespace in ns:
            self._handlers[namespace] = []
        
    def set_event_source(self, source):
        self._event_source = source

    def load_style(self, path):
        spyral._style.parse(open(path, "r").read(), self)

    def apply_style(self, style_name, object):
        if style_name not in self._style_properties:
            return

        properties = self._style_properties[style_name]
        for property, value in properties.iteritems():
            setattr(object, property, value)

    def set_background(self, image):
        self._camera.set_background(image)