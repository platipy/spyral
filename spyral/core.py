import spyral
import pygame

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