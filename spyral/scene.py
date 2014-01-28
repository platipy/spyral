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
from layertree import LayerTree
from collections import defaultdict

class Scene(object):
    """
    Creates a new Scene. When a scene is not active, no events will be processed 
        for it.
    
    :param size: The `size` of the scene internally (or "virtually"). See `View size and Window size`_ for more details.
    :type size: width, height
    :param max_ups: Maximum updates to process per second. By default, `max_ups`
        is pulled from the director.
    :type max_ups: int
    :param max_fps: Maximum frames to draw per second. By default, `max_fps` is 
        pulled from the director.
    :type max_fps: int
    """
    def __init__(self, size = None, max_ups=None, max_fps=None):
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
        
        self._style_functions['_get_spyral_path'] = spyral._get_spyral_path
        self._style_functions['TestingBox'] = TestingBox

        self._size = None
        self._scale = spyral.Vec2D(1.0, 1.0) #None
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
        self._invalidating_views = {}
        self._collision_boxes = {}
        self._rect = self._surface.get_rect()

        self._layers = []
        self._child_views = []
        self._layer_tree = LayerTree(self)
        self._sprites = set()

        self.register('director.update', self.handle_events)
        self.register('director.update', self.run_actors, ('dt',))
        self.register('spyral.internal.view.changed.*', self._invalidate_views)

        # View interface
        self.scene = self
        self._parent = self
        self._views = []

        # Loading default styles
        self.load_style(spyral._get_spyral_path() + 'resources/form_defaults.spys')
    
    # Actor Handling
    def _register_actor(self, actor, greenlet):
        """ 
        Internal method to add a new `actor` to this scene.
        """
        self._greenlets[actor] = greenlet
                    
    def _run_actors_greenlet(self, dt, _):
        """
        Helper method for run_actors to TODO: What does this do?
        """
        for actor, greenlet in self._greenlets.iteritems():
            dt, rerun = greenlet.switch(dt)
            while rerun:
                dt, rerun = greenlet.switch(dt)
        return False

    def run_actors(self, dt):
        """
        TODO: Is this an internal method? What circumstances warrant it being called explicitly?
        Main loop for running actors (until they TODO: What causes the loop to stop?
        """
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
        """
        Internal method to add a new `event` to be handled by this scene.
        """
        if self._handling_events:
            self._pending.append((type, event))
        else:
            self._events.append((type, event))

    def _reg_internal(self, namespace, handlers, args, kwargs, priority, dynamic):
        """
        TODO: Convenience method for registering a new event?
        """
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        self._namespaces.add(namespace)
        for handler in handlers:
            self._handlers[namespace].append((handler, args, kwargs, priority, dynamic))
        self._handlers[namespace].sort(key=operator.itemgetter(3))
        
    def _get_namespaces(self, namespace):
        """
        Internal method for returning all the registered namespaces that are in
        the given namespace. TODO: Could we document what exactly a namespace is?
        """
        return [n for n in self._namespaces if namespace.startswith(n)]
        
    def _send_event_to_handler(self, event, handler, args, kwargs, priority, dynamic):
        """
        Internal method to dispatch events to their handlers.
        """
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
        """
        TODO: Why did I think I could document this? What does this do??
        """
        for handler_info in itertools.chain.from_iterable(self._handlers[namespace] for namespace in self._get_namespaces(type)):
            if self._send_event_to_handler(event, *handler_info):
                break
                    
    def handle_events(self):
        """
        TODO: Is this an internal method? What circumstance requires the user to call it?
        """
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
        Registers an event `handler` to a namespace. Whenever an event in that `event_namespace` is fired, the event `handler`
        will execute with that event. For more information, see `Event Namespaces`_.
        
        :param event_namespace: the namespace of the event, e.g. "input.mouse.left.click" or "ball.collides.paddle".
        :type event_namespace: string
        :param handler: A function that will handle the event. The first argument to the function will be the event.
        :type handler: function
        :param args: any additional arguments that need to be passed in to the handler.
        :type args: sequence
        :param kwargs: any additional keyword arguments that need to be passed into the handler.
        :type kwargs: dict
        :param priority: the higher the `priority`, the sooner this handler will be called in reaction to the event, relative to the other event handlers registered.
        :type priority: int
        """
        self._reg_internal(event_namespace, (handler,), args, kwargs, priority, False)

    def register_dynamic(self, event_namespace, handler_string, args = None, kwargs = None, priority = 0):
        """
        Similar to :func:`spyral.Scene.register` function, except that instead of passing in a function, you pass in the name of a property of this scene that holds a function. For more information, see `Event Namespaces`_.
        
        Example::
        
            class MyScene(Scene):
                def __init__(self):
                    ...
                    self.register_dynamic("orc.dies", "something") #TODO: I can't think of a good example...
                    ...
                    
        TODO: Also, we need to mention how you can have multiple dots in the handler_string!
        """
        self._reg_internal(event_namespace, (handler_string,), args, kwargs, priority, True)

    def register_multiple(self, event_namespace, handlers, args = None, kwargs = None, priority = 0):
        """
        Similar to :func:`spyral.Scene.register` function, except a sequence of `handlers` are be given
        instead of just one. For more information, see `Event Namespaces`_.
        """
        self._reg_internal(event_namespace, handlers, args, kwargs, priority, False)

    def register_multiple_dynamic(self, event_namespace, handler_strings, args = None, kwargs = None, priority = 0):
        """
        Similar to :func:`spyral.Scene.register` function, except a sequence of strings representing handlers can be given
        instead of just one.
        """
        self._reg_internal(event_namespace, handler_strings, args, kwargs, priority, True)
        
    def unregister(self, event_namespace, handler):
        """
        Unregisters a registered handler for that namespace. Dynamic handler strings are supported as well. For more information, see `Event Namespaces`_.
        
        :param event_namespace: An event namespace
        :type event_namespace: string
        :param handler: The handler to unregister.
        :type handler: a function or string.
        """
        if event_namespace.endswith(".*"):
            event_namespace = event_namespace[:-2]
        self._handlers[event_namespace] = [h for h in self._handlers[event_namespace] if h[0] != handler]

    def clear_namespace(self, namespace):
        """
        Clears all handlers from namespaces that are at least as specific as the provided `namespace`. For more information, see `Event Namespaces`_.
        TODO: We need an Appendix on event namespaces
        :param namespace: The complete namespace.
        :type namespace: string
        """
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        ns = [n for n in self._namespaces if n.startswith(namespace)]
        for namespace in ns:
            self._handlers[namespace] = []
        
    def set_event_source(self, source):
        """
        TODO: What's the status on this?
        """
        self._event_source = source


    # Style Handling
    def __stylize__(self, properties):
        """
        Applies the *properties* to this scene. This is called when a style
        is applied.

        :param properties: a mapping of property names (strings) to values.
        :type properties: dict
        """
        if 'size' in properties:
            size = properties.pop('size')
            self._set_size(size)
        if 'background' in properties:
            background = properties.pop('background')
            if isinstance(background, (tuple, list)):
                bg = spyral.Image(size=self.size)
                bg.fill(background)
            else:
                bg = spyral.Image(background)
            self._set_background(bg)
        if 'layers' in properties:
            layers = properties.pop('layers')
            self.set_layers(layers)
        if len(properties) > 0:
            spyral.exceptions.unused_style_warning(self, properties.iterkeys())

    def load_style(self, path):
        """
        Loads the style file in *path* and applies it to this Scene and any Sprites that it contains. See `Stylable Properties`_ for more details.
        
        :param path: the location of the style file to load. Usually has the extension ".spys".
        :type path: string
        """
        spyral._style.parse(open(path, "r").read(), self)
        self.apply_style(self)

    def apply_style(self, object):
        """
        TODO: Should this be an internal method?
        Applies any loaded styles to this scene.
        """
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
        """
        Adds a new function that will then be available to be used in a stylesheet file.
        
        Example::
        
            import random
            class MyScene(spyral.Scene):
                def __init__(self):
                    ...
                    self.load_style("my_style.spys")
                    self.add_style_function("randint", random.randint)
                    # inside of style file you can now use the randint function!
                    ...
                
        
        :param name: The name the function will go by in the style file.
        :type name: string
        :param function: The actual function to add to the style file.
        :type function: function
        """
        self._style_functions[name] = function


    # Rendering
    def _get_size(self):
        if self._size is None:
            raise spyral.SceneHasNoSizeException("You should specify a size in the constructor or in a style file before other operations.")
        return self._size

    def _set_size(self, size):
        # This can only be called once.
        rsize = self._surface.get_size()
        self._size = size
        self._scale = (rsize[0] / size[0],
                       rsize[1] / size[1])

    def _get_width(self):
        return self._get_size()[0]

    def _get_height(self):
        return self._get_size()[1]
    
    def _get_rect(self):
        return spyral.Rect((0,0), self.size)

    #: Read-only property that returns a :class:`Vec2D <spyral.Vec2D>` of the width and height of the Scene's size. See `View size and Window size`_ for more details.
    size = property(_get_size)
    #: Read-only property that returns the width of the Scene (int).
    width = property(_get_width)
    #: Read-only property that returns the height of the Scene (int).
    height = property(_get_height)
    
    rect = property(_get_rect)

    def _set_background(self, image):
        surface = image._surf
        scene = spyral._get_executing_scene()
        if surface.get_size() != self.size:
            raise spyral.BackgroundSizeError("Background size must match the scene's size.")
        self._background = pygame.transform.smoothscale(surface, self._surface.get_size())
        self._clear_this_frame.append(self._background.get_rect())
        
    def _get_background(self):
        return self._background
        
    #: Sets the background of this scene to the `image` (:class:`Image <spyral.Image>`). The `image` must be the same size as the background. A background will be handled intelligently by Spyral; it knows to only redraw portions of it rather than the whole thing.
    background = property(_get_background, _set_background)

    def _register_sprite(self, sprite):
        """
        Internal method to add this sprite to the scene
        """
        self._sprites.add(sprite)
        # Add the view and its parents to the invalidating_views for the sprite
        parent_view = sprite._view
        while parent_view != self:
            if parent_view not in self._invalidating_views:
                self._invalidating_views[parent_view] = set()
            self._invalidating_views[parent_view].add(sprite)
            parent_view = parent_view._parent

    def _unregister_sprite(self, sprite):
        """
        Internal method to remove this sprite from the scene
        """
        if sprite in self._sprites:
            self._sprites.remove(sprite)
        if sprite in self._collision_boxes:
            del self._collision_boxes[sprite]
        for view in self._invalidating_views.keys():
            self._invalidating_views[view].discard(sprite)
            
    def _kill_view(self, view):
        if view in self._invalidating_views:
            del self._invalidating_views[view]
        if view in self._collision_boxes:
            del self._collision_boxes[view]
        self._layer_tree.remove_view(view)

    def _blit(self, blit):
        blit.apply_scale(self._scale)
        blit.clip(self._rect)
        blit.finalize()
        self._blits.append(blit)

    def _static_blit(self, key, blit):
        """
        Identifies that this sprite will be statically blit from now.
        """
        blit.apply_scale(self._scale)
        blit.clip(self._rect)
        blit.finalize()
        self._static_blits[key] = blit
        self._clear_this_frame.append(blit.rect)
        
    def _invalidate_views(self, view):
        if view in self._invalidating_views:
            for sprite in self._invalidating_views[view]:
                sprite._expire_static()

    def _remove_static_blit(self, key):
        """
        Removes this sprite from the static blit list
        """
        try:
            x = self._static_blits.pop(key)
            self._clear_this_frame.append(x.rect)
        except:
            pass

    def _draw(self):
        """
        Internal method that is called by the :class:`Director <spyral.Director>` at the end of every .render() call to do
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
            blit_rect = blit.rect
            blit_flags = blit.flags if blit_flags_available else 0
            # If a blit is entirely off screen, we can ignore it altogether
            if not screen_rect.contains(blit_rect) and not screen_rect.colliderect(blit_rect):
                continue
            if blit.static:
                skip_soft_clear = False
                for rect in clear_this:
                    if blit_rect.colliderect(rect):
                        screen.blit(blit.surface, blit_rect, None, blit_flags)
                        skip_soft_clear = True
                        clear_this.append(blit_rect)
                        self._soft_clear.append(blit_rect)
                        drawn_static += 1
                        break
                if skip_soft_clear:
                    continue
                for rect in soft_clear:
                    if blit_rect.colliderect(rect):
                        screen.blit(blit.surface, blit_rect, None, blit_flags)
                        soft_clear.append(blit.rect)
                        drawn_static += 1
                        break
            else:
                if screen_rect.contains(blit_rect):
                    r = screen.blit(blit.surface, blit_rect, None, blit_flags)
                    clear_next.append(r)
                elif screen_rect.colliderect(blit_rect):
                    # Todo: See if this is ever called. Shouldn't be.
                    x = blit.rect.clip(screen_rect)
                    y = x.move(-blit_rect.left, -blit_rect.top)
                    b = blit.surface.subsurface(y)
                    r = screen.blit(blit.surface, blit_rect, None, blit_flags)
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
        """
        Force the entire visible window to be completely redrawn.
        
        This is particularly useful for Sugar, which loves to put artifacts over
        our window.
        """
        self._clear_this_frame.append(pygame.Rect(self._rect))

    def _get_layer_position(self, view, layer):
        return self._layer_tree.get_layer_position(view, layer)
    
    def _set_view_layer(self, view, layer):
        self._layer_tree.set_view_layer(view, layer)
    def _set_view_layers(self, view, layers):
        self._layer_tree.set_view_layers(view, layers)
    def _add_view(self, view):
        self._layer_tree.add_view(view)
        
    def _compute_layer(self, layer):
        """
        Computes the numerical index of `layer` (in reference to the other layers).
        """
        return spyral.util.compute_layer(self._layers, layer)

    def set_layers(self, layers):
        """
        TODO: Should this be internal?
        """
        # Potential caveat: If you change layers after blitting, previous blits may be wrong
        # for a frame, static ones wrong until they expire
        if self._layers == []:
            self._layer_tree.set_view_layers(self, layers)
            self._layers = layers
        elif self._layers == layers:
            pass
        else:
            raise spyral.LayersAlreadySetError("You can only define the layers for a scene once.")
            
    def _get_layers(self):
        return self._layers
        
    #: Returns the list of layers for this Scene, which are represented by strings. The first layer is at the bottom, and the last is at the top.
    layers = property(_get_layers)

    def world_to_local(self, pos):
        """
        TODO: Rename, decide if necessary, perhaps auto-scale the event coordinates inside the scene.
        """
        pos = spyral.Vec2D(pos)
        if self._rect.collidepoint(pos):
            pos = pos / self._scale
            return pos
        return None
        
    def _add_child(self, entity): pass
    def _remove_child(self, entity): pass
        
    def _warp_collision_box(self, box):
        box.apply_scale(self._scale)
        box.finalize()
        return box
    
    def _set_collision_box(self, entity, box):
        self._collision_boxes[entity] = box

    def collide_sprite(self, first, second):
        if first not in self._collision_boxes or second not in self._collision_boxes:
            return False
        first_box = self._collision_boxes[first]
        second_box = self._collision_boxes[second]
        return first_box.collide_rect(second_box)
    def collide_point(self, sprite, pos):
        if sprite not in self._collision_boxes:
            return False
        sprite_box = self._collision_boxes[sprite]
        return sprite_box.collide_point(pos)
    def collide_rect(self, sprite, rect):
        if sprite not in self._collision_boxes:
            return False
        sprite_box = self._collision_boxes[sprite]
        return sprite_box.collide_rect(rect)
