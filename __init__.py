"""
Spyral, an awesome library for making games.
"""

__version__ = '0.1'
__license__ = 'LGPLv2'
__author__ = 'Robert Deaton'

import spyral.compat

import spyral.memoize
import spyral.point
import spyral.camera
import spyral.util
import spyral.sprite
import spyral.gui
import spyral.scene
import spyral._lib
import spyral.event
import spyral.animator
import spyral.animation
import pygame

director = scene.Director()

def init():
    pygame.init()
    pygame.font.init()
    
def quit():
    pygame.quit()
    spyral.director._stack = []