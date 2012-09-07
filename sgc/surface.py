#!/usr/bin/env python

#Copyright (C) 2010-2012  Sam Bull

"""
Screen class to store rect information with the screen and setup the toolkit.

"""

import pygame.display
from pygame.locals import *

import spyral.sgc.widgets._locals

class Screen(object):
    """
    Class for the screen.

    This must be used instead of ``pygame.display.set_mode()``.

    Attributes:
      image: The pygame.display screen.
      rect: ``pygame.Rect`` containing screen size.

    """

    __slots__ = ("rect", "image", "_opengl")

    def __init__(self, size, flags=0, depth=0):
        """
        Args:
          size, flags, depth: Arguments for pygame.display.set_mode()

        """
        self.rect = Rect((0,0), size)
        self.image = pygame.display.set_mode(size, flags, depth)
        self._opengl = flags & OPENGL
        widgets._locals.SCREEN = self
        widgets._locals.Font.set_fonts()

    def __getattr__(self, attr):
        """Redirect attribute access to self.image"""
        if attr != "image":
            return getattr(self.image, attr)
        raise AttributeError("image")
