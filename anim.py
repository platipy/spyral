from spyral import animations
from spyral.sprite import Sprite, Group
from collections import defaultdict
from spyral import animations

class Animation(object):
    def __init__(self, property,
                       animation,
                       duration = 1.0,
                       absolute = True,
                       ):
        """
        *animation* determines the animation you wish to apply
        
        *absolute* determines whether the property should be in
        absolute coordinates, or whether this is an offset
        animation that should be added to the current property.
        
        *duration* is the amount of time the animation should take.
        
        *property* is the property of the sprite you wish to animate.
        Special properties are "x" and "y" which refer to the first
        and second parts of the position tuple.
        """
        
        # Idea: These animators could be used for camera control
        # at some point. Everything should work pretty much the same.
        
        properties = ['x', 'y', 'image', 'scale']
        self.property = property
        self.animation = animation
        self.duration = duration
        self.absolute = absolute
        
        self.properties = set((property,))
        
    def evaluate(self, sprite, progress):
        progress = progress/self.duration
        value = self.animation(sprite, progress)
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
        """
        self.properties = set()
        self._animations = []
        self.duration = 0
        self.absolute = kwargs.get('absolute', True)
        for animation in animations:
            i = animation.properties.intersection(self.properties) 
            if i:
                raise ValueError("Cannot animate on the same properties twice: %s" % str(i))
            self.properties.update(animation.properties)
            self._animations.append(animation)
            self.duration = max(self.duration, animation.duration)
            
            
    def evaluate(self, sprite, progress):
        res = {}
        for animation in self._animations:
            res.update(animation.evaluate(sprite, progress))
        return res

class SequentialAnimation(Animation):
    def __init__(self, *animations):
        self.properties = set()
        self._animations = animations
        self.duration = 0
        self._next_cutoff = animations[0].duration
        self._old_cutoff = 0
        self._index = 0
        self._total = 0
        self.absolute = False
        for animation in animations:
            self.properties.update(animation.properties)
            self.duration += animation.duration

    def evaluate(self, sprite, progress):
        # Need to think carefully about floats and how to handle ending conditions, but later
        res = dict((p, getattr(sprite, p)) for p in self.properties)
        if progress > self._next_cutoff:
            self._index += 1
            self._old_cutoff = self._next_cutoff
            self._next_cutoff += self._animations[self._index].duration
            res.update(self._animations[self._index - 1].evaluate(sprite, self._animations[self._index - 1].duration))
        progress = progress - self._old_cutoff
        res.update(self._animations[self._index].evaluate(sprite, progress))
        return res
        

class AnimationGroup(Group):
    def __init__(self, *args):
        Group.__init__(self, *args)
        self._animations = defaultdict(list)
        self._progress = {}
        self._on_complete = {}
        self._start_state = {}
    
    def add_animation(self, sprite, animation, on_complete = None):
        for a in self._animations[sprite]:
            if a.properties.intersection(animation.properties):
                raise ValueError("Cannot animate on propety %s twice" % animation.property)
        self._animations[sprite].append(animation)
        self._progress[(sprite, animation)] = 0
        self._on_complete[(sprite, animation)] = on_complete
        if animation.absolute is False:
            self._start_state[(sprite, animation)] = dict((p, getattr(sprite, p)) for p in animation.properties)
        
    def update(self, dt):
        completed = []
        on_completes = []
        for sprite in self._sprites:
            for animation in self._animations[sprite]:
                self._progress[(sprite, animation)] += dt
                progress = self._progress[(sprite, animation)]
                if progress > animation.duration:
                    progress = animation.duration
                    completed.append((sprite, animation))
    
                values = animation.evaluate(sprite, progress)
                for property in animation.properties:
                    value = values[property]
                    if animation.absolute is False and property in ('x', 'y', 'scale'):
                        value = value + self._start_state[(sprite, animation)][property]
                    setattr(sprite, property, value)

        for sprite, animation in completed:
            self._animations[sprite].remove(animation)
            del self._progress[(sprite, animation)]
            c = self._on_complete[(sprite, animation)]
            on_completes.append(c)
            del self._on_complete[(sprite, animation)]
            try:
                del self._start_state[(sprite, animation)]
            except KeyError:
                pass
        d = [c() for c in on_completes if c is not None]
        Group.update(self, dt)

class AnimationSprite(Sprite):
    """
    TODO: Should verify the group it is added to is an AnimationGroup,
    and enforce the one group per sprite rule
    """
    def animate(self, animation, on_complete = None):
        self._groups[0].add_animation(self, animation, on_complete)