class Memoize(object):
    """
    This is a decorator to allow memoization of function calls. It is a
    completely dumb cache, and will cache anything given to it indefinitely.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            data, oldframe = self.cache[args]
            self.cache[args] = (data, frame)
            return data
        except KeyError:
            res = self.func(*args)
            self.cache[args] = (res, frame)
            return res
        except TypeError:
            print "WARNING: Unhashable type passed to memoize2. Reconsider using this decorator"
            return self.func(*args)


class SmartMemoize(object):
    """
    This is a decorator to allow memoization of function calls. Its cache
    is cleared on scene changes, and also clears items from the cache which
    haven't been used in at least 250 frames.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.scene = None
        self.last_clear = 0

    def __call__(self, *args):
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
            print "WARNING: Unhashable type passed to memoize2. Reconsider using this decorator"
            return self.func(*args)
