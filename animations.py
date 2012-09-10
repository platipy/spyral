"""
All animators should be functions which take the input time as a number
from 0 to 1 and return a new value for the property they are animating.

For numerical properties, this should also be normalized to a [0, 1]
scale, allowing for the possibility of a [-1, 1] scale as well.
"""

def Linear(start, finish):
    def linear_animator(dt):
        return (finish-start)*(dt)+start
    return linear_animator