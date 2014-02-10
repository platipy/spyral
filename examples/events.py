try:
    import _path
except NameError:
    pass
import pygame
import spyral
import sys

resolution = (640, 480)

class TestCase(object):
    chars = '123'
    files = ['%s' % chars[x] for x in range(0, 1)]

print TestCase.files


if __name__ == "__main__":
    spyral.director.init(resolution) # the director is the manager for your scenes

    my_scene = spyral.Scene(resolution)
    my_sprite = spyral.Sprite(my_scene)
    my_sprite.image = spyral.Image(size=(50,50))

    spyral.event.register("system.quit", sys.exit)

    def key_down(event):
        print event.key, event.unicode, event.mod

    spyral.event.register("input.keyboard.down.k", key_down)

    spyral.director.run(scene=my_scene) # This will run your game. It will not return.
