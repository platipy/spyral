import sys
import types
import pygame
import spyral

old = sys.modules[__name__]

cursors = {"arrow": pygame.cursors.arrow,
           "diamond": pygame.cursors.diamond,
           "x": pygame.cursors.broken_x,
           "left": pygame.cursors.tri_left,
           "right": pygame.cursors.tri_right}

class _MouseModule(types.ModuleType):
    def __init__(self, *args):
        types.ModuleType.__init__(self, *args)
        self._visible = True
    def _get_cursor(self):
        return pygame.mouse.get_cursor()
    def _set_cursor(self, cursor):
        if cursor in cursors:
            pygame.mouse.set_cursor(*cursors[cursor])
        else:
            pygame.mouse.set_cursor(*cursor)
    def _get_visible(self):
        return self._visible
    def _set_visible(self, visiblity):
        pygame.mouse.set_visible(visiblity)
        self._visible = visiblity
    #: 
    cursor = property(_get_cursor, _set_cursor)
    visible = property(_get_visible, _set_visible)

# Keep the refcount from going to 0
mouse = _MouseModule(__name__)
sys.modules[__name__] = mouse
mouse.__dict__.update(old.__dict__)
