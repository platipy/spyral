try:
    import _path
except NameError:
    pass
import pygame
import spyral

resolution = (640, 480)

if __name__ == "__main__":
    spyral.director.init(resolution)

    my_scene = spyral.Scene(resolution)
    my_scene.background = spyral.Image(size=resolution).fill((0,0,0))
    my_sprite = spyral.Sprite(my_scene)
    my_sprite.image = spyral.Image(size=(50,50))

    spyral.event.register("system.quit", spyral.director.quit, scene=my_scene)

    # Can accept the keys directly
    def key_down(key, unicode, mod):
        print key, unicode, mod
    def mouse_down(pos, button):
        print pos, button
    
    # Or maybe none or only some of them!
    def key_down_alt1(key, mod):
        print key, mod
    def mouse_down_alt1():
        print "Clicked"
    
    # Also can accept an "event" parameter instead
    def key_down_alt2(event):
        print event.key, event.unicode, event.mod
    def mouse_down_alt2(event):
        print event.pos, event.button

    # Note that we now need to pass in the scene!
    spyral.event.register("input.keyboard.down", key_down, scene=my_scene)
    spyral.event.register("input.mouse.down", mouse_down, scene=my_scene)

    spyral.director.run(scene=my_scene)
