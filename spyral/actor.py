import greenlet
import spyral

class Actor(object):
    def __init__(self):
        self._greenlet = greenlet.greenlet(self.main)
        scene = spyral._get_executing_scene()
        scene._register_actor(self, self._greenlet)
            
    def wait(self, dt = 0):
        if dt == 0:
            return self._greenlet.parent.switch(True)
        return self._greenlet.parent.switch(dt)
        
    def run_animation(self, animation):
        progress = 0.0
        dt = 0.0
        while progress < animation.duration:
            progress += dt
            
            if progress > animation.duration:
                extra = progress - animation.duration
                progress = animation.duration
            else:
                extra = 0
            values = animation.evaluate(self, progress)
            for property in animation.properties:
                if property in values:
                    setattr(self, property, values[property])
            dt = self.wait(extra)
        
    def main(self, dt):
        pass