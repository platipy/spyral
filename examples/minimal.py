try:
    import _path
except NameError:
    pass
import spyral
import sys

resolution = (640, 480)

if __name__ == "__main__":
    spyral.director.init(resolution) # the director is the manager for your scenes
    
    my_scene = spyral.Scene(resolution)
    my_sprite = spyral.Sprite(my_scene)
    my_sprite.image = spyral.Image(size=(50,50))
    
    my_scene.register("system.quit", sys.exit)
    
    spyral.director.run(scene=my_scene) # This will run your game. It will not return.
