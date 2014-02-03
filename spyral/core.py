import spyral
import pygame
import inspect

_inited = False

def init():
    """
    TODO
    """
    global _inited
    if _inited:
        return
    _inited = True
    spyral.event.init()
    spyral._style.init()
    pygame.display.init()
    pygame.font.init()

def quit():
    """
    TODO
    """
    pygame.quit()
    spyral.director._stack = []
    spyral.director._initialized = False
    
def get_executing_scene():
    for frame, _, _, _, _, _ in inspect.stack():
        args = inspect.getargvalues(frame)
        if len(args.args) > 0 and args.args[0] == 'self':
            o = args.locals['self']
            if isinstance(o, spyral.Scene):
                return o