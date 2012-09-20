import spyral
from spyral.sprite import Sprite, Group
from collections import defaultdict


class Animation(object):
    def __init__(self, property,
                 animator,
                 duration=1.0,
                 absolute=True,
                 shift=None,
                 loop=False
                 ):
        """
        *animator* determines the animation you wish to apply

        *duration* is the amount of time the animation should take.

        *property* is the property of the sprite you wish to animate.
        Special properties are "x" and "y" which refer to the first
        and second parts of the position tuple.
        """

        # Idea: These animators could be used for camera control
        # at some point. Everything should work pretty much the same.

        properties = ['x', 'y', 'image', 'scale', 'pos']
        if property not in properties:
            raise ValueError('%s is not a valid animation property.' % (property))
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
        self.loop = kwargs.get('loop', self.loop)

    def evaluate(self, sprite, progress):
        res = dict((p, getattr(sprite, p)) for p in self.properties)
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

    def evaluate(self, sprite, progress):
        res = dict((p, getattr(sprite, p)) for p in self.properties)
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
    def __init__(self, duration=1.0):
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

    def add_animation(self, animation, sprite):
        for a in self._animations[sprite]:
            if a.properties.intersection(animation.properties):
                raise ValueError(
                    "Cannot animate on propety %s twice" % animation.property)
        self._animations[sprite].append(animation)
        self._progress[(sprite, animation)] = 0
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
                    self.evaluate(animation, sprite, animation.duration)
                    if animation.loop is True:
                        self.evaluate(animation, sprite, progress - animation.duration)
                        self._progress[(sprite, animation)] = progress - animation.duration
                    elif animation.loop:
                        self.evaluate(animation, sprite, progress - animation.duration + animation.loop)
                        self._progress[(sprite, animation)] = progress - animation.duration + animation.loop
                    else:
                        completed.append((animation, sprite))
                else:
                    self.evaluate(animation, sprite, progress)

        for animation, sprite in completed:
            self.stop_animation(animation, sprite)
        Group.update(self, dt)

    def stop_animation(self, animation, sprite):
        if sprite in self._animations and animation in self._animations[sprite]:
            self._animations[sprite].remove(animation)
            animation.on_complete.emit(animation, sprite)
            del self._progress[(sprite, animation)]

    def stop_animations_for_sprite(self, sprite):
        for animation in self._animations[sprite][:]:
            self.stop_animation(animation, sprite)


class AnimationSprite(Sprite):
    def animate(self, animation):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.add_animation(animation, self)

    def stop_animation(self, animation):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.stop_animation(animation, self)

    def stop_all_animations(self):
        if self.group is None:
            raise ValueError("You must add this sprite to an AnimationGroup before you can animate it.")
        self.group.stop_animations_for_sprite(self)
