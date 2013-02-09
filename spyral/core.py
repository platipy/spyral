import spyral
import pygame
import inspect

_inited = False

def init():
    global _inited
    if _inited:
        return
    _inited = True
    spyral.event.init()
    pygame.init()
    pygame.font.init()

def quit():
    pygame.quit()
    spyral.director._stack = []
    
def _get_executing_scene():
    for frame, _, _, _, _, _ in inspect.stack():
        args = inspect.getargvalues(frame)
        if len(args.args) > 0 and args.args[0] == 'self':
            o = args.locals['self']
            if isinstance(o, spyral.Scene):
                return o