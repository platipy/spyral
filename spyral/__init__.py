"""
Spyral, an awesome library for making games.
"""

__version__ = '0.3'
__license__ = 'MIT'
__author__ = 'Robert Deaton'

from types import ModuleType
import sys

import spyral.compat
import pygame

# import mapping to objects in other modules
ALL_BY_MODULE = {
    'spyral.debug' : ['DebugText'],
    'spyral.sprite' : ['Sprite'],
    'spyral.scene' : ['Scene'],
    'spyral.image' : ['Image'],
    'spyral.vector' : ['Vec2D'],
    'spyral.rect' : ['Rect'],
    'spyral.animation' : ['Animation'],
    'spyral.core' : ['init', 'quit', '_get_executing_scene'],
    'spyral.cursor' : ['set_cursor', 'MonochromeCursor', 'ColorCursor',
                       'cursors'],
    'spyral.font' : ['Font'],
    'spyral.clock' : ['GameClock'],
    'spyral.event' : ['keys', 'mods', 'queue', 'Event',
                      'EventHandler', 'LiveEventHandler'],
    'spyral.form' : ['Form'],
    'spyral.dev' : ['_get_spyral_path'],
    'spyral.actor' : ['Actor'],
    'spyral.util' : ['anchor_offset'],
    'spyral.exceptions': ['SceneHasNoSizeError', 'NotStylableError',
                          'NoImageError', 'BackgroundSizeError',
                          'LayersAlreadySetError', 'UnusedStyleWarning'],
    'spyral.view': ['View']
}

ATTRIBUTE_MODULES = frozenset(['memoize', 'point', 'exceptions', 'easing',
                               'event', '_lib', 'font', 'form', 'director',
                               'sprite', '_style', 'widgets', 'cursor', 'util'])

OBJECT_ORIGINS = {}
for module, items in ALL_BY_MODULE.iteritems():
    for item in items:
        OBJECT_ORIGINS[item] = module

class SpyralModule(ModuleType):
    """Automatically import objects from the modules."""

    def __getattr__(self, name):
        if name in OBJECT_ORIGINS:
            sub_module = __import__(OBJECT_ORIGINS[name], None, None, [name])
            for extra_name in ALL_BY_MODULE[sub_module.__name__]:
                setattr(self, extra_name, getattr(sub_module, extra_name))
            return getattr(sub_module, name)
        elif name in ATTRIBUTE_MODULES:
            __import__('spyral.' + name)
        return ModuleType.__getattribute__(self, name)

    def __dir__(self):
        """Just show what we want to show."""
        result = list(NEW_MODULE.__all__)
        result.extend(('__file__', '__path__', '__doc__', '__all__',
                       '__docformat__', '__name__', '__path__',
                       '__package__', '__version__'))
        return result

# keep a reference to this module so that it's not garbage collected
OLD_MODULE = sys.modules['spyral']

# setup the new module and patch it into the dict of loaded modules
NEW_MODULE = sys.modules['spyral'] = SpyralModule('spyral')
NEW_MODULE.__dict__.update({
    '__file__': __file__,
    '__package__': 'spyral',
    '__path__': __path__,
    '__doc__': __doc__,
    '__version__': __version__,
    '__all__': tuple(OBJECT_ORIGINS) + tuple(ATTRIBUTE_MODULES),
    '__docformat__': 'restructuredtext en'
})
