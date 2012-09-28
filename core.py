import spyral
import pygame

def init():
    spyral.event.init()
    pygame.init()
    pygame.font.init()


def quit():
    pygame.quit()
    spyral.director._stack = []