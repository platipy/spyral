from __future__ import division
import spyral
import pygame
import time
import operator
import greenlet
import inspect
import sys
from itertools import chain
from layertree import _LayerTree
from collections import defaultdict
from weakref import ref as _wref

class Scene(object):
    """
    Creates a new Scene. When a scene is not active, no events will be processed
    for it. Scenes are the basic units that are executed by spyral for your game,
    and should be subclassed and filled in with code which is relevant to your
    game. The :class:`Director <spyral.director>`, is a manager for Scenes,
    which maintains a stacks and actually executes the code.


    :param size: The `size` of the scene internally (or "virtually"). This is
                 the coordinate space that you place Sprites in, but it does
                 not have to match up 1:1 to the window (which could be scaled).
    :type size: width, height
    :param int max_ups: Maximum updates to process per second. By default,
                        `max_ups` is pulled from the director.
    :param int max_fps: Maximum frames to draw per second. By default,
                        `max_fps` is pulled from the director.
    """
    def __init__(self, size = None, max_ups=None, max_fps=None):
        time_source = time.time
        self.clock = spyral.GameClock(
            time_source=time_source,
            max_fps=max_fps or spyral.director._max_fps,
            max_ups=max_ups or spyral.director._max_ups)
        self.clock.use_wait = True

        self._handlers = defaultdict(lambda: [])
        self._namespaces = set()
        self._event_source = spyral.event.LiveEventHandler()
        self._handling_events = False
        self._events = []
        self._pending = []
        self._greenlets = {} # Maybe need to weakref dict

        self._style_symbols = {}
        self._style_classes = []
        self._style_properties = defaultdict(lambda: {})
        self._style_functions = {}

        self._style_functions['_get_spyral_path'] = spyral._get_spyral_path

        self._size = None
        self._scale = spyral.Vec2D(1.0, 1.0) #None
        self._surface = pygame.display.get_surface()
        if size is not None:
            self._set_size(size)
        display_size = self._surface.get_size()
        self._background = spyral.image._new_spyral_surface(display_size)
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
        self._layer_tree = _LayerTree(self)
        self._sprites = set()

        spyral.event.register('director.scene.enter', self.redraw,
                              scene=self)
        spyral.event.register('director.update', self._handle_events,
                              scene=self)
        spyral.event.register('director.update', self._run_actors, ('delta',),
                              scene=self)
        spyral.event.register('spyral.internal.view.changed',
                              self._invalidate_views, scene=self)

        # View interface
        self._scene = _wref(self)
        self._views = []

        # Loading default styles
        self.load_style(spyral._get_spyral_path() +
                        'resources/form_defaults.spys')

    # Actor Handling
    def _register_actor(self, actor, greenlet):
        """
        Internal method to add a new :class:`Actor <spyral.Actor>` to this
        scene.

        :param actor: The name of the actor object.
        :type actor: :class:`Actor <spyral.Actor>`
        :param greenlet greenlet: The greenlet context for this actor.
        """
        self._greenlets[actor] = greenlet

    def _run_actors_greenlet(self, delta, _):
        """
        Helper method for running the actors.

        :param float delta: The amount of time progressed.
        """
        for actor, greenlet in self._greenlets.iteritems():
            delta, rerun = greenlet.switch(delta)
            while rerun:
                delta, rerun = greenlet.switch(delta)
        return False

    def _run_actors(self, delta):
        """
        Main loop for running actors, switching between their different
        contexts.

        :param float delta: The amount of time progressed.
        """
        g = greenlet.greenlet(self._run_actors_greenlet)
        while True:
            d = g.switch(delta, False)
            if d is True:
                continue
            if d is False:
                break
            g.switch(d, True)

    # Event Handling
    def _queue_event(self, type, event=None):
        """
        Internal method to add a new `event` to be handled by this scene.

        :param str type: The name of the event to queue
        :param event: Metadata about this event.
        :type event: :class:`Event <spyral.Event>`
        """
        if self._handling_events:
            self._pending.append((type, event))
        else:
            self._events.append((type, event))

    def _reg_internal(self, namespace, handlers, args,
                      kwargs, priority, dynamic):
        """
        Convenience method for registering a new event; other variations
        exist to keep the signature convenient and easy.
        """
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        self._namespaces.add(namespace)
        for handler in handlers:
            self._handlers[namespace].append((handler, args, kwargs,
                                              priority, dynamic))
        self._handlers[namespace].sort(key=operator.itemgetter(3))

    def _get_namespaces(self, namespace):
        """
        Internal method for returning all the registered namespaces that are in
        the given namespace.
        """
        return [n for n in self._namespaces if namespace.startswith(n)]

    def _send_event_to_handler(self, event, type, handler, args,
                               kwargs, priority, dynamic):
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
                raise TypeError("Handler expects an argument named "
                                "%s, %s does not have that." %
                                (arg, str(type)))
        if dynamic is True:
            h = handler
            handler = self
            for piece in h.split("."):
                handler = getattr(handler, piece, None)
                if handler is None:
                    return
        if handler is sys.exit and args is None and kwargs is None:
            # Dirty hack to deal with python builtins
            args = []
            kwargs = {}
        elif args is None and kwargs is None:
            # Autodetect the arguments
            try:
                funct = handler.func
            except AttributeError, e:
                funct = handler
            try:
                h_argspec = inspect.getargspec(funct)
            except Exception, e:
                raise Exception(("Unfortunate Python Problem! "
                                 "%s isn't supported by Python's "
                                 "inspect module! Oops.") % str(handler))
            h_args = h_argspec.args
            h_defaults = h_argspec.defaults or tuple()
            if len(h_args) > 0 and 'self' == h_args[0]:
                h_args.pop(0)
            d = len(h_args) - len(h_defaults)
            if d > 0:
                h_defaults = [fillval] * d + list(*h_defaults)
            args = [_get_arg_val(arg, default) for arg, default
                                               in zip(h_args, h_defaults)]
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
        For a given event, send the event information to all registered handlers
        """
        handlers = chain.from_iterable(self._handlers[namespace]
                                            for namespace
                                            in self._get_namespaces(type))
        for handler_info in handlers:
            if self._send_event_to_handler(event, type, *handler_info):
                break

    def _handle_events(self):
        """
        Run through all the events and handle them.
        """
        self._handling_events = True
        do = True
        while do or len(self._pending) > 0:
            do = False
            for (type, event) in self._events:
                self._handle_event(type, event)
            self._events = self._pending
            self._pending = []

    def _unregister(self, event_namespace, handler):
        """
        Unregisters a registered handler for that namespace. Dynamic handler
        strings are supported as well. For more information, see
        `Event Namespaces`_.

        :param str event_namespace: An event namespace
        :param handler: The handler to unregister.
        :type handler: a function or string.
        """
        if event_namespace.endswith(".*"):
            event_namespace = event_namespace[:-2]
        self._handlers[event_namespace] = [h for h
                                             in self._handlers[event_namespace]
                                             if h[0].func is not handler.im_func or h[0].weak_object_ref() is not handler.im_self]

    def _clear_namespace(self, namespace):
        """
        Clears all handlers from namespaces that are at least as specific as the
        provided `namespace`. For more information, see `Event Namespaces`_.

        :param str namespace: The complete namespace.
        """
        if namespace.endswith(".*"):
            namespace = namespace[:-2]
        ns = [n for n in self._namespaces if n.startswith(namespace)]
        for namespace in ns:
            self._handlers[namespace] = []

    def _clear_all_events(self):
        """
        Completely clear all registered events for this scene. This is a very
        dangerous function, and should almost never be used.
        """
        self._handlers.clear()

    def _get_event_source(self):
        """
        The event source can be used to control event playback. Although
        normally events are given through the operating system, you can enforce
        events being played from a file; there is also a mechanism for recording
        events to a file.
        """
        return self._event_source

    def _set_event_source(self, source):
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
            self._set_layers(layers)
        if len(properties) > 0:
            spyral.exceptions.unused_style_warning(self, properties.iterkeys())

    def load_style(self, path):
        """
        Loads the style file in *path* and applies it to this Scene and any
        Sprites and Views that it contains. Most properties are stylable.

        :param path: The location of the style file to load. Should have the
                     extension ".spys".
        :type path: str
        """
        spyral._style.parse(open(path, "r").read(), self)
        self._apply_style(self)

    def _apply_style(self, obj):
        """
        Applies any loaded styles from this scene to the object.

        :param object obj: Any object
        """
        if not hasattr(obj, "__stylize__"):
            raise spyral.NotStylableError(("%r is not an object"
                                           "which can be styled.") % obj)
        properties = {}
        for cls in reversed(obj.__class__.__mro__[:-1]):
            name = cls.__name__
            if name not in self._style_properties:
                continue
            properties.update(self._style_properties[name])
        if hasattr(obj, "__style__"):
            name = getattr(obj, "__style__")
            if name in self._style_properties:
                properties.update(self._style_properties[name])
        if properties != {}:
            obj.__stylize__(properties)

    def add_style_function(self, name, function):
        """
        Adds a new function that will then be available to be used in a
        stylesheet file.

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
        """
        Read-only property that returns a :class:`Vec2D <spyral.Vec2D>` of the
        width and height of the Scene's size.  This is the coordinate space that
        you place Sprites in, but it does not have to match up 1:1 to the window
        (which could be scaled). This property can only be set once.
        """
        if self._size is None:
            raise spyral.SceneHasNoSizeException("You should specify a size in "
                                                 "the constructor or in a "
                                                 "style file before other "
                                                 "operations.")
        return self._size

    def _set_size(self, size):
        # This can only be called once.
        rsize = self._surface.get_size()
        self._size = size
        self._scale = (rsize[0] / size[0],
                       rsize[1] / size[1])

    def _get_width(self):
        """
        The width of this scene. Read-only number.
        """
        return self._get_size()[0]

    def _get_height(self):
        """
        The height of this scene. Read-only number.
        """
        return self._get_size()[1]

    def _get_rect(self):
        """
        Returns a :class:`Rect <spyral.Rect>` representing the position (0, 0)
        and size of this Scene.
        """
        return spyral.Rect((0,0), self.size)

    def _get_scene(self):
        """
        Returns this scene. Read-only.
        """
        return self._scene()

    def _get_parent(self):
        """
        Returns this scene. Read-only.
        """
        return self._scene()


    size = property(_get_size)
    width = property(_get_width)
    height = property(_get_height)
    scene = property(_get_scene)
    parent = property(_get_parent)
    rect = property(_get_rect)

    def _set_background(self, image):
        self._background_image = image
        surface = image._surf
        scene = spyral._get_executing_scene()
        if surface.get_size() != self.size:
            raise spyral.BackgroundSizeError("Background size must match "
                                             "the scene's size.")
        size = self._surface.get_size()
        self._background = pygame.transform.smoothscale(surface, size)
        self._clear_this_frame.append(self._background.get_rect())

    def _get_background(self):
        """
        The background of this scene. The given :class:`Image <spyral.Image>`
        must be the same size as the Scene. A background will be handled
        intelligently by Spyral; it knows to only redraw portions of it rather
        than the whole thing, unlike a Sprite.
        """
        return self._background_image

    background = property(_get_background, _set_background)

    def _register_sprite(self, sprite):
        """
        Internal method to add this sprite to the scene
        """
        self._sprites.add(sprite)
        # Add the view and its parents to the invalidating_views for the sprite
        parent_view = sprite._parent()
        while parent_view != self:
            if parent_view not in self._invalidating_views:
                self._invalidating_views[parent_view] = set()
            self._invalidating_views[parent_view].add(sprite)
            parent_view = parent_view.parent

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
        """
        Remove all references to the view from within this Scene.
        """
        if view in self._invalidating_views:
            del self._invalidating_views[view]
        if view in self._collision_boxes:
            del self._collision_boxes[view]
        self._layer_tree.remove_view(view)

    def _blit(self, blit):
        """
        Apply any scaling associated with the Scene to the Blit, then finalize
        it. Note that Scene's don't apply cropping.
        """
        blit.apply_scale(self._scale)
        blit.finalize()
        self._blits.append(blit)

    def _static_blit(self, key, blit):
        """
        Identifies that this sprite will be statically blit from now, and
        applies scaling and finalization to the blit.
        """
        blit.apply_scale(self._scale)
        blit.finalize()
        self._static_blits[key] = blit
        self._clear_this_frame.append(blit.rect)

    def _invalidate_views(self, view):
        """
        Expire any sprites that belong to the view being invalidated.
        """
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
        Internal method that is called by the
        :class:`Director <spyral.Director>` at the end of every .render() call
        to do the actual drawing.
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

        #pygame.display.set_caption("%d / %d static, %d dynamic. %d ups, %d fps" %
        #                           (drawn_static, static_blits,
        #                            dynamic_blits, self.clock.ups,
        #                            self.clock.fps))
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
        """
        For the given view and layer, calculate its position in the depth order.
        """
        return self._layer_tree.get_layer_position(view, layer)

    def _set_view_layer(self, view, layer):
        """
        Set the layer that the view is on within layer tree.
        """
        self._layer_tree.set_view_layer(view, layer)

    def _set_view_layers(self, view, layers):
        """
        Set the view's layers within the layer tree.
        """
        self._layer_tree.set_view_layers(view, layers)

    def _add_view(self, view):
        """
        Register the given view within this scene.
        """
        self._layer_tree.add_view(view)

    def _set_layers(self, layers):
        """
        Potential caveat: If you change layers after blitting, previous blits
        may be wrong for a frame, static ones wrong until they expire
        """
        if self._layers == []:
            self._layer_tree.set_view_layers(self, layers)
            self._layers = layers
        elif self._layers == layers:
            pass
        else:
            raise spyral.LayersAlreadySetError("You can only define the layers "
                                               "for a scene once.")

    def _get_layers(self):
        """
        A list of strings representing the layers that are available for this
        scene. The first layer is at the bottom, and the last is at the top.

        Note that the layers can only be set once.
        """
        return self._layers

    layers = property(_get_layers, _set_layers)

    def _add_child(self, entity):
        """
        Add this child to the Scene; since only Views care about their children,
        this function does nothing.
        """
        pass

    def _remove_child(self, entity):
        """
        Remove this child to the Scene; since only Views care about their
        children, this function does nothing.
        """
        pass

    def _warp_collision_box(self, box):
        """
        Modify the given collision box according to this Scene's scaling, and
        then finalize it.
        """
        box.apply_scale(self._scale)
        box.finalize()
        return box

    def _set_collision_box(self, entity, box):
        """
        Registers the given entity (a View or Sprite) with the given
        CollisionBox.
        """
        self._collision_boxes[entity] = box

    def collide_sprites(self, first, second):
        """
        Returns whether the first sprite is colliding with the second.

        :param first: A sprite or view
        :type first: :class:`Sprite <spyral.Sprite>` or a
                     :class:`View <spyral.View>`
        :param second: Another sprite or view
        :type second: :class:`Sprite <spyral.Sprite>` or a
                      :class:`View <spyral.View>`
        :returns: A ``bool``
        """
        if first not in self._collision_boxes or second not in self._collision_boxes:
            return False
        first_box = self._collision_boxes[first]
        second_box = self._collision_boxes[second]
        return first_box.collide_rect(second_box)

    def collide_point(self, sprite, point):
        """
        Returns whether the sprite is colliding with the point.

        :param sprite: A sprite
        :type sprite: :class:`Sprite <spyral.Sprite>`
        :param point: A point
        :type point: :class:`Vec2D <spyral.Vec2D>`
        :returns: A ``bool``
        """
        if sprite not in self._collision_boxes:
            return False
        sprite_box = self._collision_boxes[sprite]
        return sprite_box.collide_point(point)

    def collide_rect(self, sprite, rect):
        """
        Returns whether the sprite is colliding with the rect.

        :param sprite: A sprite
        :type sprite: :class:`Sprite <spyral.Sprite>`
        :param rect: A rect
        :type rect: :class:`Rect <spyral.Rect>`
        :returns: A ``bool``
        """
        if sprite not in self._collision_boxes:
            return False
        sprite_box = self._collision_boxes[sprite]
        return sprite_box.collide_rect(rect)
