import math
__doc__ = 
"""
This module provides a set of built-in animators which can be used by
any game. Additionally, custom animators can be built. An animator
should be a function (or callable) which takes in a sprite, and a 
time delta which is normalized to [0,1], and returns the state of
animator at that time. See the source code of this module for some
example implementations.

Built-in animators are stateless, so the same animation can be used
many times or on many different objects. Custom animators do not
have to be stateless.

"""

"""
Many of these animators were inspired by Clutter/Kivy, but have been
generalized.
"""


def Linear(start=0.0, finish=1.0):
    def linear_animator(sprite, dt):
        return (finish - start) * (dt) + start
    return linear_animator


def QuadraticIn(start=0.0, finish=1.0):
    def quadratic_animator(sprite, dt):
        return start + (finish - start) * dt * dt
    return quadratic_animator


def QuadraticOut(start=0.0, finish=1.0):
    def quadratic_out_animator(sprite, dt):
        return start + (finish - start) * (2.0 * dt - dt * dt)
    return quadratic_out_animator


def QuadraticInOut(start=0.0, finish=1.0):
    def quadratic_in_out_animator(sprite, dt):
        dt *= 2
        if dt < 1:
            return start + 0.5 * dt * dt * (finish - start)
        dt -= 1
        return start + (dt - 0.5 * dt * dt + 0.5) * (finish - start)
    return quadratic_in_out_animator


def CubicIn(start=0.0, finish=1.0):
    def cubic_in_animator(sprite, dt):
        return start + (dt * dt * dt) * (finish - start)
    return cubic_in_animator


def CubicOut(start=0.0, finish=1.0):
    def cubic_out_animator(sprite, dt):
        dt -= 1.0
        return start + (dt * dt * dt + 1.0) * (finish - start)
    return cubic_out_animator


def CubicInOut(start=0.1, finish=1.0):
    def cubic_in_out_animator(sprite, dt):
        dt *= 2.0
        if dt < 1.0:
            return start + 0.5 * dt * dt * dt * (finish - start)
        dt -= 2.0
        return (1.0 + 0.5 * dt * dt * dt) * (finish - start) + 2.0 * start
    return cubic_in_out_animator


def Iterate(items, times=1):
    def iterate_animator(sprite, dt):
        # We preturb the result slightly negative so that it ends on
        # the last frame instead of looping back to the first
        i = round(dt * len(items) * times)
        return items[int(i % len(items))]
    return iterate_animator


def Sine(amplitude=1.0, phase=0, end_phase=2.0 * math.pi):
    def sin_animator(sprite, dt):
        return amplitude * math.sin(phase + dt * (2.0 * math.pi - phase))
    return sin_animator


def LinearTuple(start=(0, 0), finish = (0, 0)):
    def linear_animator(sprite, dt):
        return ((finish[0] - start[0]) * dt + start[0],
                (finish[1] - start[1]) * dt + start[1])
    return linear_animator


def Arc(center=(0, 0), radius = 1, theta_start = 0, theta_end = 2 * math.pi):
    def arc_animator(sprite, dt):
        theta = (theta_end - theta_start) * dt
        return (center[0] + radius * math.cos(theta),
                center[1] + radius * math.sin(theta))
    return arc_animator


def Polar(center=(0, 0), radius = lambda theta: 1.0, theta_start = 0, theta_end = 2 * math.pi):
    def arc_animator(sprite, dt):
        theta = (theta_end - theta_start) * dt
        return (center[0] + radius(theta) * math.cos(theta),
                center[1] + radius(theta) * math.sin(theta))
    return arc_animator
