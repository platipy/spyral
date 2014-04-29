"""Actors are tools for rapidly adding multiprocessing behavior to your game."""

import greenlet
import spyral

class Actor(object):
    """
    Actors are a powerful mechanism for quickly adding multiprocessing behavior
    to your game through `Greenlets <http://greenlet.readthedocs.org/>`_ .
    Any object that subclasses the Actor
    mixin can implement a `main` method that will run concurrently. You can put
    a non-terminating loop into it, and it will work like magic, allowing
    other actors and the main game itself to keep processing::
    
        class MyActor(spyral.Actor):
            def main(self, delta):
                while True:
                    print "Acting!"
                    
    When an instance of the above class is created in a scene, it will
    continuously print "Acting!" until the scene ends. Like a Sprite, An Actor
    belongs to the Scene that was currently active when it was created.
    """
    def __init__(self):
        self._greenlet = greenlet.greenlet(self.main)
        scene = spyral.director.get_scene()
        scene._register_actor(self, self._greenlet)

    def wait(self, delta=0):
        """
        Switches execution from this Actor for *delta* frames to the other
        Actors. Returns the amount of time that this actor was left waiting.

        :param delta: the number of frames(?) to wait.
        :type delta: number
        :rtype: float
        """
        if delta == 0:
            return self._greenlet.parent.switch(True)
        return self._greenlet.parent.switch(delta)

    def run_animation(self, animation):
        """
        Run this animation, without blocking other Actors, until the animation
        completes.
        """
        progress = 0.0
        delta = 0.0
        while progress < animation.duration:
            progress += delta

            if progress > animation.duration:
                extra = progress - animation.duration
                progress = animation.duration
            else:
                extra = 0
            values = animation.evaluate(self, progress)
            for property in animation.properties:
                if property in values:
                    setattr(self, property, values[property])
            delta = self.wait(extra)

    def main(self, delta):
        """
        The main function is executed continuously until either the program
        ends or the main function ends. While the Actor's scene is not on the
        top of the stack, the Actor is paused; it will continue when the Scene
        is back on the top of the Directory's stack.
        
        :param float delta: The amount of time that has passed since this
                            method was last invoked.
        """
        pass
