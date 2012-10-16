try:
    import _path
except NameError:
    pass
import spyral
import sys
import greenlet
import functools

SIZE = (600, 600)
BG_COLOR = (0, 0, 0)

class Manager(object):
    def __init__(self):
        self._greenlets = {} # Maybe use a weakref dict here later
    
    def register(self, actor, greenlet):
        self._greenlets[actor] = greenlet

    def _run(self, dt):
        for actor, greenlet in self._greenlets.iteritems():
            greenlet.switch(dt)
            
    def run(self, dt):
        g = greenlet.greenlet(_manager._run)
        g.switch(dt)
        
_manager = Manager()

class Actor(object):
    def __init__(self):
        spyral.Sprite.__init__(self)
        self._greenlet = greenlet.greenlet(self.main)
        _manager.register(self, self._greenlet)
            
    def wait(self):
        return self._greenlet.parent.switch(0.1)
        
    def run_animation(self, animation):
        progress = 0.0
        dt = 0.0
        while progress < animation.duration:
            progress += dt
            
            if progress > animation.duration:
                progress = animation.duration
            values = animation.evaluate(self, progress)
            for property in animation.properties:
                if property in values:
                    setattr(self, property, values[property])
            dt = self.wait()
        
    def main(self, dt):
        pass
        
    
class StupidSprite(spyral.Sprite, Actor):
    def __init__(self):
        spyral.Sprite.__init__(self)
        Actor.__init__(self)
        
        self.image = spyral.Image(size=(10, 10))
        self.image.fill((255, 255, 255))
        self.pos = (0, 0)
        self.anchor = 'center'
        
    def main(self, dt):
        right = spyral.Animation('x', spyral.animator.Linear(0, 600), duration = 1.0)
        down = spyral.Animation('y', spyral.animator.Linear(0, 600), duration = 1.0)
        left = spyral.Animation('x', spyral.animator.Linear(600, 0), duration = 1.0)
        up = spyral.Animation('y', spyral.animator.Linear(600, 0), duration = 1.0)
        while True:
            self.run_animation(right)
            self.run_animation(down)
            self.run_animation(left)
            self.run_animation(up)
         
class Game(spyral.Scene):
    def __init__(self):
        spyral.Scene.__init__(self)
        self.camera = self.parent_camera.make_child(SIZE)
        self.group = spyral.Group(self.camera)
        self.initialized = False
        self.a1 = StupidSprite()
        self.group.add(self.a1)
        
    def on_enter(self):
        if self.initialized:
            return
        self.initialized = True

        bg = spyral.Image(size=SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
                
    def render(self):
        self.group.draw()
        
    def update(self, dt):
        for event in self.event_handler.get():
            if event['type'] == 'QUIT':
                spyral.quit()
                sys.exit()
                    
        # self.group.update(dt)
        _manager.run(dt)
        

if __name__ == "__main__":
    spyral.init()
    spyral.director.init(SIZE)
    spyral.director.push(Game())
    spyral.director.run()
