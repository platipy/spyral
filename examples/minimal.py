try:
    import _path
except NameError:
    pass
import spyral

resolution = (640, 480)

# the director is the manager for your scenes
spyral.director.init(resolution)

# A Scene will hold sprites
my_scene = spyral.Scene(resolution)
my_scene.background = spyral.Image(size=resolution).fill((0,0,0))

# A Sprite is the simplest drawable item in Spyral
my_sprite = spyral.Sprite(my_scene)

# A Sprite needs to have an Image
my_sprite.image = spyral.Image(size=(16,16)).fill((255,255,255))

# You register events with functions
import sys
my_scene.register("system.quit", spyral.quit)

# This will run your game. Execution will stop here until the game ends.
spyral.director.run(scene=my_scene) 