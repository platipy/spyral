"""
Spyral, an awesome library for making games.
"""

__version__ = '0.1'
__license__ = 'MIT'
__author__ = 'Robert Deaton'

import compat

import memoize
import point
import camera
import util
import sprite
import scene
import _lib
import event
import animator
import animation
import pygame

director = scene.Director()


def init():
    pygame.init()
    pygame.font.init()


def quit():
    pygame.quit()
    director._stack = []
