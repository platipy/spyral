"""Core functionality module - e.g., init, quit"""

import spyral
import pygame
import inspect

_inited = False

def _init():
    """
    This is the core Spyral code that is run on startup; not only does it setup
    spyral, but it also sets up pygame.
    """
    global _inited
    if _inited:
        return
    _inited = True
    spyral.event._init()
    spyral._style.init()
    pygame.display.init()
    pygame.font.init()

def _quit():
    """
    Cleanly quits pygame and empties the spyral stack.
    """
    pygame.quit()
    spyral.director._stack = []
    spyral.director._initialized = False
    raise spyral.exceptions.GameEndException("The game has ended correctly.")

def _get_executing_scene():
    """
    Returns the currently executing scene using Python introspection.

    This function should not be used lightly - it requires some dark magic.
    """
    for frame, _, _, _, _, _ in inspect.stack():
        args = inspect.getargvalues(frame)
        if len(args.args) > 0 and args.args[0] == 'self':
            obj = args.locals['self']
            if isinstance(obj, spyral.Scene):
                return obj
