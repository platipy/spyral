"""
This module provides a set of built-in easings which can be used by any 
game. Additionally, custom easings can be built. An easing should be a 
function (or callable) which takes in a sprite, and a time delta which 
is normalized to [0,1], and returns the state of easing at that time. 
See the source code of this module for some example implementations. 
Built-in easings are stateless, so the same animation can be used many 
times or on many different objects. Custom easings do not have to be 
stateless. 

Visualizations of these easings are available at 
`http://easings.net <http://easings.net>`_ .
"""

import math

def Linear(start=0.0, finish=1.0):
    """
    Linearly increasing: f(x) = x
    """
    def linear_easing(sprite, delta):
        return (finish - start) * (delta) + start
    return linear_easing


def QuadraticIn(start=0.0, finish=1.0):
    """
    Quadratically increasing, starts slower : f(x) = x ^ 2
    """
    def quadratic_easing(sprite, delta):
        return start + (finish - start) * delta * delta
    return quadratic_easing


def QuadraticOut(start=0.0, finish=1.0):
    """
    Quadratically increasing, starts faster : f(x) = 2x - x^2
    """
    def quadratic_out_easing(sprite, delta):
        return start + (finish - start) * (2.0 * delta - delta * delta)
    return quadratic_out_easing


def QuadraticInOut(start=0.0, finish=1.0):
    """
    Quadratically increasing, starts and ends slowly but fast in the middle.
    """
    def quadratic_in_out_easing(sprite, delta):
        delta *= 2
        if delta < 1:
            return start + 0.5 * delta * delta * (finish - start)
        delta -= 1
        return start + (delta - 0.5 * delta * delta + 0.5) * (finish - start)
    return quadratic_in_out_easing


def CubicIn(start=0.0, finish=1.0):
    """
    Cubically increasing, starts very slow : f(x) = x^3
    """
    def cubic_in_easing(sprite, delta):
        return start + (delta * delta * delta) * (finish - start)
    return cubic_in_easing


def CubicOut(start=0.0, finish=1.0):
    """
    Cubically increasing, starts very fast : f(x) = 1 + (x-1)^3
    """
    def cubic_out_easing(sprite, delta):
        delta -= 1.0
        return start + (delta * delta * delta + 1.0) * (finish - start)
    return cubic_out_easing


def CubicInOut(start=0.1, finish=1.0):
    """
    Cubically increasing, starts and ends very slowly but very fast in the
    middle.
    """
    def cubic_in_out_easing(sprite, delta):
        delta *= 2.0
        if delta < 1.0:
            return start + 0.5 * delta * delta * delta * (finish - start)
        delta -= 2.0
        return ((1.0 + 0.5 * delta * delta * delta) *
                (finish - start) +
                2.0 * start)
    return cubic_in_out_easing


def Iterate(items, times=1):
    """
    Iterate over a list of items. This particular easing is very useful
    for creating image animations, e.g.::
    
        walk_images = [spyral.Image('f1.png'), spyral.Image('f2.png'), spyral.Image('f3.png')]
        walking_animation = Animation('image', easing.Iterate(walk_images), 2.0, loop=True)
        my_sprite.animate(walking_animation)
    
    :param list items: A list of items (e.g., a list of
                       :class:`Images <spyral.Image>`).
    :param int times: The number of times to iterate through the list.
    """
    def iterate_easing(sprite, delta):
        # We preturb the result slightly negative so that it ends on
        # the last frame instead of looping back to the first
        i = round(delta * len(items) * times)
        return items[int(i % len(items))]
    return iterate_easing


def Sine(amplitude=1.0, phase=0, end_phase=2.0 * math.pi):
    """
    Depending on the arguments, moves at a different pace according to the sine
    function.
    """
    def sin_easing(sprite, delta):
        return amplitude * math.sin(phase + delta * (2.0 * math.pi - phase))
    return sin_easing


def LinearTuple(start=(0, 0), finish=(0, 0)):
    """
    Linearly increasing, but with two properites instead of one.
    """
    def linear_easing(sprite, delta):
        return ((finish[0] - start[0]) * delta + start[0],
                (finish[1] - start[1]) * delta + start[1])
    return linear_easing


def Arc(center=(0, 0), radius=1, theta_start=0, theta_end=2 * math.pi):
    """
    Increasing according to a circular curve for two properties.
    """
    def arc_easing(sprite, delta):
        theta = (theta_end - theta_start) * delta
        return (center[0] + radius * math.cos(theta),
                center[1] + radius * math.sin(theta))
    return arc_easing


def Polar(center=(0, 0),
          radius=lambda theta: 1.0,
          theta_start=0,
          theta_end=2 * math.pi):
    """
    Similar to an Arc, except the radius should be a function of time.
    """
    def arc_easing(sprite, delta):
        theta = (theta_end - theta_start) * delta
        return (center[0] + radius(theta) * math.cos(theta),
                center[1] + radius(theta) * math.sin(theta))
    return arc_easing
