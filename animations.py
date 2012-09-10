import math
"""
All animators should be functions which take the input time as a number
from 0 to 1 and return a new value for the property they are animating.

For numerical properties, this should also be normalized to a [0, 1]
scale, allowing for the possibility of a [-1, 1] scale as well.
"""

def Linear(start = 0, finish = 0):
    def linear_animator(dt):
        return (finish-start)*(dt)+start
    return linear_animator
    
def Iterate(items, times = 1):
    def iterate_animator(dt):
        # We preturb the result slightly negative so that it ends on
        # the last frame instead of looping back to the first
        i = math.floor(dt*len(items)*times-0.00000001) 
        return items[int(i % len(items))]
    return iterate_animator
    
def Sin(amplitude = 1.0, phase = 0, end_phase = 2.0*math.pi):
    def sin_animator(dt):
        return amplitude*math.sin(phase + dt*(2.0*math.pi-phase))
    return sin_animator