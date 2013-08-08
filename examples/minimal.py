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

# A Sprite is the simplest drawable item in Spyral
my_sprite = spyral.Sprite(my_scene)

# A Sprite needs to have an Image
my_sprite.image = spyral.Image(size=(500,100))

# You register events with functions
import sys
my_scene.register("system.quit", sys.exit)

# This will run your game. Execution will stop here until the game ends.
spyral.director.run(scene=my_scene) 
