from __future__ import division
import spyral
import pygame
import time
import collections
import operator
import itertools
import greenlet
import inspect
import sys
import math
from collections import defaultdict

@spyral.memoize._ImageMemoize
def _scale(s, factor):
    if factor == (1.0, 1.0):
        return s
    size = s.get_size()
    new_size = (int(math.ceil(size[0] * factor[0])),
                int(math.ceil(size[1] * factor[1])))
    t = pygame.transform.smoothscale(s,
                               new_size,
                               pygame.Surface(new_size, pygame.SRCALPHA).convert_alpha())
    return t

class _Blit(object):
    __slots__ = ['surface', 'rect', 'layer', 'flags', 'static', 'clipping']
    def __init__(self, surface, rect, layer, flags, static, clipping):
        self.surface = surface
        self.rect = rect
        self.layer = layer
        self.flags = flags
        self.static = static
        self.clipping = clipping


class Scene(object):
    """
    Represents a state of the game as it runs.

    *self.clock* will contain an instance of GameClock which can be replaced
    or changed as is needed.
    """
    def __init__(self, size = None, max_ups=None, max_fps=None):
        """
        By default, max_ups and max_fps are pulled from the director.
        """
        time_source = time.time
        self.clock = spyral.GameClock(
            time_source=time_source,
            max_fps=max_fps or spyral.director._max_fps,
            max_ups=max_ups or spyral.director._max_ups)
        self.clock.use_wait = True

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

        def TestingBox(size, color):
            i = spyral.Image(size=size)
            i.fill(color)
            return i
        
        self._style_functions['TestingBox'] = TestingBox


        self._size = None
        self._scale = None
        self._surface = pygame.display.get_surface()
        if size is not None:
            self._set_size(size)
        self._background = pygame.surface.Surface(self._surface.get_size())
        self._background.fill((255, 255, 255))
        self._surface.blit(self._background, (0, 0))
        self._blits = []
        self._dirty_rects = []
        self._clear_this_frame = []
        self._clear_next_frame = []
        self._soft_clear = []
        self._static_blits = {}
        self._rect = self._surface.get_rect()

        self._layers = ['all']
        self._sprites = set()

        self.register('director.update', self.handle_events)
        self.register('director.update', self.run_actors, ('dt',))

        # View interface
        self.scene = self

        # Loading default styles
        self.load_style(spyral._get_spyral_path() + 'resources/form_defaults.spys')
    
    # Actor Handling
    def _register_actor(self, actor, greenlet):
        self._greenlets[actor] = greenlet
                    
    def _run_actors_greenlet(self, dt, _):
        for actor, greenlet in self._greenlets.iteritems():
            dt, rerun = greenlet.switch(dt)
            while rerun:
                dt, rerun = greenlet.switch(dt)
        return False

    def run_actors(self, dt):
        g = greenlet.greenlet(self._run_actors_greenlet)
        while True:
            d = g.switch(dt, False)
            if d is True:
                continue
            if d is False:
                break
            g.switch(d, True)
    

    # Event Handling
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
                    
    def handle_events(self):
        self._handling_events = True
        do = True
        while do or len(self._pending) > 0:
            do = False
            for (type, event) in self._events:
                self._handle_event(type, event)
            self._events = self._pending
            self._pending = []

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


    # Style Handling
    def __stylize__(self, properties):
        if 'size' in properties:
            size = properties.pop('size')
            self._set_size(size)
        if 'background' in properties:
            background = properties.pop('background')
            if isinstance(background, (tuple, list)):
                bg = spyral.Image(size=self.size)
                bg.fill(background)
            else:
                bg = spyral.Image(backgronud)
            self.set_background(bg)
        if 'layers' in properties:
            layers = properties.pop('layers')
            self.set_layers(layers)
        if len(properties) > 0:
            spyral.exceptions.unused_style_warning(self, properties.iterkeys())

    def load_style(self, path):
        spyral._style.parse(open(path, "r").read(), self)
        self.apply_style(self)

    def apply_style(self, object):
        if not hasattr(object, "__stylize__"):
            raise spyral.NotStylableError("%r is not an object which can be styled." % object)
        properties = {}
        for cls in reversed(object.__class__.__mro__[:-1]):
            name = cls.__name__
            if name not in self._style_properties:
                continue
            properties.update(self._style_properties[name])
        if hasattr(object, "__style__"):
            name = getattr(object, "__style__")
            if name in self._style_properties:
                properties.update(self._style_properties[name])
        if properties != {}:
            object.__stylize__(properties)

    def add_style_function(self, name, function):
        self._style_functions[name] = function


    # Rendering
    def _get_size(self):
        if self._size is None:
            raise spyral.SceneHasNoSizeException("You should specify a size in the constructor or in a style file before other operations.")
        return self._size

    def _set_size(self, size):
        rsize = self._surface.get_size()
        self._size = size
        self._scale = (rsize[0] / size[0],
                       rsize[1] / size[1])

    size = property(_get_size, _set_size)

    def set_background(self, image):
        surface = image._surf
        scene = spyral._get_executing_scene()
        if surface.get_size() != self.size:
            raise spyral.BackgroundSizeError("Background size must match the scene's size.")
        self._background = pygame.transform.smoothscale(surface, self._surface.get_size())
        self._clear_this_frame.append(surface.get_rect())

    def _register_sprite(self, sprite):
        self._sprites.add(sprite)

    def _unregister_sprite(self, sprite):
        if sprite in self._sprites:
            self._sprites.remove(sprite)

    def _blit(self, surface, position, layer, flags, clipping):
        layer = self._compute_layer(layer)
        position = spyral.point.scale(position, self._scale)
        new_surface = _scale(surface, self._scale)
        r = pygame.Rect(position, new_surface.get_size())

        if self._rect.contains(r):
            pass
        elif self._rect.colliderect(r):
            x = r.clip(self._rect)
            y = x.move(-r.left, -r.top)
            new_surface = new_surface.subsurface(y)
            r = x
        else:
            return
        self._blits.append(_Blit(new_surface, r, layer, flags, False, clipping))

    def _static_blit(self, sprite, surface, position, layer, flags, clipping):
        layer = self._compute_layer(layer)
        position = spyral.point.scale(position, self._scale)
        redraw = sprite in self._static_blits
        if redraw:
            r2 = self._static_blits[sprite][1]
        new_surface = _scale(surface, self._scale)
        r = pygame.Rect(position, new_surface.get_size())
        if self._rect.contains(r):
            pass
        elif self._rect.colliderect(r):
            x = r.clip(self._rect)
            y = x.move(-r.left, -r.top)
            new_surface = new_surface.subsurface(y)
            r = x
        else:
            return
        self._static_blits[sprite] = _Blit(new_surface, r, layer, flags, True, clipping)
        if redraw:
            self._clear_this_frame.append(r2.union(r))
        else:
            self._clear_this_frame.append(r)

    def _remove_static_blit(self, sprite):
        try:
            x = self._static_blits.pop(sprite)
            self._clear_this_frame.append(x.rect)
        except:
            pass

    def _draw(self):
        """
        Called by the director at the end of every .render() call to do
        the actual drawing.
        """

        # This function sits in a potential hot loop
        # For that reason, some . lookups are optimized away
        screen = self._surface

        # Let's finish up any rendering from the previous frame
        # First, we put the background over all blits
        x = self._background.get_rect()
        for i in self._clear_this_frame + self._soft_clear:
            i = x.clip(i)
            b = self._background.subsurface(i)
            screen.blit(b, i)

        # Now, we need to blit layers, while simultaneously re-blitting
        # any static blits which were obscured
        static_blits = len(self._static_blits)
        dynamic_blits = len(self._blits)
        blits = self._blits + list(self._static_blits.values())
        blits.sort(key=operator.attrgetter('layer'))
        
        # Clear this is a list of things which need to be cleared
        # on this frame and marked dirty on the next
        clear_this = self._clear_this_frame
        # Clear next is a list which will become clear_this on the next
        # draw cycle. We use this for non-static blits to say to clear
        # That spot on the next frame
        clear_next = self._clear_next_frame
        # Soft clear is a list of things which need to be cleared on
        # this frame, but unlike clear_this, they won't be cleared
        # on future frames. We use soft_clear to make things static
        # as they are drawn and then no longer cleared
        soft_clear = self._soft_clear
        self._soft_clear = []
        screen_rect = screen.get_rect()
        drawn_static = 0
        
        blit_flags_available = pygame.version.vernum < (1, 8)
        
        for blit in blits:
            blit_clipping_offset, blit_clipping_region = blit.clipping
            blit_rect = blit.rect.move(blit_clipping_offset)
            blit_flags = blit.flags if blit_flags_available else 0
            # If a blit is entirely off screen, we can ignore it altogether
            if not screen_rect.contains(blit_rect) and not screen_rect.colliderect(blit_rect):
                continue
            if blit.static:
                skip_soft_clear = False
                for rect in clear_this:
                    if blit_rect.colliderect(rect):
                        screen.blit(blit.surface, blit_rect, blit_clipping_region, blit_flags)
                        skip_soft_clear = True
                        clear_this.append(blit_rect)
                        self._soft_clear.append(blit_rect)
                        drawn_static += 1
                        break
                if skip_soft_clear:
                    continue
                for rect in soft_clear:
                    if blit_rect.colliderect(rect):
                        screen.blit(blit.surface, blit_rect, blit_clipping_region, blit_flags)
                        soft_clear.append(blit.rect)
                        drawn_static += 1
                        break
            else:                
                if screen_rect.contains(blit_rect):
                    r = screen.blit(blit.surface, blit_rect, blit_clipping_region, blit_flags)
                    clear_next.append(r)
                elif screen_rect.colliderect(blit_rect):
                    x = blit.rect.clip(screen_rect)
                    y = x.move(-blit_rect.left, -blit_rect.top)
                    b = blit.surf.subsurface(y)
                    r = screen.blit(blit.surface, blit_rect, blit_clipping_region, blit_flags)
                    clear_next.append(r)

        pygame.display.set_caption("%d / %d static, %d dynamic. %d ups, %d fps" %
                                   (drawn_static, static_blits,
                                    dynamic_blits, self.clock.ups,
                                    self.clock.fps))
        # Do the display update
        pygame.display.update(self._clear_next_frame + self._clear_this_frame)
        # Get ready for the next call
        self._clear_this_frame = self._clear_next_frame
        self._clear_next_frame = []
        self._blits = []

    def redraw(self):
        self._clear_this_frame.append(pygame.Rect((0,0), self._vsize))


    def _compute_layer(self, layer):
        # This should be optimized at some point.
        if type(layer) in (int, long, float):
            return layer
        try:
            s = layer.split(':')
            layer = s[0]
            offset = 0
            if len(s) > 1:
                mod = s[1]
                if mod == 'above':
                    offset = 0.5
                if mod == 'below':
                    offset = -0.5
            layer = self._layers.index(layer) + offset
        except ValueError:
            layer = len(self._layers)
        return layer

    def set_layers(self, layers):
        # Potential caveat: If you change layers after blitting, previous blits may be wrong
        # for a frame, static ones wrong until they expire
        if self._layers == ['all']:
            self._layers = layers
        elif self._layers == layers:
            pass
        else:
            raise spyral.LayersAlreadySetError("You can only define the layers for a scene once.")

    def world_to_local(self, pos):
        """
        Rename, decide if necessary, perhaps auto-scale the event coordinates inside the scene.
        """
        pos = spyral.Vec2D(pos)
        if self._rect.collidepoint(pos):
            pos = pos / self._scale
            return pos
        return None