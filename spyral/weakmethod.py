"""
This magic was taken from
http://code.activestate.com/recipes/81253-weakmethod/#c4

This module provides classes and methods for weakly referencing functions and
bound methods; it turns out this is a non-trivial problem.
"""

import weakref

class WeakMethodBound(object):
    """
    Holds a weak reference to a bound method for an object.

    .. attribute::method

        The function being called.
    """
    def __init__(self, func):
        self.func = func.im_func
        self.weak_object_ref = weakref.ref(func.im_self)
    def _func(self):
        return self.func
    method = property(_func)
    def __call__(self, *arg):
        if self.weak_object_ref() == None:
            raise TypeError('Method called on dead object')
        return apply(self.func, (self.weak_object_ref(), ) + arg)

class WeakMethodFree(object):
    """
    Holds a weak reference to an unbound function. Included only for
    completeness.

    .. attribute::method

        The function being called.
    """
    def __init__(self, func):
        self.func = weakref.ref(func)
    def _func(self):
        return self.func()
    method = property(_func)
    def __call__(self, *arg):
        if self.func() == None:
            raise TypeError('Function no longer exist')
        return apply(self.func(), arg)

def WeakMethod(func):
    """
    Attempts to create a weak reference to this function; only bound methods
    require a weakreference.
    """
    try:
        func.im_func
    except AttributeError:
        return func
    return WeakMethodBound(func)
