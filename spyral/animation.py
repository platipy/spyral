import spyral
from spyral.sprite import Sprite
from collections import defaultdict


class Animation(object):
    """
    Creates an animation on *property*, with the specified
    *animator*, to last *duration* in seconds.
    
    For example. Animation('x', animator.Linear(0, 100), 2.0)
    creates an animation that will change the x propety of what it
    is applied to from 0 to 100 over 2 seconds.
    
    Animations can be appended one after another with the `+`
    operator, and can be run in parallel with the `&` operator.
    """

    def __init__(self, property,
                 animator,
                 duration=1.0,
                 absolute=True,
                 shift=None,
                 loop=False
                 ):
        # Idea: These animators could be used for camera control
        # at some point. Everything should work pretty much the same.

        self.property = property
        self.animator = animator
        self.duration = duration
        self.loop = loop
        self.properties = set((property,))
        self._shift = shift
        
        self.on_complete = spyral.Signal()

    def evaluate(self, sprite, progress):
        progress = progress / self.duration
        value = self.animator(sprite, progress)
        if self._shift is not None:
            if self.property == 'pos':
                value = (value[0] + self._shift[0],
                         value[1] + self._shift[1])
            else:
                value = value + self._shift
        return {self.property: value}

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
        # Ensure we don't clobber on properties
        clobbering_animations = [('scale', set(['scale_x', 'scale_y'])),
                                 ('pos', set(['x', 'y', 'position'])),
                                 ('position', set(['x', 'y', 'pos']))]
        for p, others in clobbering_animations:
            if p in self.properties and self.properties.intersection(others):
                raise ValueError("Cannot animate on %s and %s in the same animation." % (p, str(self.properties.intersection(others).pop())))
        self.loop = kwargs.get('loop', self.loop)
        self.on_complete = spyral.Signal()

    def evaluate(self, sprite, progress):
        res = {}
        for animation in self._animations:
            if progress <= animation.duration:
                res.update(animation.evaluate(sprite, progress))
            else:
                res.update(animation.evaluate(sprite, animation.duration))
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
        self.on_complete = spyral.Signal()

    def evaluate(self, sprite, progress):
        res = {}
        if progress == self.duration:
            res.update(self._animations[-1].evaluate(sprite,
                       self._animations[-1].duration))
            return res
        i = 0
        while progress > self._animations[i].duration:
            progress -= self._animations[i].duration
            i += 1
        if i > 0:
            res.update(self._animations[i - 1].evaluate(sprite,
                       self._animations[i - 1].duration))
        res.update(self._animations[i].evaluate(sprite, progress))
        return res


class DelayAnimation(Animation):
    """
    Animation which performs no actions. Useful for lining up appended
    and parallel animations so that things run at the right times.
    """
    def __init__(self, duration=1.0):
        self.absolute = False
        self.properties = set([])
        self.duration = duration
        self.loop = False
        self.on_complete = spyral.Signal()

    def evaluate(self, sprite, progress):
        return {}
