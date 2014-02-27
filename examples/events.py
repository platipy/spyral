try:
    import _path
except NameError:
    pass
import pygame
import spyral
import sys

resolution = (640, 480)

if __name__ == "__main__":
    spyral.director.init(resolution)

    my_scene = spyral.Scene(resolution)
    my_sprite = spyral.Sprite(my_scene)
    my_sprite.image = spyral.Image(size=(50,50))

    spyral.event.register("system.quit", sys.exit, scene=my_scene)

    def key_down(event):
        print event.key, event.unicode, event.mod

    # Note that we now need to pass in the scene!
    spyral.event.register("input.keyboard.down", key_down, scene=my_scene)

    spyral.director.run(scene=my_scene)
