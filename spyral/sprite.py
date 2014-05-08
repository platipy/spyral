import spyral
import pygame
from weakref import ref as _wref
import math


_all_sprites = []

def _switch_scene():
    """
    Ensure that dead sprites are removed from the list and that sprites are
    redrawn on a scene change.
    """
    global _all_sprites
    _all_sprites = [s for s in _all_sprites
                      if s() is not None and s()._expire_static()]


class Sprite(object):
    """
    Sprites are how images are positioned and drawn onto the screen.
    They aggregate together information such as where to be drawn,
    layering information, and more.

    :param parent: The parent that this Sprite will belong to.
    :type parent: :class:`View <spyral.View>` or :class:`Scene <spyral.Scene>`
    """

    def __stylize__(self, properties):
        """
        The __stylize__ function is called during initialization to set up
        properties taken from a style function. Sprites that want to override
        default styling behavior should implement this class, although that
        should rarely be necessary.
        """
        if 'image' in properties:
            image = properties.pop('image')
            if isinstance(image, str):
                image = spyral.Image(image)
            setattr(self, 'image', image)
        simple = ['pos', 'x', 'y', 'position', 'anchor', 'layer', 'visible',
                  'scale', 'scale_x', 'scale_y', 'flip_x', 'flip_y', 'angle',
                  'mask']
        for property in simple:
            if property in properties:
                value = properties.pop(property)
                setattr(self, property, value)
        if len(properties) > 0:
            spyral.exceptions.unused_style_warning(self, properties.iterkeys())

    def __init__(self, parent):
        _all_sprites.append(_wref(self))
        self._age = 0
        self._static = False
        self._image = None
        self._image_version = None
        self._layer = None
        self._computed_layer = 1
        self._make_static = False
        self._pos = spyral.Vec2D(0, 0)
        self._blend_flags = 0
        self._visible = True
        self._anchor = 'topleft'
        self._offset = spyral.Vec2D(0, 0)
        self._scale = spyral.Vec2D(1.0, 1.0)
        self._scaled_image = None
        self._parent = _wref(parent)
        self._scene = _wref(parent.scene)
        self._angle = 0
        self._crop = None
        self._transform_image = None
        self._transform_offset = spyral.Vec2D(0, 0)
        self._flip_x = False
        self._flip_y = False
        self._animations = []
        self._progress = {}
        self._mask = None

        parent._add_child(self)

        self._scene()._register_sprite(self)
        self._scene()._apply_style(self)
        spyral.event.register('director.render', self._draw,
                              scene=self._scene())

    def _set_static(self):
        """
        Forces this class to be static, indicating that it will not be redrawn
        every frame.
        """
        self._make_static = True
        self._static = True

    def _expire_static(self):
        """
        Force this class to no longer be static; it will be redrawn for a few
        frames, until it has sufficiently aged. This also triggers the collision
        box to be recomputed.
        """
        # Expire static is part of the private API which must
        # be implemented by Sprites that wish to be static.
        if self._static:
            self._scene()._remove_static_blit(self)
        self._static = False
        self._age = 0
        self._set_collision_box()
        return True

    def _recalculate_offset(self):
        """
        Recalculates this sprite's offset based on its position, transform
        offset, anchor, its image, and the image's scaling.
        """
        if self.image is None:
            return
        size = self._scale * self._image.size

        offset = spyral.util._anchor_offset(self._anchor, size[0], size[1])

        self._offset = spyral.Vec2D(offset) - self._transform_offset

    def _recalculate_transforms(self):
        """
        Calculates the transforms that need to be applied to this sprite's
        image. In order: flipping, scaling, and rotation.
        """
        source = self._image._surf

        # flip
        if self._flip_x or self._flip_y:
            source = pygame.transform.flip(source, self._flip_x, self._flip_y)

        # scale
        if self._scale != (1.0, 1.0):
            new_size = self._scale * self._image.size
            new_size = (int(new_size[0]), int(new_size[1]))
            if 0 in new_size:
                self._transform_image = spyral.image._new_spyral_surface((1,1))
                self._recalculate_offset()
                self._expire_static()
                return
            new_surf = spyral.image._new_spyral_surface(new_size)
            source = pygame.transform.smoothscale(source, new_size, new_surf)

        # rotate
        if self._angle != 0:
            angle = 180.0 / math.pi * self._angle % 360
            old = spyral.Vec2D(source.get_rect().center)
            source = pygame.transform.rotate(source, angle).convert_alpha()
            new = source.get_rect().center
            self._transform_offset = old - new

        self._transform_image = source
        self._recalculate_offset()
        self._expire_static()

    def _evaluate(self, animation, progress):
        """
        Performs a step of the given animation, setting any properties that will
        change as a result of the animation (e.g., x position).
        """        
        values = animation.evaluate(self, progress)
        for property in animation.properties:
            if property in values:
                setattr(self, property, values[property])

    def _run_animations(self, delta):
        """
        For a given time-step (delta), perform a step of all the animations
        associated with this sprite.
        """
        completed = []
        for animation in self._animations:
            self._progress[animation] += delta
            progress = self._progress[animation]
            if progress > animation.duration:
                self._evaluate(animation, animation.duration)
                if animation.loop is True:
                    self._evaluate(animation, progress - animation.duration)
                    self._progress[animation] = progress - animation.duration
                elif animation.loop:
                    current = progress - animation.duration + animation.loop
                    self._evaluate(animation, current)
                    self._progress[animation] = current
                else:
                    completed.append(animation)
            else:
                self._evaluate(animation, progress)

        for animation in completed:
            self.stop_animation(animation)


    # Getters and Setters
    def _get_rect(self):
        """
        Returns a :class:`Rect <spyral.Rect>` representing the position and size
        of this Sprite's image. Note that if you change a property of this rect
        that it will not actually update this sprite's properties:
        
        >>> my_sprite.rect.top = 10
        
        Does not adjust the y coordinate of `my_sprite`. Changing the rect will
        adjust the sprite however
        
        >>> my_sprite.rect = spyral.Rect(10, 10, 64, 64)
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

    def _get_pos(self):
        """
        The position of a sprite in 2D coordinates, represented as a
        :class:`Vec2D <spyral.Vec2D>`
        """
        return self._pos

    def _set_pos(self, pos):
        if pos == self._pos:
            return
        self._pos = spyral.Vec2D(pos)
        self._expire_static()

    def _get_layer(self):
        """
        String. The name of the layer this sprite belongs to. See
        :ref:`layering <ref.layering>` for more.
        """
        return self._layer

    def _set_layer(self, layer):
        if layer == self._layer:
            return
        self._layer = layer
        self._computed_layer = self._scene()._get_layer_position(self._parent(),
                                                                 layer)
        self._expire_static()

    def _get_image(self):
        """
        The :class:`Image <spyral.Image>` for this sprite.
        """
        return self._image

    def _set_image(self, image):
        if self._image is image:
            return
        self._image = image
        self._image_version = image._version
        self._recalculate_transforms()
        self._expire_static()

    def _get_x(self):
        """
        The x coordinate of the sprite, which will remain synced with the
        position. Number.
        """
        return self._get_pos()[0]

    def _set_x(self, x):
        self._set_pos((x, self._get_y()))

    def _get_y(self):
        """
        The y coordinate of the sprite, which will remain synced with the
        position. Number
        """
        return self._get_pos()[1]

    def _set_y(self, y):
        self._set_pos((self._get_x(), y))

    def _get_anchor(self):
        """
        Defines an :ref:`anchor point <ref.anchors>` where coordinates are relative to
        on the image. String.
        """
        return self._anchor

    def _set_anchor(self, anchor):
        if anchor == self._anchor:
            return
        self._anchor = anchor
        self._recalculate_offset()
        self._expire_static()

    def _get_width(self):
        """
        The width of the image after all transforms. Number.
        """
        if self._transform_image:
            return self._transform_image.get_width()

    def _set_width(self, width):
        self._set_scale((width / self._get_width(), self._scale[1]))

    def _get_height(self):
        """
        The height of the image after all transforms. Number.
        """
        if self._transform_image:
            return self._transform_image.get_height()

    def _set_height(self, height):
        self._set_scale((self._scale[0], height / self._get_height()))

    def _get_size(self):
        """
        The size of the image after all transforms (:class:`Vec2D <spyral.Vec2D>`).
        """
        if self._transform_image:
            return spyral.Vec2D(self._transform_image.get_size())
        return spyral.Vec2D(0, 0)

    def _set_size(self, size):
        self._set_scale((width / self._get_width(),
                         height / self._get_height()))

    def _get_scale(self):
        """
        A scale factor for resizing the image. When read, it will always contain
        a :class:`spyral.Vec2D` with an x factor and a y factor, but it can be
        set to a numeric value which wil ensure identical scaling along both
        axes.
        """
        return self._scale

    def _set_scale(self, scale):
        if isinstance(scale, (int, float)):
            scale = spyral.Vec2D(scale, scale)
        if self._scale == scale:
            return
        self._scale = spyral.Vec2D(scale)
        self._recalculate_transforms()
        self._expire_static()

    def _get_scale_x(self):
        """
        The x factor of the scaling that's kept in sync with scale. Number.
        """
        return self._scale[0]

    def _set_scale_x(self, x):
        self._set_scale((x, self._scale[1]))

    def _get_scale_y(self):
        """
        The y factor of the scaling that's kept in sync with scale. Number.
        """
        return self._scale[1]

    def _set_scale_y(self, y):
        self._set_scale((self._scale[0], y))

    def _get_angle(self):
        """
        An angle to rotate the image by. Rotation is computed after scaling and
        flipping, and keeps the center of the original image aligned with the
        center of the rotated image.
        """
        return self._angle

    def _set_angle(self, angle):
        if self._angle == angle:
            return
        self._angle = angle
        self._recalculate_transforms()

    def _get_flip_x(self):
        """
        A boolean that determines whether the image should be flipped
        horizontally.
        """
        return self._flip_x

    def _set_flip_x(self, flip_x):
        if self._flip_x == flip_x:
            return
        self._flip_x = flip_x
        self._recalculate_transforms()

    def _get_flip_y(self):
        """
        A boolean that determines whether the image should be flipped
        vertically.
        """
        return self._flip_y

    def _set_flip_y(self, flip_y):
        if self._flip_y == flip_y:
            return
        self._flip_y = flip_y
        self._recalculate_transforms()

    def _get_visible(self):
        """
        A boolean indicating whether this sprite should be drawn.
        """
        return self._visible

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self._expire_static()

    def _get_scene(self):
        """
        The top-level scene that this sprite belongs to. Read-only.
        """
        return self._scene()

    def _get_parent(self):
        """
        The parent of this sprite, either a :class:`View <spyral.View>` or a
        :class:`Scene <spyral.Scene>`. Read-only.
        """
        return self._parent()

    def _get_mask(self):
        """
        A :class:`Rect <spyral.Rect>` to use instead of the current image's rect
        for computing collisions. `None` if the image's rect should be used.
        """
        return self._mask

    def _set_mask(self, mask):
        self._mask = mask
        self._set_collision_box()

    pos = property(_get_pos, _set_pos)
    layer = property(_get_layer, _set_layer)
    image = property(_get_image, _set_image)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    anchor = property(_get_anchor, _set_anchor)
    scale = property(_get_scale, _set_scale)
    scale_x = property(_get_scale_x, _set_scale_x)
    scale_y = property(_get_scale_y, _set_scale_y)
    width = property(_get_width, _set_width)
    height = property(_get_height, _set_height)
    size = property(_get_size, _set_size)
    angle = property(_get_angle, _set_angle)
    flip_x = property(_get_flip_x, _set_flip_x)
    flip_y = property(_get_flip_y, _set_flip_y)
    visible = property(_get_visible, _set_visible)
    rect = property(_get_rect, _set_rect)
    scene = property(_get_scene)
    parent = property(_get_parent)
    mask = property(_get_mask, _set_mask)

    def _draw(self):
        """
        Internal method for generating this sprite's blit, unless it is
        invisible or currently static. If it has aged sufficiently or is being
        forced, it will become static; otherwise, it ages one step.
        """
        if not self.visible:
            return
        if self._image is None:
            raise spyral.NoImageError("A sprite must have an image"
                                      " set before it can be drawn.")
        if self._image_version != self._image._version:
            self._image_version = self._image._version
            self._recalculate_transforms()
            self._expire_static()
        if self._static:
            return

        area = spyral.Rect(self._transform_image.get_rect())
        b = spyral.util._Blit(self._transform_image,
                              self._pos - self._offset,
                              area,
                              self._computed_layer,
                              self._blend_flags,
                              False)

        if self._make_static or self._age > 4:
            b.static = True
            self._make_static = False
            self._static = True
            self._parent()._static_blit(self, b)
            return
        self._parent()._blit(b)
        self._age += 1

    def _set_collision_box(self):
        """
        Updates this sprite's collision box.
        """
        if self.image is None:
            return
        if self._mask is None:
            area = spyral.Rect(self._transform_image.get_rect())
        else:
            area = self._mask
        c = spyral.util._CollisionBox(self._pos - self._offset, area)
        warped_box = self._parent()._warp_collision_box(c)
        self._scene()._set_collision_box(self, warped_box.rect)

    def kill(self):
        """
        When you no longer need a Sprite, you can call this method to have it
        removed from the Scene. This will not remove the sprite entirely from
        memory if there are other references to it; if you need to do that,
        remember to ``del`` the reference to it.
        """
        self._scene()._unregister_sprite(self)
        self._scene()._remove_static_blit(self)
        self._parent()._remove_child(self)

    def animate(self, animation):
        """
        Animates this sprite given an animation. Read more about
        :class:`animation <spyral.animation>`.

        :param animation: The animation to run.
        :type animation: :class:`Animation <spyral.Animation>`
        """
        for a in self._animations:
            repeats = a.properties.intersection(animation.properties)
            if repeats:
                # Loop over all repeats
                raise ValueError("Cannot animate on propies %s twice" %
                                 (str(repeats),))
        if len(self._animations) == 0:
            spyral.event.register('director.update',
                                  self._run_animations,
                                  ('delta', ),
                                  scene=self._scene())
        self._animations.append(animation)
        self._progress[animation] = 0
        self._evaluate(animation, 0.0)
        e = spyral.Event(animation=animation, sprite=self)
        # Loop over all possible properties
        for property in animation.properties:
            spyral.event.handle("%s.%s.animation.start" % (self.__class__.__name__,
                                                           property),
                                e)

    def stop_animation(self, animation):
        """
        Stops a given animation currently running on this sprite.

        :param animation: The animation to stop.
        :type animation: :class:`Animation <spyral.Animation>`
        """
        if animation in self._animations:
            self._animations.remove(animation)
            del self._progress[animation]
            e = spyral.Event(animation=animation, sprite=self)
            for property in animation.properties:
                spyral.event.handle("%s.%s.animation.end" % (self.__class__.__name__,
                                                            property),
                                    e)
            if len(self._animations) == 0:
                spyral.event.unregister('director.update',
                                        self._run_animations,
                                        scene=self._scene())


    def stop_all_animations(self):
        """
        Stops all animations currently running on this sprite.
        """
        for animation in self._animations:
            self.stop_animation(animation)

    def collide_sprite(self, other):
        """
        Returns whether this sprite is currently colliding with the other
        sprite. This collision will be computed correctly regarding the sprites
        offsetting and scaling within their views.

        :param other: The other sprite
        :type other: :class:`Sprite <spyral.Sprite>`
        :returns: ``bool`` indicating whether this sprite is colliding with the
                  other sprite.
        """
        return self._scene().collide_sprites(self, other)

    def collide_point(self, point):
        """
        Returns whether this sprite is currently colliding with the position.
        This uses the appropriate offsetting for the sprite within its views.

        :param point: The point (relative to the window dimensions).
        :type point: :class:`Vec2D <spyral.Vec2D>`
        :returns: ``bool`` indicating whether this sprite is colliding with the
                  position.
        """
        return self._scene().collide_point(self, point)

    def collide_rect(self, rect):
        """
        Returns whether this sprite is currently colliding with the rect. This
        uses the appropriate offsetting for the sprite within its views.

        :param rect: The rect (relative to the window dimensions).
        :type rect: :class:`Rect <spyral.Rect>`
        :returns: ``bool`` indicating whether this sprite is colliding with the
                  rect.
        """
        return self._scene().collide_rect(self, rect)
        