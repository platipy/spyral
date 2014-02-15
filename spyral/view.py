import spyral
from weakref import ref as _wref

class View(object):
    """
    Creates a new view with a scene or view as a parent. A view is a collection
    of Sprites and Views that can be collectively transformed - e.g., flipped,
    cropped, scaled, offset, hidden, etc. A View can also have a ``mask``, in
    order to treat it as a single collidable object. Like a Sprite, a View cannot
    be moved between Scenes.
    
    :param parent: The view or scene that this View belongs in.
    :type parent: :func:`View <spyral.View>` or :func:`Scene <spyral.Scene>`
    """
    def __init__(self, parent):

        self._size = spyral.Vec2D(parent.size)
        self._output_size = spyral.Vec2D(parent.size)
        self._crop_size = spyral.Vec2D(parent.size)
        self._pos = spyral.Vec2D(0,0)
        self._crop = False
        self._visible = True
        self._parent = _wref(parent)
        self._anchor = 'topleft'
        self._offset = spyral.Vec2D(0,0)
        self._layers = []
        self._layer = None
        self._mask = None

        self._children = set()
        self._child_views = set()
        self._scene = _wref(parent.scene)
        self._scene()._add_view(self)
        self._parent()._add_child(self)
        self._scene()._apply_style(self)

    def _add_child(self, entity):
        """
        Starts keeping track of the entity as a child of this view.

        :param entity: The new entity to keep track of.
        :type entity: a View or a Sprite.
        """
        self._children.add(entity)
        if isinstance(entity, View):
            self._child_views.add(entity)

    def _remove_child(self, entity):
        """
        Stops keeping track of the entity as a child of this view, if it exists.

        :param entity: The entity to keep track of.
        :type entity: a View or a Sprite.
        """
        self._children.discard(entity)
        self._child_views.discard(entity)

    def kill(self):
        """
        Completely remove any parent's links to this view. When you want to
        remove a View, you should call this function.
        """
        for child in list(self._children):
            child.kill()
        self._children.clear()
        self._child_views.clear()
        self._scene()._kill_view(self)

    def _get_mask(self):
        """
        Return this View's mask, a spyral.Rect representing the collidable area.
        
        :rtype: :class:`Rect <spyral.Rect>` if this value has been set,
                otherwise it will be ``None``.
        """
        return self._mask

    def _set_mask(self, mask):
        """
        Set this View's mask. Triggers a recomputation of the collision box.
        :param mask: The region that this View collides with, or None
        (indicating that the default should be used).
        :type mask: a :class:`Rect <spyral.Rect>`, or None.
        """
        self._mask = mask
        self._set_collision_box()

    def _set_collision_box_tree(self):
        """
        Set this View's collision box, and then also recursively recompute
        the collision box for any child Views.
        """
        self._set_collision_box()
        for view in self._child_views:
            view._set_collision_box_tree()

    def _changed(self):
        """
        Called when this View has changed a visual property, ensuring that the
        offset and collision box are recomputed; also triggers a
        `spyral.internal.view.changed` event.
        """
        self._recalculate_offset()
        self._set_collision_box_tree()
        # Notify any listeners (probably children) that I have changed
        changed_event = spyral.Event(name="changed", view=self)
        spyral.event.handle("spyral.internal.view.changed",
                            changed_event,
                            self.scene)

    def _recalculate_offset(self):
        """
        Recalculates the offset of this View.
        """
        if self._mask:
            self._offset = spyral.util._anchor_offset(self._anchor, 
                                                     self._mask.size[0], 
                                                     self._mask.size[1])
        else:
            self._offset = spyral.util._anchor_offset(self._anchor, 
                                                     self._size[0], 
                                                     self._size[1])

    # Properties
    def _get_pos(self):
        """
        Returns the position (:func:`Vec2D <spyral.Vec2D>`) of this View within its
        parent.
        """
        return self._pos

    def _set_pos(self, pos):
        if pos == self._pos:
            return
        self._pos = spyral.Vec2D(pos)
        self._changed()

    def _get_layer(self):
        """
        The layer (a ``str``) that this View is on, within its parent.
        """
        return self._layer

    def _set_layer(self, layer):
        if layer == self._layer:
            return
        self._layer = layer
        self._scene()._set_view_layer(self, layer)
        self._changed()

    def _get_layers(self):
        """
        A list of strings representing the layers that are available for this
        view. The first layer is at the bottom, and the last is at the top. For
        more information on layers, check out the :ref:`layers <ref.layering>`
        appendix.

        .. note:
            
            Layers can only be set once.
        """
        return tuple(self._layers)

    def _set_layers(self, layers):
        if not self._layers:
            self._layers = layers[:]
            self._scene()._set_view_layers(self, layers)
        elif self._layers == layers:
            pass
        else:
            raise spyral.LayersAlreadySetError("You can only define the "
                                               "layers for a view once.")

    def _get_x(self):
        """
        The x coordinate of the view, which will remain synced with the
        position. Number.
        """
        return self._get_pos()[0]

    def _set_x(self, x):
        self._set_pos((x, self._get_y()))

    def _get_y(self):
        """
        The y coordinate of the view, which will remain synced with the
        position. Number.
        """
        return self._get_pos()[1]

    def _set_y(self, y):
        self._set_pos((self._get_x(), y))

    def _get_anchor(self):
        """
        Defines an :ref:`anchor point <ref.anchors>` where coordinates are relative to
        on the view. String.
        """
        return self._anchor

    def _set_anchor(self, anchor):
        if anchor == self._anchor:
            return
        self._anchor = anchor
        self._recalculate_offset()
        self._changed()

    def _get_width(self):
        """
        The width of the view. Number.
        """
        return self._size[0]

    def _set_width(self, width):
        self._set_size(width, self._get_height())

    def _get_height(self):
        """
        The height of the view. Number.
        """
        return self._size[1]

    def _set_height(self, height):
        self._set_size(self._get_width(), height)

    def _get_output_width(self):
        """
        The width of this view when drawn on the parent. Number.
        """
        return self._output_size[0]

    def _set_output_width(self, width):
        self._set_output_size((width, self._get_output_height()))

    def _get_output_height(self):
        """
        The height of this view when drawn on the parent. Number.
        """
        return self._output_size[1]

    def _set_output_height(self, height):
        self._set_output_size((self._get_output_width(), height))

    def _get_crop_width(self):
        """
        The width of the cropped area. Number.
        """
        return self._crop_size[0]

    def _set_crop_width(self, width):
        self._set_crop_size((width, self._get_crop_height()))

    def _get_crop_height(self):
        """
        The height of the cropped area. Number.
        """
        return self._crop_size[1]

    def _set_crop_height(self, height):
        self._set_crop_size((self._get_crop_width(), height))

    def _get_size(self):
        """
        The (width, height) of this view's coordinate space
        (:class:`Vec2D <spyral.Vec2d>`). Defaults to size of the parent.
        """
        return self._size

    def _set_size(self, size):
        if size == self._size:
            return
        self._size = spyral.Vec2D(size)
        self._changed()

    def _get_output_size(self):
        """
        The (width, height) of this view when drawn on the parent
        (:class:`Vec2D <spyral.Vec2d>`). Defaults to size of the parent.
        """
        return self._output_size

    def _set_output_size(self, size):
        if size == self._output_size:
            return
        self._output_size = spyral.Vec2D(size)
        self._changed()

    def _get_crop_size(self):
        """
        The (width, height) of the area that will be cropped; anything outside
        of this region will be removed when the crop is active.
        """
        return self._crop_size

    def _set_crop_size(self, size):
        if size == self._crop_size:
            return
        self._crop_size = spyral.Vec2D(size)
        self._changed()

    def _get_scale(self):
        """
        A scale factor from the size to the output_size for the view. It will
        always contain a :class:`Vec2D <spyral.Vec2D>` with an x factor and a
        y factor, but it can be set to a numeric value which will be set for
        both coordinates.
        """
        return self._output_size / self._size

    def _set_scale(self, scale):
        if isinstance(scale, (int, float)):
            scale = spyral.Vec2D(scale, scale)
        if scale == self._get_scale():
            return
        self._output_size = self._size * spyral.Vec2D(scale)
        self._changed()

    def _get_scale_x(self):
        """
        The x factor of the scaling. Kept in sync with scale. Number.
        """
        return self._get_scale()[0]

    def _get_scale_y(self):
        """
        The y factor of the scaling. Kept in sync with scale. Number.
        """
        return self._get_scale()[1]

    def _set_scale_x(self, x):
        self._set_scale((x, self._get_scale()[1]))

    def _set_scale_y(self, y):
        self._set_scale((self._get_scale()[0], y))

    def _get_visible(self):
        """
        Whether or not this View and its children will be drawn (``bool``).
        Defaults to ``False``.
        """
        return self._visible

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self._changed()

    def _get_crop(self):
        """
        A ``bool`` that determines whether the view should crop anything
        outside of it's size (default: True).
        """
        return self._crop

    def _set_crop(self, crop):
        if self._crop == crop:
            return
        self._crop = crop
        self._changed()


    def _get_parent(self):
        """
        The first parent :class:`View <spyral.View>` or 
        :class:`Scene <spyral.Scene>` that this View belongs to. Read-only.
        """
        return self._parent()
        
    def _get_scene(self):
        """
        The top-most parent :class:`Scene <spyral.Scene>` that this View
        belongs to. Read-only.
        """
        return self._scene()

    def _get_rect(self):
        """
        A :class:`Rect <spyral.Rect>` representing the position and size of
        this View. Can be set through a ``Rect``, a 2-tuple of position and
        size, or a 4-tuple.
        """
        return spyral.Rect(self._pos, self.size)

    def _set_rect(self, *rect):
        if len(rect) == 1:
            r = rect[0]
            self.x, self.y = r.x, r.y
            self.width, self.height = r.w, r.h
        elif len(rect) == 2:
            self.pos = rect[0]
            self.size = rect[1]
        elif len(args) == 4:
            self.x, self.y, self.width, self.height = args
        else:
            raise ValueError("TODO: You done goofed.")

    pos = property(_get_pos, _set_pos)
    layer = property(_get_layer, _set_layer)
    layers = property(_get_layers, _set_layers)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    anchor = property(_get_anchor, _set_anchor)
    scale = property(_get_scale, _set_scale)
    scale_x = property(_get_scale_x, _set_scale_x)
    scale_y = property(_get_scale_y, _set_scale_y)
    width = property(_get_width, _set_width)
    height = property(_get_height, _set_height)
    size = property(_get_size, _set_size)
    mask = property(_get_mask, _set_mask)
    output_width = property(_get_output_width, _set_output_width)
    output_height = property(_get_output_height, _set_output_height)
    output_size = property(_get_output_size, _set_output_size)
    crop_width = property(_get_crop_width, _set_crop_width)
    crop_height = property(_get_crop_height, _set_crop_height)
    crop_size = property(_get_crop_size, _set_crop_size)
    visible = property(_get_visible, _set_visible)
    crop = property(_get_crop, _set_crop)
    parent = property(_get_parent)
    scene = property(_get_scene)
    rect = property(_get_rect, _set_rect)

    def _blit(self, blit):
        """
        If this View is visible, applies offseting, scaling, and cropping
        before passing it up the transformation chain.
        """
        if self.visible:
            blit.position += self.pos
            blit.apply_scale(self.scale)
            if self.crop:
                blit.clip(spyral.Rect((0, 0), self.crop_size))
            self._parent()._blit(blit)

    def _static_blit(self, key, blit):
        """
        If this View is visible, applies offseting, scaling, and cropping
        before passing it up the transformation chain.
        """
        if self.visible:
            blit.position += self.pos
            blit.apply_scale(self.scale)
            if self.crop:
                blit.clip(spyral.Rect((0, 0), self.crop_size))
            self._parent()._static_blit(key, blit)

    def _warp_collision_box(self, box):
        """
        Transforms the given collision box according to this view's scaling,
        cropping, and offset; then passes the box to this boxes parent.
        """
        box.position += self.pos
        box.apply_scale(self.scale)
        if self.crop:
            box.clip(spyral.Rect((0, 0), self.crop_size))
        return self._parent()._warp_collision_box(box)

    def _set_collision_box(self):
        """
        Updates this View's collision box.
        """
        if self._mask is not None:
            pos = self._mask.topleft - self._offset
            area = spyral.Rect((0,0), self._mask.size)
        else:
            pos = self._pos - self._offset
            area = spyral.Rect((0,0), self.size)
        c = spyral.util._CollisionBox(pos, area)
        warped_box = self._parent()._warp_collision_box(c)
        self._scene()._set_collision_box(self, warped_box.rect)

    def __stylize__(self, properties):
        """
        Applies the *properties* to this scene. This is called when a style
        is applied.

        :param properties: a mapping of property names (strings) to values.
        :type properties: ``dict``
        """
        simple = ['pos', 'x', 'y', 'position',
                  'width', 'height', 'size',
                  'output_width', 'output_height', 'output_size',
                  'anchor', 'layer', 'layers', 'visible',
                  'scale', 'scale_x', 'scale_y',
                  'crop', 'crop_width', 'crop_height', 'crop_size']
        for property in simple:
            if property in properties:
                value = properties.pop(property)
                setattr(self, property, value)
        if len(properties) > 0:
            spyral.exceptions.unused_style_warning(self, properties.iterkeys())

    def collide_sprite(self, other):
        """
        Returns whether this view is colliding with the sprite or view.

        :param other: A sprite or a view
        :type other: :class:`Sprite <spyral.Sprite>` or a 
                     :class:`View <spyral.View>`
        :returns: A ``bool``
        """
        return self._scene().collide_sprite(self, other)
        
    def collide_point(self, pos):
        """
        Returns whether this view is colliding with the point.

        :param point: A point
        :type point: :class:`Vec2D <spyral.Vec2D>`
        :returns: A ``bool``
        """
        return self._scene().collide_point(self, pos)
        
    def collide_rect(self, rect):
        """
        Returns whether this view is colliding with the rect.

        :param rect: A rect
        :type rect: :class:`Rect <spyral.Rect>`
        :returns: A ``bool``
        """
        return self._scene().collide_rect(self, rect)
