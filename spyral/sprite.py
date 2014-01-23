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
    pos             The position of a sprite in 2D coordinates, represented as a :class:`Vec2D <spyral.Vec2D>`
    position        An alias for pos
    x               The x coordinate of the sprite, which will remain synced with the position`
    y               The y coordinate of the sprite, which will remain synced with the position`
    anchor          Defines an `anchor point <anchors>` where coordinates are relative to on the image.
    layer           The name of the layer this sprite belongs to. See `layering <spyral_layering>` for more.
    image           The image for this sprite
    visible         A boolean that represents whether this sprite should be drawn.
    width           Width of the image after all transforms.
    height          Height of the image after all transforms.
    size            (width, height) of the image after all transforms.
    scale           A scale factor for resizing the image. It will always contain a :class:`spyral.Vec2D` with an x factor and a y factor, but it can be set to a numeric value which will be set for both coordinates.
    scale_x         The x factor of the scaling. Kept in sync with scale
    scale_y         The y factor of the scaling. Kept in sync with scale
    flip_x          A boolean that determines whether the image should be flipped horizontally
    flip_y          A boolean that determines whether the image should be flipped vertically
    angle           An angle to rotate the image by. Rotation is computed after scaling and flipping, and keeps the center of the original image aligned with the center of the rotated image.
    parent          The parent of this sprite, either a View or a Scene. Read-only.
    scene           The scene that this sprite belongs to. Read-only.
    mask            A rect to use instead of the current image's rect for computing collisions. `None` if the image's rect should be used.
    ============    ============
    """

    def __stylize__(self, properties):
        if 'image' in properties:
            image = properties.pop('image') 
            if isinstance(image, str):
                image = spyral.Image(image)
            setattr(self, 'image', image)
        simple = ['pos', 'x', 'y', 'position', 'anchor', 'layer', 'visible',
                  'scale', 'scale_x', 'scale_y', 'flip_x', 'flip_y', 'angle']
        for property in simple:
            if property in properties:
                value = properties.pop(property)
                setattr(self, property, value)
        if len(properties) > 0:
            spyral.exceptions.unused_style_warning(self, properties.iterkeys())

    def __init__(self, view):
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
        self._view = view
        self._scene = view.scene
        self._angle = 0
        self._crop = None
        self._transform_image = None
        self._transform_offset = spyral.Vec2D(0, 0)
        self._flip_x = False
        self._flip_y = False
        self._animations = []
        self._progress = {}
        self._mask = None
        
        view.add_child(self)

        self._scene._register_sprite(self)
        self._scene.apply_style(self)
        self._scene.register('director.render', self.draw)

    def _set_static(self):
        self._make_static = True
        self._static = True

    def _expire_static(self):
        # Expire static is part of the private API which must
        # be implemented by Sprites that wish to be static.
        if self._static:
            self._scene._remove_static_blit(self)
        self._static = False
        self._age = 0
        self._set_collision_box()
        return True

    def _recalculate_offset(self):
        if self.image is None:
            return
        size = self._scale * self._image.get_size()

        offset = spyral.util.anchor_offset(self._anchor, size[0], size[1])

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
        self._computed_layer = self._scene._get_layer_position(self._view, layer)
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
            
    def _set_width(self, width):
        self._set_scale((width / self._get_width(), self._scale[1]))

    def _get_height(self):
        if self._transform_image:
            return self._transform_image.get_height()
            
    def _set_height(self, height):
        self._set_scale((self._scale[0], height / self._get_height()))

    def _get_size(self):
        if self._transform_image:
            return spyral.Vec2D(self._transform_image.get_size())
        return spyral.Vec2D(0, 0)
        
    def _set_size(self, size):
        self._set_scale((width / self._get_width(), height / self._get_height()))

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
        """
        Determines whether this Sprite will be drawn, either True or ``False``.
        """
        return self._visible
        
    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self._expire_static()
    
    def _get_scene(self):
        return self._scene
    def _get_view(self):
        return self._view

    #: Determines where this Sprite is drawn in the Scene (or View).
    position = property(_get_pos, _set_pos)
    #: Alias for position
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
    scene = property(_get_view)

    def get_rect(self):
        """
        Returns a :class:`rect <spyral.Rect>` representing where this
        sprite will be drawn.
        """
        return spyral.Rect(
            (self._pos[0] - self._offset[0], self._pos[1] - self._offset[1]),
            self.size)

    def draw(self):
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
            self._view._static_blit(self, b)
            return
        self._view._blit(b)
        self._age += 1
    
    def _set_collision_box(self):
        if self._mask is None:
            area = spyral.Rect(self._transform_image.get_rect())
        else:
            area = self._mask
        c = spyral.util._CollisionBox(self._pos - self._offset, area)
        warped_box = self._view._warp_collision_box(c)
        self._scene._set_collision_box(self, warped_box.rect)

    def kill(self):
        self._scene.unregister("director.render", self.draw)
        self._scene._unregister_sprite(self)
        self._scene._remove_static_blit(self)
        self._view.remove_child(self)

    def __del__(self):
        self._scene._remove_static_blit(self)
        
    def animate(self, animation):
        """
        Animates this sprite given an animation. Read more about :class:`animation <spyral.animation>`.
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

    def collide_sprite(self, other):
        return self.scene.collide_sprite(self, other)
    def collide_point(self, pos):
        return self.scene.collide_point(self, pos)
    def collide_rect(self, rect):
        return self.scene.collide_rect(self, rect)
        