import spyral
import pygame as pygame
from weakref import ref as _wref
import math

_all_sprites = []


def _switch_scene():
    global _all_sprites
    _all_sprites = [s for s in _all_sprites if s() is not None and s()
                    ._expire_static()]


class Sprite(object):
    """
    Sprites are how images are positioned and drawn onto the screen. 
    They aggregate information such as where to be drawn, layering
    information, and more together.
        
    Sprites have the following built-in attributes.
    
    ============    ============
    Attribute       Description
    ============    ============
    pos             The position of a sprite in 2D coordinates, represented as a :ref:`Vec2D <spyral_Vec2D>`
    x               The x coordinate of the sprite, which will remain synced with the :ref:`Vec2D <spyral_Vec2D>`
    y               The y coordinate of the sprite, which will remain synced with the :ref:`Vec2D <spyral_Vec2D>`
    position        An alias for pos
    anchor          Defines an :ref:`anchor point <anchors>` where coordinates are relative to on the image.
    layer           The name of the layer this sprite belongs to. See :ref:`layering <spyral_layering>` for more.
    image           The image for this sprite
    visible         A boolean that represents whether this sprite should be drawn.
    width           Width of the image after all transforms. Read-only
    height          Height of the image after all transforms. Read-only
    size            (width, height) of the image after all transforms. Read-only
    scale           A scale factor for resizing the image. It will always contain a :ref:`Vec2D <spyral_Vec2D>` with an x factor and a y factor, but it can be set to a numeric value which will be set for both coordinates.
    scale_x         The x factor of the scaling. Kept in sync with scale
    scale_y         The y factor of the scaling. Kept in sync with scale
    flip_x          A boolean that determines whether the image should be flipped horizontally
    flip_y          A boolean that determines whether the image should be flipped vertically
    angle           An angle to rotate the image by. Rotation is computed after scaling and flipping, and keeps the center of the original image aligned with the center of the rotated image.
    ============    ============
    """

    def __stylize__(self, properties):
        simple = ['scale', 'flip_x', 'flip_y', 'angle', 'visible', 'layer']
        for property, value in properties.iteritems():
            setattr(self, property, value)

    def __init__(self, scene):
        _all_sprites.append(_wref(self))
        self._age = 0
        self._static = False
        self._image = None
        self._image_version = None
        self._layer = '__default__'
        self._make_static = False
        self._pos = spyral.Vec2D(0, 0)
        self._blend_flags = 0
        self._visible = True
        self._anchor = 'topleft'
        self._offset = spyral.Vec2D(0, 0)
        self._scale = spyral.Vec2D(1.0, 1.0)
        self._scaled_image = None
        self._scene = scene
        self._camera = scene._camera
        self._angle = 0
        self._transform_image = None
        self._transform_offset = spyral.Vec2D(0, 0)
        self._flip_x = False
        self._flip_y = False
        self._animations = []
        self._progress = {}

        self._scene.apply_style(self)
        self._scene.register('director.render', self.draw)

    def _set_static(self):
        self._make_static = True
        self._static = True

    def _expire_static(self):
        # Expire static is part of the private API which must
        # be implemented by Sprites that wish to be static.
        if self._static:
            spyral.director._get_camera()._remove_static_blit(self)
        self._static = False
        self._age = 0
        return True

    def _recalculate_offset(self):
        if self.image is None:
            return
        size = self._scale * self._image.get_size()
        w = size[0]
        h = size[1]
        a = self._anchor

        if a == 'topleft':
            offset = (0, 0)
        elif a == 'topright':
            offset = (w, 0)
        elif a == 'midtop':
            offset = (w / 2., 0)
        elif a == 'bottomleft':
            offset = (0, h)
        elif a == 'bottomright':
            offset = (w, h)
        elif a == 'midbottom':
            offset = (w / 2., h)
        elif a == 'midleft':
            offset = (0, h / 2.)
        elif a == 'midright':
            offset = (w, h / 2.)
        elif a == 'center':
            offset = (w / 2., h / 2.)
        else:
            offset = a * spyral.Vec2D(-1, -1)
        self._offset = spyral.Vec2D(offset) - self._transform_offset
            
    def _recalculate_transforms(self):
        source = self._image._surf
        
        # flip
        if self._flip_x or self._flip_y:
            source = pygame.transform.flip(source, self._flip_x, self._flip_y)

        # scale
        if self._scale != (1.0, 1.0):
            new_size = self._scale * self._image.get_size()
            new_size = (int(new_size[0]), int(new_size[1]))
            if 0 in new_size:
                self._transform_image = pygame.Surface((1,1), pygame.SRCALPHA)
                self._recalculate_offset()
                self._expire_static()
                return
            source = pygame.transform.smoothscale(source, new_size, pygame.Surface(new_size, pygame.SRCALPHA))

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
        values = animation.evaluate(self, progress)
        for property in animation.properties:
            if property in values:
                setattr(self, property, values[property])
                
    def _run_animations(self, dt):
        completed = []
        for animation in self._animations:
            self._progress[animation] += dt
            progress = self._progress[animation]
            if progress > animation.duration:
                self._evaluate(animation, animation.duration)
                if animation.loop is True:
                    self._evaluate(animation, progress - animation.duration)
                    self._progress[animation] = progress - animation.duration
                elif animation.loop:
                    self._evaluate(animation, progress - animation.duration + animation.loop)
                    self._progress[animation] = progress - animation.duration + animation.loop
                else:
                    completed.append(animation)
            else:
                self._evaluate(animation, progress)

        for animation in completed:
            self.stop_animation(animation)


    # Getters and Setters
    def _get_pos(self):
        return self._pos

    def _set_pos(self, pos):
        if pos == self._pos:
            return
        self._pos = spyral.Vec2D(pos)
        self._expire_static()

    def _get_layer(self):
        return self._layer

    def _set_layer(self, layer):
        if layer == self._layer:
            return
        self._layer = layer
        self._expire_static()

    def _get_image(self):
        return self._image

    def _set_image(self, image):
        if self._image is image:
            return
        self._image = image
        self._image_version = image._version
        self._recalculate_transforms()
        self._expire_static()

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
        self._expire_static()

    def _get_width(self):
        if self._transform_image:
            return self._transform_image.get_width()

    def _get_height(self):
        if self._transform_image:
            return self._transform_image.get_height()

    def _get_size(self):
        if self._transform_image:
            return spyral.Vec2D(self._transform_image.get_size())
        return spyral.Vec2D(0, 0)

    def _get_scale(self):
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
        return self._scale[0]
        
    def _get_scale_y(self):
        return self._scale[1]
        
    def _set_scale_x(self, x):
        self._set_scale((x, self._scale[1]))

    def _set_scale_y(self, y):
        self._set_scale((self._scale[0], y))
        
    def _get_angle(self):
        return self._angle
        
    def _set_angle(self, angle):
        if self._angle == angle:
            return
        self._angle = angle
        self._recalculate_transforms()
        
    def _get_flip_x(self):
        return self._flip_x
    
    def _set_flip_x(self, flip_x):
        if self._flip_x == flip_x:
            return
        self._flip_x = flip_x
        self._recalculate_transforms()

    def _get_flip_y(self):
        return self._flip_y
    
    def _set_flip_y(self, flip_y):
        if self._flip_y == flip_y:
            return
        self._flip_y = flip_y
        self._recalculate_transforms()
        
    def _get_visible(self):
        return self._visible
        
    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self._expire_static()

    position = property(_get_pos, _set_pos)
    pos = property(_get_pos, _set_pos)
    layer = property(_get_layer, _set_layer)
    image = property(_get_image, _set_image)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    anchor = property(_get_anchor, _set_anchor)
    scale = property(_get_scale, _set_scale)
    scale_x = property(_get_scale_x, _set_scale_x)
    scale_y = property(_get_scale_y, _set_scale_y)
    width = property(_get_width)
    height = property(_get_height)
    size = property(_get_size)
    angle = property(_get_angle, _set_angle)
    flip_x = property(_get_flip_x, _set_flip_x)
    flip_y = property(_get_flip_y, _set_flip_y)
    visible = property(_get_visible, _set_visible)

    def get_rect(self):
        """
        Returns a :ref:`rect <spyral_Rect>` representing where this
        sprite will be drawn.
        """
        return spyral.Rect(
            (self._pos[0] - self._offset[0], self._pos[1] - self._offset[1]),
            self.size)

    def draw(self, offset = spyral.Vec2D(0, 0)):
        """
        This documentation is wrong now. Fix it later.

        Draws this sprite to the camera specified. Called automatically in
        the render loop. This should only be overridden in extreme
        circumstances.
        """
        if not self.visible:
            return
        if self._image is None:
            raise spyral.NoImageError("A sprite must have an image set before it can be drawn.")
        if self._image_version != self._image._version:
            self._image_version = self._image._version
            self._recalculate_transforms()
            self._expire_static()
        if self._static:
            return
        if self._make_static or self._age > 4:
            self._camera._static_blit(self,
                                    self._transform_image,
                                    (self._pos[0] - self._offset[0] + offset[0],
                                    self._pos[1] - self._offset[1] + offset[1]),
                                    self._layer,
                                    self._blend_flags)
            self._make_static = False
            self._static = True
            return
        self._camera._blit(self._transform_image,
                        (self._pos[0] - self._offset[0] + offset[0],
                        self._pos[1] - self._offset[1] + offset[1]),
                        self._layer,
                        self._blend_flags)
        self._age += 1

    def __del__(self):
        spyral.director._get_camera()._remove_static_blit(self)
        
    def animate(self, animation):
        """
        Animates this sprite given an animation. Read more about :ref:`animation <spyral_animation>`.
        """
        for a in self._animations:
            if a.properties.intersection(animation.properties):
                raise ValueError(
                    "Cannot animate on propety %s twice" % animation.property)
        if len(self._animations) == 0:
            self._scene.register('director.update',
                                 self._run_animations,
                                 ('dt', ))
        self._animations.append(animation)
        self._progress[animation] = 0
        self._evaluate(animation, 0.0)
        e = spyral.Event(animation=animation, sprite=self)
        spyral.event.handle("sprites.%s.animation.start", e)

    def stop_animation(self, animation):
        """
        Stops a given animation currently running on this sprite.
        """
        if animation in self._animations:
            self._animations.remove(animation)
            del self._progress[animation]
            if len(self._animations) == 0:
                self._scene.unregister('director.update', self._run_animations)
                e = spyral.Event(animation=animation, sprite=self)
                spyral.event.handle("sprites.%s.animation.end", e)


    def stop_all_animations(self):
        """
        Stops all animations currently running on this sprite.
        """
        for animation in self._animations:
            self.stop_animation(animation)

            
class AggregateSprite(Sprite):
    """
    An AggregateSprite is a sprite which also acts similarly to a
    group. Child sprites can be added to the group, and their drawing
    is offset by the position of the AggregateSprite. Their positioning
    can also be anchored with the attribute *child_anchor*, which will
    specify an :ref:`anchor point <anchors>` on the parent which the
    child sprites are relative to.
    
    Child sprites do not need to worry about being in a Group, the
    AggregateSprite will handle that for them.
    """
    def __init__(self, scene):
        Sprite.__init__(self, scene)
        self._internal_group = set()
        self._child_anchor = spyral.Vec2D(0, 0)
        
    def _get_child_anchor(self):
        return self._child_anchor
        
    def _set_child_anchor(self, anchor):
        for sprite in self._internal_group:
            sprite._expire_static()
        try:
            self._child_anchor = spyral.Vec2D(anchor)
        except Exception:
            self._child_anchor = anchor
            
    child_anchor = property(_get_child_anchor, _set_child_anchor)
        
    def add_child(self, sprite):
        """
        Adds a child to this AggregateSprite.
        """
        self._internal_group.add(sprite)
        self._scene.unregister("director.render", sprite.draw)
        
    def remove_child(self, sprite):
        """
        Remove a child from this AggregateSprite.
        """
        self._internal_group.remove(sprite)
        
    def get_children(self):
        """
        Return a list of the children sprites
        """
        return self._internal_group
                
    def get_rect(self):
        """
        Return a rect which is the union of all the child rects.
        """
        # This may potentially be a performance trap
        # Down the line we may have to mess with getting cached
        # versions of rects if we know the children haven't changed
        sprites = self._internal_group 
        r = Sprite.get_rect(self)
        try:
            i_offset = getattr(Sprite.get_rect(self), self._child_anchor)
        except (AttributeError, TypeError):
            i_offset = self.pos
        for s in sprites:
            r = r.union(s.get_rect().move(*i_offset))
        return r       
    
    def draw(self, offset = spyral.Vec2D(0,0)):
        """
        Draws this sprite and all children to the camera. Should be
        overridden only in extreme circumstances.
        """
        if self._age == 0:
            for sprite in self._internal_group:
                sprite._expire_static()
        if self.image is not None:
            Sprite.draw(self, offset)
        if not self.visible:
            return
        try:
            i_offset = getattr(Sprite.get_rect(self), self._child_anchor)
        except (TypeError, AttributeError):
            i_offset = self.pos - self._offset
        
        for sprite in self._internal_group:
            sprite.draw(offset + i_offset)
            
class ViewPort(Sprite):
    """
    """
    pass
    