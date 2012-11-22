from __future__ import division
import spyral
import pygame
import math
import operator
import sys

class _Blit(object):
    __slots__ = ['surface', 'rect', 'layer', 'flags', 'static']
    def __init__(self, surface, rect, layer, flags, static):
        self.surface = surface
        self.rect = rect
        self.layer = layer
        self.flags = flags
        self.static = static
        

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


class Camera(object):
    """
    Represents an area to draw to. It can handle automatic scaling with
    optional offsets and optional layering.
    
    Cameras should never be instantiated directly. Instead, you should
    call `make_camera` on the camera passed into your scene.
    """
    def __init__(self, virtual_size=None,
                 real_size=None,
                 offset=(0, 0),
                 layers = None,
                 root = False):
        if root:
            self._surface = pygame.display.get_surface()
            if real_size is None or real_size == (0, 0):
                self._rsize = self._surface.get_size()
            else:
                self._rsize = real_size
        elif real_size is None:
            raise ValueError("Must specify a real_size.")
        else:
            self._rsize = real_size

        if virtual_size is None or virtual_size == (0, 0):
            self._vsize = self._rsize
            self._scale = (1.0, 1.0)
        else:
            self._vsize = virtual_size
            self._scale = (self._rsize[0] / self._vsize[0],
                           self._rsize[1] / self._vsize[1])
        self._background = None
        self._root = root
        self._offset = offset
        if layers is None:
            layers = ['all']
        self._layers = layers

        if self._root:
            self._background = pygame.surface.Surface(self._rsize)
            self._background.fill((255, 255, 255))
            self._surface.blit(self._background, (0, 0))
            self._blits = []
            self._dirty_rects = []
            self._clear_this_frame = []
            self._clear_next_frame = []
            self._soft_clear = []
            self._static_blits = {}
            self._rs = self
            self._rect = self._surface.get_rect()
            self._saved_blits = {}
            self._backgrounds = {}

    def make_child(self, virtual_size=None,
                   real_size=None,
                   offset=(0, 0),
                   layers = ['all']):
        """
        Method for creating a new Camera.

        | *virtual_size* is a size of the virtual resolution to be used.
        | *real_size* is a size of the resolution with respect to the parent
          camera (not to the physical display, unless the parent camera is the
          root one). This allows multi-level nesting of cameras, if needed.
        | *offset* is a position offset of where this camera should be in the
          parent camera's coordinates.
        | *layers* is a list of layers which should be drawn bottom to top.
        """
        if real_size == (0, 0) or real_size is None:
            real_size = self.get_size()
        y = spyral.camera.Camera(virtual_size, real_size, offset, layers, 0)
        y._parent = self
        offset = spyral.Vec2D(offset) * self._scale
        y._offset = offset + self._offset
        y._scale = spyral.Vec2D(self._scale) * y._scale
        y._rect = pygame.Rect(y._offset,
                              spyral.point.scale(real_size, self._scale))
        y._rs = self._rs
        return y

    def get_size(self):
        """
        Returns the virtual size of this camera's display.
        """
        return self._vsize

    def get_rect(self):
        """
        Returns a rect the virtual size of this camera's display
        """
        return spyral.Rect((0, 0), self._vsize)

    def set_background(self, image):
        """
        Sets a background for this camera's display.
        """
        surface = image._surf
        # This is CPython specific, but right now so is Pygame.
        if sys._getframe(1).f_code.co_name == "__init__":
            raise RuntimeError("Background initialization must be done in a scene's on_enter, not __init__")
        if surface.get_size() != self._vsize:
            raise ValueError("Background size must match the display size.")
        if not self._root:
            self._rs._background.blit(_scale(surface, self._scale),
                                      self._offset)
            self._rs._clear_this_frame.append(self._rs._background.get_rect())
        else:
            raise ValueError(
                "You cannot set the background on the root camera directly.")
            self._background = surface
            self._clear_this_frame.append(surface.get_rect())
            
    def _compute_layer(self, layer):
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

    def _blit(self, surface, position, layer, flags):
        position = spyral.point.scale(position, self._scale)
        position = (position[0] + self._offset[0],
                    position[1] + self._offset[1])
        layer = self._compute_layer(layer)
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

        self._rs._blits.append(_Blit(new_surface,
                                     r,
                                     layer,
                                     flags,
                                     False))

    def _static_blit(self, sprite, surface, position, layer, flags):
        position = spyral.point.scale(position, self._scale)
        position = (position[0] + self._offset[0],
                    position[1] + self._offset[1])
        layer = self._compute_layer(layer)
        rs = self._rs
        redraw = sprite in rs._static_blits
        if redraw:
            r2 = rs._static_blits[sprite][1]
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

        rs._static_blits[sprite] = _Blit(new_surface,
                                          r,
                                          layer,
                                          flags,
                                          True)
        if redraw:
            rs._clear_this_frame.append(r2.union(r))
        else:
            rs._clear_this_frame.append(r)

    def _remove_static_blit(self, sprite):
        if not self._root:
            self._rs._remove_static_blit(sprite)
            return
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
        if not self._root:
            return
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
        v = pygame.version.vernum
        
        for blit in blits:
            # If a blit is entirely off screen, we can ignore it altogether
            if not screen_rect.contains(blit.rect) and not screen_rect.colliderect(blit.rect):
                continue
            if blit.static:
                skip_soft_clear = False
                for rect in clear_this:
                    if blit.rect.colliderect(rect):
                        if v < (1, 8):
                            screen.blit(blit.surface, blit.rect)
                        else:
                            screen.blit(blit.surface, blit.rect, None, blit.flags)
                        skip_soft_clear = True
                        clear_this.append(blit.rect)
                        self._soft_clear.append(blit.rect)
                        drawn_static += 1
                        break
                if skip_soft_clear:
                    continue
                for rect in soft_clear:
                    if blit.rect.colliderect(rect):
                        if v < (1, 8):
                            screen.blit(blit.surface, blit.rect)
                        else:
                            screen.blit(blit.surface, blit.rect, None, blit.flags)
                        soft_clear.append(blit.rect)
                        drawn_static += 1
                        break
            else:                
                if screen_rect.contains(blit.rect):
                    if v < (1, 8):
                        r = screen.blit(blit.surface, blit.rect)
                    else:
                        r = screen.blit(blit.surface, blit.rect, None, blit.flags)
                    clear_next.append(r)
                elif screen_rect.colliderect(blit.rect):
                    x = blit.rect.clip(screen_rect)
                    y = x.move(-blit.rect.left, -blit.rect.top)
                    b = blit.surf.subsurface(y)
                    if v < (1, 8):
                        r = screen.blit(b, x)
                    else:
                        r = screen.blit(b, x, None, blit.flags)
                    clear_next.append(r)

        # print "%d / %d static drawn, %d dynamic" %
        #       (drawn_static, len(s), len(blits))
        pygame.display.set_caption("%d / %d static, %d dynamic. %d ups, %d fps" %
                                   (
                                   drawn_static, static_blits, dynamic_blits, spyral.director.get_scene(
                                       ).clock.ups,
                                   spyral.director.get_scene().clock.fps))
        # Do the display update
        pygame.display.update(self._clear_next_frame + self._clear_this_frame)
        # Get ready for the next call
        self._clear_this_frame = self._clear_next_frame
        self._clear_next_frame = []
        self._blits = []

    def _exit_scene(self, scene):
        self._saved_blits[scene] = self._static_blits
        self._static_blits = {}
        self._backgrounds[scene] = self._background
        self._background = pygame.surface.Surface(self._rsize)
        self._background.fill((255, 255, 255))
        self._surface.blit(self._background, (0, 0))

    def _enter_scene(self, scene):
        self._static_blits = self._saved_blits.pop(scene, self._static_blits)
        if scene in self._backgrounds:
            self._background = self._backgrounds.pop(scene)
            self._clear_this_frame.append(self._background.get_rect())

    def layers(self):
        """ Returns a list of this camera's layers. """
        return self._layers[:]

    def world_to_local(self, pos):
        """
        Converts coordinates from the display to coordinates in this camera's
        space. If the coordinate is outside, then it returns None.
        """
        pos = spyral.Vec2D(pos)
        if self._rect.collidepoint(pos):
            pos -= self._offset
            pos = pos / self._scale
            return pos
        return None

    def redraw(self):
        self._clear_this_frame.append(self.get_rect())
