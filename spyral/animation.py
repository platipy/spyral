"""Animations interpolate a property between two values over a number of frames.
They can be combined to run at the same time, or directly after each other."""

class Animation(object):
    """
    Creates an animation on *property*, with the specified
    *easing*, to last *duration* in seconds.

    The following example shows a Sprite with an animation that will linearly
    change its 'x' property from 0 to 100 over 2 seconds.::

        from spyral import Sprite, Animation, easing
        ...
        my_sprite = Sprite(my_scene)
        my_animation = Animation('x', easing.Linear(0, 100), 2.0)
        my_sprite.animate(my_animation)

    Animations can be appended one after another with the `+`
    operator, and can be run in parallel with the `&` operator.

    >>> from spyral import Animation, easing
    >>> first  = Animation('x', easing.Linear(0, 100), 2.0)
    >>> second = Animation('y', easing.Linear(0, 100), 2.0)
    # Sequential animations
    >>> right_angle = first + second
    # Parallel animations
    >>> diagonal = first & second

    :param property: The property of the sprite to change (e.g., 'x')
    :type property: :class:`string`
    :param easing: The easing (rate of change) of the property.
    :type easing: :class:`Easing <spyral.Easing>`
    :param duration: How many seconds to play the animation
    :type duration: :class:`float`
    :param absolute: (**Unimplemented?**) Whether to position this relative
                     to the sprite's offset, or to absolutely position it on the
                     screen.
    :type absolute: :class:`boolean`
    :param shift: How much to offset the animation (a number if the property is
                  scalar, a :class:`Vec2D <spyral.Vec2D>` if the property is
                  "pos", and None if there is no offset.
    :type shift: None, a :class:`Vec2D <spyral.Vec2D>`, or a number
    :param loop: Whether to loop indefinitely
    :type loop: :class:`boolean`
    """

    def __init__(self, property,
                 easing,
                 duration=1.0,
                 absolute=True,
                 shift=None,
                 loop=False
                 ):
        # Idea: These easings could be used for camera control
        # at some point. Everything should work pretty much the same.
        self.absolute = absolute
        self.property = property
        self.easing = easing
        self.duration = duration
        self.loop = loop
        self.properties = set((property,))
        self._shift = shift

    def evaluate(self, sprite, progress):
        """
        For a given *sprite*, complete *progress*'s worth of this animation.
        Basically, complete a step of the animation. Returns a dictionary
        representing the changed property and its new value, e.g.:
        :code:`{"x": 100}`. Typically, you will use the sprite's animate function instead of calling
        this directly.

        :param sprite: The Sprite that will be manipulated.
        :type sprite: :class:`Sprite <spyral.Sprite>`
        :param float progress: The amount of progress to make on this animation.
        :rtype: :class:`dict`
        """
        progress = progress / self.duration
        value = self.easing(sprite, progress)
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
    """
    Class for creating parallel animation from two other animations.

    This does not respect the absolute setting on individual
    animations. Pass absolute as a keyword argument to change,
    default is True.
    Absolute applies only to numerical properties.

    loop is accepted as a kwarg, default is True if any child
    loops, or False otherwise.
    """
    def __init__(self, *animations, **kwargs):
        self.properties = set()
        self._animations = []
        self.duration = 0
        self.absolute = kwargs.get('absolute', True)
        self.loop = False
        for animation in animations:
            i = animation.properties.intersection(self.properties)
            if i:
                message = "Cannot animate on the same properties twice: %s"
                raise ValueError(message % i)
            self.properties.update(animation.properties)
            self._animations.append(animation)
            self.duration = max(self.duration, animation.duration)
            if animation.loop:
                self.loop = True
        # Ensure we don't clobber on properties
        clobbering_animations = [('scale', set(['scale_x', 'scale_y'])),
                                 ('pos', set(['x', 'y', 'position'])),
                                 ('position', set(['x', 'y', 'pos']))]
        for prop, others in clobbering_animations:
            overlapping_properties = self.properties.intersection(others)
            if prop in self.properties and overlapping_properties:
                message = "Cannot animate on %s and %s in the same animation."
                raise ValueError(message % (prop,
                                            overlapping_properties.pop()))
        self.loop = kwargs.get('loop', self.loop)

    def evaluate(self, sprite, progress):
        res = {}
        for animation in self._animations:
            if progress <= animation.duration:
                res.update(animation.evaluate(sprite, progress))
            else:
                res.update(animation.evaluate(sprite, animation.duration))
        return res


class SequentialAnimation(Animation):
    """
    An animation that represents the input animations in sequence.

    loop is accepted as a kwarg, default is False.

    If the last animation in a SequentialAnimation is set to loop,
    that animation will be looped indefinitely at the end, but not
    the entire SequentialAnimation. If loop is set to true, the
    entire SequentialAnimation will loop indefinitely.
    """
    def __init__(self, *animations, **kwargs):
        self.properties = set()
        self._animations = animations
        self.duration = 0
        self.absolute = True
        self.loop = kwargs.get('loop', False)
        for animation in animations:
            self.properties.update(animation.properties)
            self.duration += animation.duration
            if self.loop and animation.loop:
                raise ValueError("Looping sequential animation with a looping "
                                 "animation anywhere in the sequence "
                                 "is not allowed.")
            if animation.loop and animation is not animations[-1]:
                raise ValueError("Looping animation in the middle of a "
                                 "sequence is not allowed.")
        if animations[-1].loop is True:
            self.loop = self.duration - animations[-1].duration

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

    def evaluate(self, sprite, progress):
        return {}
