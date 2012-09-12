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
        
        properties = ['x', 'y', 'image', 'scale', 'pos']
        self.property = property
        self.animation = animation
        self.duration = duration
        self.absolute = absolute
        self.loop = False
        
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
        res = dict((p, getattr(sprite, p)) for p in self.properties)
        for animation in self._animations:
            if progress <= animation.duration:
                res.update(animation.evaluate(sprite, progress))
        return res

class SequentialAnimation(Animation):
    def __init__(self, *animations):
        self.properties = set()
        self._animations = animations
        self.duration = 0
        self.absolute = False
        for animation in animations:
            self.properties.update(animation.properties)
            self.duration += animation.duration

    def evaluate(self, sprite, progress):
        # Need to think carefully about floats and how to handle ending conditions, but later
        res = dict((p, getattr(sprite, p)) for p in self.properties)
        if progress == self.duration:
            res.update(self._animations[-1].evaluate(sprite, self._animations[-1].duration))
            return res
        i = 0
        while progress > self._animations[i].duration:
            progress -= self._animations[i].duration
            i += 1
        res.update(self._animations[i].evaluate(sprite, progress))
        return res
        
class DelayAnimation(Animation):
    def __init__(self, duration = 1.0):
        self.absolute = False
        self.properties = set([])
        self.duration = duration
        
    def evaluate(self, sprite, progress):
        return {}


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
        for sprite in self._sprites:
            for animation in self._animations[sprite]:
                self._progress[(sprite, animation)] += dt
                progress = self._progress[(sprite, animation)]
                if progress > animation.duration:
                    progress = animation.duration
                    completed.append((animation, sprite))
    
                values = animation.evaluate(sprite, progress)
                for property in animation.properties:
                    value = values[property]
                    if animation.absolute is False and property in ('x', 'y', 'scale'):
                        value = value + self._start_state[(sprite, animation)][property]
                    if animation.absolute is False and property in ('pos'):
                        s = self._start_state[(sprite, animation)][property]
                        value = (value[0] + s[0], value[1] + s[1])
                    setattr(sprite, property, value)

        for animation, sprite in completed:
            if animation.loop:
                self._progress[(sprite, animation)] = 0
            else:
                self.stop_animation(animation, sprite)
        Group.update(self, dt)

    def stop_animation(self, animation, sprite):
        self._animations[sprite].remove(animation)
        del self._progress[(sprite, animation)]
        c = self._on_complete[(sprite, animation)]
        del self._on_complete[(sprite, animation)]
        try:
            del self._start_state[(sprite, animation)]
        except KeyError:
            pass
        if c is not None:
            c(animation, sprite)
            
    def stop_animations_for_sprite(self, sprite):
        for animation in self._animations[sprite][:]:
            self.stop_animation(animation, sprite)

class AnimationSprite(Sprite):        
    def animate(self, animation, on_complete = None):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.add_animation(self, animation, on_complete)
        
    def stop_animation(self, animation):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.stop_animation(animation, self)
        
    def stop_all_animations(self):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.stop_animations_for_sprite(self)