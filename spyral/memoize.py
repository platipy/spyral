"""This module contains classes to handle memoization, a time-saving method that
caches previously seen results from function calls."""

class Memoize(object):
    """
    This is a decorator to allow memoization of function calls. It is a
    completely dumb cache, and will cache anything given to it indefinitely.

    :param object func: Any function (although any object will work).
    .. warning:: This may be deprecated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        """
        Attempts to return the results of this function call from the cache;
        if it can't find it, then it will execute the function and add it to the
        cache.
        """
        try:
            return self.cache[args]
        except KeyError:
            res = self.func(*args)
            self.cache[args] = res
            return res
        except TypeError:
            print ("WARNING: Unhashable type passed to memoize."
                   "Reconsider using this decorator.")
            return self.func(*args)

class SmartMemoize(object):
    """
    This is a decorator to allow memoization of function calls. Its cache
    is cleared on scene changes, and also clears items from the cache which
    haven't been used in at least 250 frames.

    :param object func: Any function (although any object will work).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.scene = None
        self.last_clear = 0

    def __call__(self, *args):
        """
        Attempts to return the results of this function call from the cache;
        if it can't find it, then it will execute the function and add it to the
        cache.
        """
        from spyral import director
        frame = director.get_tick()
        if director.get_scene() is not self.scene:
            self.scene = director.get_scene()
            self.cache = {}
        if frame - self.last_clear > 100:
            for key, value in self.cache.items():
                data, oldframe = value
                if frame - oldframe > 250:
                    self.cache.pop(key)
            self.last_clear = frame
        try:
            data, oldframe = self.cache[args]
            self.cache[args] = (data, frame)
            return data
        except KeyError:
            res = self.func(*args)
            self.cache[args] = (res, frame)
            return res
        except TypeError:
            print ("WARNING: Unhashable type passed to SmartMemoize."
                   "Reconsider using this decorator")
            return self.func(*args)

class _ImageMemoize(SmartMemoize):
    """
    A subclass of SmartMemoise that is built explicitly for image related calls.
    It allows images to be cleared from its cache when they are updated.
    """
    def clear(self, clear_image):
        """
        Removes the given image from the cache.
        :param clear_image: The image to remove.
        :type clear_image: :class:`Image <spyral.Image>`
        """
        self.cache = dict(((image, scale) for (image, scale)
                                          in self.cache.iteritems()
                                          if image is clear_image))
