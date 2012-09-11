import spyral
import pygame as pygame
from weakref import ref as _wref

_all_sprites = []

def _switch_scene():
    global _all_sprites
    _all_sprites = [s for s in _all_sprites if s() is not None and s()._expire_static()]

class Sprite(object):
    """
    Analagous to Sprite in pygame, but with many more features. For more
    detail, read the FAQ. Important member variables are:
    
    | *position*, *pos* - (x,y) coordinates for the sprite. Supports
      subpixel positioning and is kept in sync with *x* and *y*
    | *x* - x coordinate for the sprite
    | *y* - y coordinate for the sprite
    | *anchor* - position that the *x* and *y* coordinates are relative
      to on the image. Supports special values 'topleft', 'topright',
      'bottomleft', 'bottomright', 'center', 'midtop', 'midbottom',
      'midleft', 'midright', or a tuple of offsets which are treated
      as relative to the top left of the image.
    | *layer* - a string representing the layer to draw on. It should be a
      layer which exists on the camera that is used for the group(s) the
      sprite belongs to; if it is not, it will be drawn on top
    | *image* - a pygame.surface.Surface to be drawn to the screen. The surface
      must, for now, have certain flags set. Use spyral.util.new_surface and 
      spyral.util.load_image to get surfaces. One caveat is that once it is
      drawn to the camera, if the camera uses scaling, and the surface is
      changed, the display will not reflect this due to caching. If you must
      change a surface, copy it first. 
    | *blend_flags* - blend flags for pygame.surface.Surface.blit(). See the
      pygame documentation for more information.
    | *visible* - whether or not to draw this sprite
    | *width*, *height*, *size* - width, height, and size of the image
      respectively. Read-only.
    """

    def __init__(self, *groups):
        """ Adds this sprite to any number of groups by default. """
        _all_sprites.append(_wref(self))
        self._age = 0
        self._static = False
        self._image = None
        self._layer = '__default__'
        self._groups = []
        self.add(*groups)
        self._make_static = False
        self._pos = (0,0)
        self._blend_flags = 0
        self.visible = True
        self._anchor = 'topleft'
        self._offset = (0, 0)
        self._scale = 1.0
        self._scaled_image = None
    
    def _set_static(self):
        self._make_static = True
        self._static = True
    
    def _expire_static(self):
        # Expire static is part of the private API which must
        # be implemented by Sprites that wish to be static.
        if self._static:
            spyral.director.get_camera()._remove_static_blit(self)
        self._static = False
        self._age = 0
        return True
        
    def _recalculate_offset(self):
        w = self.width
        h = self.height
        a = self._anchor
        
        if a == 'topleft':
            offset = (0, 0)
        elif a == 'topright':
            offset = (w, 0)
        elif a == 'midtop':
            offset = (w/2., 0)
        elif a == 'bottomleft':
            offset = (0, h)
        elif a == 'bottomright':
            offset = (w, h)
        elif a == 'midbottom':
            offset = (w/2., h)
        elif a == 'midleft':
            offset = (0, h/2.)
        elif a == 'midright':
            offset = (w, h/2.)
        elif a == 'center':
            offset = (w/2., h/2.)
        else:
            offset = a
        self._offset = offset
        
    def _recalculate_scaled(self):
        if self._scale == 1.0:
            self._scaled_image = self._image
        else:
            new_size = (int(self._image.get_width() * self._scale), int(self._image.get_height() * self._scale))
            self._scaled_image = pygame.transform.smoothscale(self._image, new_size, spyral.util.new_surface(new_size))

    def _get_pos(self):
        return self._pos

    def _set_pos(self, pos):
        self._pos = pos
        self._age = 0
        if self._static:
            self._expire_static()
        

    def _get_layer(self):
        return self._layer
        
    def _set_layer(self, layer):
        self._layer = layer
        if self._static:
            self._expire_static()
        

    def _get_image(self):
        return self._image
        
    def _set_image(self, image):
        if self._image is image:
            return
        self._image = image
        self._recalculate_scaled()
        self._recalculate_offset()
        if self._static:
            self._expire_static()
            

    def _get_blend_flags(self):
        return self._blend_flags
    
    def _set_blend_flags(self, flags):
        if self._blend_flags == flags:
            return
        self._blend_flags = flags
        if self._static:
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
        if self._static:
            self._expire_static()
        
    def _get_width(self):
        if self.image:
            return self._image.get_width()
        return None
    
    def _get_height(self):
        if self.image:
            return self._image.get_height()
        return None
        
    def _get_size(self):
        if self.image:
            return self._image.get_size()
            
    def _get_scale(self):
        return self._scale
        
    def _set_scale(self, scale):
        if self._scale == scale:
            return
        self._scale = scale
        self._recalculate_scaled()
        if self._static:
            self._expire_static()
            
        
    
    position = property(_get_pos, _set_pos)
    pos = property(_get_pos, _set_pos)
    layer = property(_get_layer, _set_layer)
    image = property(_get_image, _set_image)
    blend_flags = property(_get_blend_flags, _set_blend_flags)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    anchor = property(_get_anchor, _set_anchor)
    scale = property(_get_scale, _set_scale)
    width = property(_get_width)
    height = property(_get_height)
    size = property(_get_size)
    
    def get_rect(self):
        return pygame.Rect((self._pos[0] - self._offset[0], self._pos[1] - self._offset[1]),
                           (self.width, self.height))
        
    def add(self, *groups):
        """ Add this sprite to any groups passed in. """
        self._expire_static()
        for g in groups:
            if g not in self._groups:
                self._groups.append(g)
                g.add(self)
                
    def kill(self):
        """ Remove this sprite from all groups. """
        self._expire_static()
        for g in self._groups:
            g.remove(self)
            
    def alive(self):
        """ Return True if this sprite belongs to any groups, false otherwise"""
        return len(self._groups) > 0
        
    def groups(self):
        """ Return a list of groups that this sprite belongs to. """
        return self._groups[:]
        
    def draw(self, camera):
        if not self.visible:
            return
        if self._static:
            return
        if self._make_static or self._age > 4:
            camera._static_blit(self,
                                self._scaled_image,
                                (self._pos[0] - self._offset[0],
                                 self._pos[1] - self._offset[1]),
                                self._layer,
                                self._blend_flags)
            self._make_static = False
            self._static = True
            return
        camera._blit(self._scaled_image,
                     (self._pos[0] - self._offset[0],
                      self._pos[1] - self._offset[1]),
                     self._layer,
                     self._blend_flags)
        self._age += 1
                                    
    def update(self, camera, *args):
        """ Called once per update tick. """
        pass
        
    def remove(self, *groups):
        """ Remove this sprite from any groups passed in. """
        self._expire_static()
        for g in groups:
            if g in self._groups:
                self._groups.remove(g)
                
    def __del__(self):
        spyral.director.get_camera()._remove_static_blit(self)

### Group classes ###
        
class Group(object):
    """ Behaves like sprite.Group in pygame. """
    
    def __init__(self, camera, *sprites):
        """
        Create a group and associate a camera with it. This is where all drawing
        will be sent.
        """
        self.camera = camera
        self._sprites = list(sprites)
        
    def draw(self):
        """ Draws all of its sprites to the group's camera. """
        c = self.camera
        for x in self._sprites:
            x.draw(c)
    
    def update(self, *args):
        """ Calls update on all of its Sprites. """ 
        [x.update(self.camera, *args) for x in self._sprites]
        
    def remove(self, *sprites):
        """ Removes Sprites from this Group. """
        for sprite in sprites:
            if sprite in self._sprites:
                self._sprites.remove(sprite)
                sprite.remove(self)
    
    def add(self, *sprites):
        """ Adds an object to its drawable list. """
        for sprite in sprites:
            if sprite not in self._sprites:
                self._sprites.append(sprite)
                sprite.add(self)
    
    def has(self, *sprites):
        """
        Return true if all sprites are contained in the group. Unlike
        pygame, this does not take an iterator for each argument, only sprites.
        """
        for sprite in sprites:
            if sprite not in self._sprites:
                return False
        return True
    
    def empty(self):
        """ Clears all sprites from the group. """
        for sprite in self._sprites:
            sprite.remove(self)
        self._sprites = []
        
    def sprites(self):
        """ Return a list of the sprites in this group. """
        return self._sprites[:]