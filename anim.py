from spyral import animations
from spyral.sprite import Sprite, Group
from collections import defaultdict
from spyral import animations

class Animation(object):
    def __init__(self, property,
                       animation,
                       duration = 1.0,
                       absolute = True,
                       shift = None,
                       loop = False
                       ):
        """
        *animation* determines the animation you wish to apply
        
        *duration* is the amount of time the animation should take.
        
        *property* is the property of the sprite you wish to animate.
        Special properties are "x" and "y" which refer to the first
        and second parts of the position tuple.
        """
        
        # Idea: These animators could be used for camera control
        # at some point. Everything should work pretty much the same.
        
        properties = ['x', 'y', 'image', 'scale', 'pos']
        self.property = property
        self.animation = animation
        self.duration = duration
        self.loop = loop
        self.properties = set((property,))
        self._shift = shift
                
    def evaluate(self, sprite, progress):
        progress = progress/self.duration
        value = self.animation(sprite, progress)
        if self._shift is not None:
            if self.property == 'pos':
                value = (value[0] + self._shift[0],
                         value[1] + self._shift[1])
            else:
                value = value + self._shift
        return {self.property : value}

    def __and__(self, second):
        return MultiAnimation(self, second)
        
    def __iand__(self, second):
        return MultiAnimation(self, second)
        
    def __add__(self, second):
        return SequentialAnimation(self, second)
        
    def __iadd__(self, second):
        return SequentialAnimation(self, second)

class MultiAnimation(Animation):
    def __init__(self, *animations, **kwargs):
        """
        This does not respect the absolute setting on individual
        animations. Pass absolute as a keyword argument to change,
        default is True.
        Absolute applies only to numerical properties.
        
        loop is accepted as a kwarg, default is True if any child
        loops, or False otherwise.
        """
        self.properties = set()
        self._animations = []
        self.duration = 0
        self.absolute = kwargs.get('absolute', True)
        self.loop = False
        for animation in animations:
            i = animation.properties.intersection(self.properties) 
            if i:
                raise ValueError("Cannot animate on the same properties twice: %s" % str(i))
            self.properties.update(animation.properties)
            self._animations.append(animation)
            self.duration = max(self.duration, animation.duration)
            if animation.loop:
                self.loop = True
        self.loop = kwargs.get('loop', self.loop)
            
    def evaluate(self, sprite, progress):
        res = dict((p, getattr(sprite, p)) for p in self.properties)
        for animation in self._animations:
            if progress <= animation.duration:
                res.update(animation.evaluate(sprite, progress))
        return res

class SequentialAnimation(Animation):
    def __init__(self, *animations, **kwargs):
        """
        An animation that represents the input animations in sequence.
        
        loop is accepted as a kwarg, default is False.
        
        If the last animation in a SequentialAnimation is set to loop,
        that animation will be looped indefinitely at the end, but not
        the entire SequentialAnimation. If loop is set to true, the 
        entire SequentialAnimation will loop indefinitely.
        """
        self.properties = set()
        self._animations = animations
        self.duration = 0
        self.absolute = True
        self.loop = kwargs.get('loop', False)
        for animation in animations:
            self.properties.update(animation.properties)
            self.duration += animation.duration
            if self.loop and animation.loop:
                raise ValueError("Looping sequential animation with a looping animation anywhere in the sequence is not allowed.")
            if animation.loop and animation is not animations[-1]:
                raise ValueError("Looping animation in the middle of a sequence is not allowed.")
        if animations[-1].loop is True:
            self.loop = self.duration - animations[-1].duration
        print self.loop
    def evaluate(self, sprite, progress):
        res = dict((p, getattr(sprite, p)) for p in self.properties)
        if progress == self.duration:
            res.update(self._animations[-1].evaluate(sprite, self._animations[-1].duration))
            return res
        i = 0
        while progress > self._animations[i].duration:
            progress -= self._animations[i].duration
            i += 1
        if i > 0:
            res.update(self._animations[i-1].evaluate(sprite, self._animations[i-1].duration))
        res.update(self._animations[i].evaluate(sprite, progress))
        return res
        
class DelayAnimation(Animation):
    def __init__(self, duration = 1.0):
        self.absolute = False
        self.properties = set([])
        self.duration = duration
        self.loop = False
        
    def evaluate(self, sprite, progress):
        return {}

class AnimationGroup(Group):
    def __init__(self, *args):
        Group.__init__(self, *args)
        self._animations = defaultdict(list)
        self._progress = {}
        self._on_complete = {}
    
    def add_animation(self, animation, sprite, on_complete = None):
        for a in self._animations[sprite]:
            if a.properties.intersection(animation.properties):
                raise ValueError("Cannot animate on propety %s twice" % animation.property)
        self._animations[sprite].append(animation)
        self._progress[(sprite, animation)] = 0
        self._on_complete[(sprite, animation)] = on_complete
        self.evaluate(animation, sprite, 0.0)
            
    def evaluate(self, animation, sprite, progress):
        values = animation.evaluate(sprite, progress)
        for property in animation.properties:
            setattr(sprite, property, values[property])
        
    def update(self, dt):
        completed = []
        for sprite in self._sprites:
            for animation in self._animations[sprite]:
                self._progress[(sprite, animation)] += dt
                progress = self._progress[(sprite, animation)]
                if progress > animation.duration:
                    progress = animation.duration
                    completed.append((animation, sprite))
                self.evaluate(animation, sprite, progress)

        for animation, sprite in completed:
            if animation.loop is True:
                self._progress[(sprite, animation)] = 0
            elif animation.loop:
                print animation.loop
                self._progress[(sprite, animation)] = animation.loop
            else:
                self.stop_animation(animation, sprite)
        Group.update(self, dt)

    def stop_animation(self, animation, sprite):
        self._animations[sprite].remove(animation)
        del self._progress[(sprite, animation)]
        c = self._on_complete[(sprite, animation)]
        del self._on_complete[(sprite, animation)]
        if c is not None:
            c(animation, sprite)
            
    def stop_animations_for_sprite(self, sprite):
        for animation in self._animations[sprite][:]:
            self.stop_animation(animation, sprite)

class AnimationSprite(Sprite):        
    def animate(self, animation, on_complete = None):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.add_animation(animation, self, on_complete)
        
    def stop_animation(self, animation):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.stop_animation(animation, self)
        
    def stop_all_animations(self):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.stop_animations_for_sprite(self)