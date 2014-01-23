import spyral

class View(object):
    def __init__(self, parent):
        """
        Creates a new view with a scene or view as a parent.

        Views have the following built-in attributes
    
        ============    ============
        Attribute       Description
        ============    ============
        pos             The position of a sprite in 2D coordinates, represented as a :class:`Vec2D <spyral.Vec2D>`. (Default: (0, 0))
        position        An alias for pos
        x               The x coordinate of the sprite, which will remain synced with the position`
        y               The y coordinate of the sprite, which will remain synced with the position`
        size            The (width, height) of this view's coordinate space (:class:`Vec2D <spyral.Vec2d>`). (Default: size of the parent)
        width           The width of the view.
        height          The height of the view
        output_size     The (width, height) of this view when drawn on the parent (:class:`Vec2D <spyral.Vec2d>`). (Default: size of the parent)
        output_width    The width of this view when drawn on the parent.
        output_height   The height of this view when drawn on the parent.
        scale           A scale factor from the size to the output_size for the view. It will always contain a :class:`spyral.Vec2D` with an x factor and a y factor, but it can be set to a numeric value which will be set for both coordinates.
        scale_x         The x factor of the scaling. Kept in sync with scale
        scale_y         The y factor of the scaling. Kept in sync with scale
        anchor          Defines an `anchor point <anchors>` where coordinates are relative to in the view.
        layer           The name of the layer this view belongs to in it's parent. See `layering <spyral_layering>` for more.
        layers          A list of layers that the children of this view can be in. See `layering <spyral_layering>` for more.
        visible         A boolean that represents whether this view should be drawn (default: True).
        crop            A boolean that determines whether the view should crop anything outside of it's size (default: True)
        crop_size       The (width, height) of the area that will be cropped; anything outside of this region will be removed
        crop_width      The width of the cropped area
        crop_height     The height of the cropped area
        parent          The first parent View or Scene that this View belongs to. Read-only.
        scene           The Scene that this View belongs to. Read-only.
        mask            A rect to use instead of the current image's rect for computing collisions. `None` if the view's rect should be used.
        ============    ============
        """

        self._size = spyral.Vec2D(parent.size)
        self._output_size = spyral.Vec2D(parent.size)
        self._crop_size = spyral.Vec2D(parent.size)
        self._pos = spyral.Vec2D(0,0)
        self._crop = False
        self._visible = True
        self._parent = parent
        self._anchor = 'topleft'
        self._offset = spyral.Vec2D(0,0)
        self._layers = []
        self._layer = None
        self._mask = None

        self._children = set()
        self._child_views = set()
        self._scene = scene = parent.scene
        self.scene._add_view(self)
        self._parent.add_child(self)
        scene.apply_style(self)
        
    def add_child(self, entity):
        self._children.add(entity)
        if isinstance(entity, View):
            self._child_views.add(entity)
        
    def remove_child(self, entity):
        self._children.discard(entity)
        self._child_views.discard(entity)
        
    def kill(self):
        for child in list(self._children):
            child.kill()
        self._children.clear()
        self._child_views.clear()
        self.scene._kill_view(self)
        self._parent = None
        
    def _get_mask(self):
        return self._mask
        
    def _set_mask(self, mask):
        self._mask = mask
        self._set_collision_box()
    
    def _set_collision_box_tree(self):
        self._set_collision_box()
        for view in self._child_views:
            view._set_collision_box_tree()

    def _changed(self):
        self._recalculate_offset()
        self._set_collision_box_tree()
        # Notify any listeners (probably children) that I have changed
        e = spyral.Event(name="changed", view=self)
        spyral.event.handle("spyral.internal.view.changed.%s" %
                                spyral.event.get_identifier(self), e)

    def _recalculate_offset(self):
        self._offset = spyral.util.anchor_offset(self._anchor, self._size[0], self._size[1])

    # Properties
    def _get_pos(self):
        return self._pos

    def _set_pos(self, pos):
        if pos == self._pos:
            return
        self._pos = spyral.Vec2D(pos)
        self._changed()

    def _get_layer(self):
        return self._layer

    def _set_layer(self, layer):
        if layer == self._layer:
            return
        self._layer = layer
        self.scene._set_view_layer(self, layer)
        #self._computed_layer = self._view._compute_layer(layer)
        self._changed()
        
    def _compute_layer(self, layer):
        """
        Computes the numerical index of `layer` (in reference to the other layers).
        """
        return spyral.util.compute_layer(self._layers, layer)

    def _get_layers(self):
        return tuple(self._layers)

    def _set_layers(self, layers):
        if not self._layers:
            self._layers = layers[:]
            self.scene._set_view_layers(self, layers)
        elif self._layers == layers:
            pass
        else:
            raise spyral.LayersAlreadySetError("You can only define the layers for a view once.")

    def _get_x(self):
        return self._get_pos()[0]

    def _set_x(self, x):
        self._set_pos((x, self._get_y()))

    def _get_y(self):
        return self._get_pos()[1]

    def _set_y(self, y):
        self._set_pos((self._get_x(), y))

    def _get_anchor(self):
        return self._anchor

    def _set_anchor(self, anchor):
        if anchor == self._anchor:
            return
        self._anchor = anchor
        self._recalculate_offset()
        self._changed()

    def _get_width(self):
        return self._size[0]
            
    def _set_width(self, width):
        self._set_size(width, self._get_height())

    def _get_height(self):
        return self._size[1]
            
    def _set_height(self, height):
        self._set_size(self._get_width(), height)

    def _get_output_width(self):
        return self._output_size[0]
            
    def _set_output_width(self, width):
        self._set_output_size((width, self._get_output_height()))

    def _get_output_height(self):
        return self._output_size[1]
            
    def _set_output_height(self, height):
        self._set_output_size((self._get_output_width(), height))
        
    def _get_crop_width(self):
        return self._crop_size[0]
            
    def _set_crop_width(self, width):
        self._set_crop_size((width, self._get_crop_height()))

    def _get_crop_height(self):
        return self._crop_size[1]
            
    def _set_crop_height(self, height):
        self._set_crop_size((self._get_crop_width(), height))

    def _get_size(self):
        return self._size
        
    def _set_size(self, size):
        if size == self._size:
            return
        self._size = spyral.Vec2D(size)
        self._changed()

    def _get_output_size(self):
        return self._output_size
        
    def _set_output_size(self, size):
        if size == self._output_size:
            return
        self._output_size = spyral.Vec2D(size)
        self._changed()
        
    def _get_crop_size(self):
        return self._crop_size
        
    def _set_crop_size(self, size):
        if size == self._crop_size:
            return
        self._crop_size = spyral.Vec2D(size)
        self._changed()

    def _get_scale(self):
        return self._output_size / self._size

    def _set_scale(self, scale):
        if isinstance(scale, (int, float)):
            scale = spyral.Vec2D(scale, scale)
        if scale == self._get_scale():
            return
        self._output_size = self._size * spyral.Vec2D(scale)
        self._changed()
            
    def _get_scale_x(self):
        return self._get_scale()[0]
        
    def _get_scale_y(self):
        return self._get_scale()[1]
        
    def _set_scale_x(self, x):
        self._set_scale((x, self._get_scale()[1]))

    def _set_scale_y(self, y):
        self._set_scale((self._get_scale()[0], y))
                
    def _get_visible(self):
        return self._visible
        
    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self._changed()

    def _get_crop(self):
        return self._crop

    def _set_crop(self, crop):
        if self._crop == crop:
            return
        self._crop = crop
        self._changed()
        
    
    def _get_parent(self):
        return self._parent
    def _get_scene(self):
        return self._scene
        
    def _get_rect(self):
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

    position = property(_get_pos, _set_pos)
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
        if self.visible:
            blit.position += self.position
            blit.apply_scale(self.scale)
            if self.crop:
                blit.clip(spyral.Rect((0, 0), self.crop_size))
            self._parent._blit(blit)
        
    def _static_blit(self, key, blit):
        if self.visible:
            blit.position += self.position
            blit.apply_scale(self.scale)
            if self.crop:
                blit.clip(spyral.Rect((0, 0), self.crop_size))
            self._parent._static_blit(key, blit)
    
    def _warp_collision_box(self, box):
        box.position += self.position
        box.apply_scale(self.scale)
        if self.crop:
            box.clip(spyral.Rect((0, 0), self.crop_size))
        return self._parent._warp_collision_box(box)
    
    def _set_collision_box(self):
        if self._mask is not None:
            pos = self._mask.topleft
            area = spyral.Rect((0,0), self._mask.size)
        else:
            pos = self._pos - self._offset
            area = spyral.Rect((0,0), self.size)
        c = spyral.util._CollisionBox(pos, area)
        warped_box = self._parent._warp_collision_box(c)
        self._scene._set_collision_box(self, warped_box.rect)
            
    def __stylize__(self, properties):
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
        return self.scene.collide_sprite(self, other)
    def collide_point(self, pos):
        return self.scene.collide_point(self, pos)
    def collide_rect(self, rect):
        return self.scene.collide_rect(self, rect)
