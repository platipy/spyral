"""
Spyral, an awesome library for making games.
"""

__version__ = '0.2'
__license__ = 'MIT'
__author__ = 'Robert Deaton'

from types import ModuleType
import sys

import compat
import pygame

# import mapping to objects in other modules
all_by_module = {
    'spyral.sprite' : ['Sprite', 'AggregateSprite', 'ViewPort'],
    'spyral.scene' : ['Scene'],
    'spyral.image' : ['Image'],
    'spyral.vector' : ['Vec2D'],
    'spyral.rect' : ['Rect'],
    'spyral.animation' : ['Animation'],
    'spyral.core' : ['init', 'quit', '_get_executing_scene'],
    'spyral.font' : ['Font'],
    'spyral.clock' : ['GameClock'],
    'spyral.event' : ['keys', 'mods', 'queue', 'Event', 'EventHandler', 'LiveEventHandler'],
    'spyral.form' : ['TextInputWidget', 'Form', 'FormStyle', 'ButtonWidget'],
    'spyral.dev' : ['_get_spyral_path'],
    'spyral.actor' : ['Actor'],
    'spyral.exceptions': ['SceneHasNoSizeError', 'NotStylableError', 'NoImageError', 'BackgroundSizeError']
}

attribute_modules = frozenset(['memoize', 'point', 'exceptions', 'animator', 'event', '_lib', 'color', 'font', 'form', 'director', 'sprite', '_style'])

object_origins = {}
for module, items in all_by_module.iteritems():
    for item in items:
        object_origins[item] = module

class module(ModuleType):
    """Automatically import objects from the modules."""

    def __getattr__(self, name):
        if name in object_origins:
            module = __import__(object_origins[name], None, None, [name])
            for extra_name in all_by_module[module.__name__]:
                setattr(self, extra_name, getattr(module, extra_name))
            return getattr(module, name)
        elif name in attribute_modules:
            __import__('spyral.' + name)
        return ModuleType.__getattribute__(self, name)

    def __dir__(self):
        """Just show what we want to show."""
        result = list(new_module.__all__)
        result.extend(('__file__', '__path__', '__doc__', '__all__',
                       '__docformat__', '__name__', '__path__',
                       '__package__', '__version__'))
        return result

# keep a reference to this module so that it's not garbage collected
old_module = sys.modules['spyral']

# setup the new module and patch it into the dict of loaded modules
new_module = sys.modules['spyral'] = module('spyral')
new_module.__dict__.update({
    '__file__': __file__,
    '__package__': 'spyral',
    '__path__': __path__,
    '__doc__': __doc__,
    '__version__': __version__,
    '__all__': tuple(object_origins) + tuple(attribute_modules),
    '__docformat__': 'restructuredtext en'
})
