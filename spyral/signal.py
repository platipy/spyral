
class Signal(object):
    __slots__ = ['_callbacks']    
    def __init__(self):
        self._callbacks = []
    
    def connect(self, callback):
        self._callbacks.append(callback)
        
    def emit(self, *args, **kwargs):
        for cb in self._callbacks:
            cb(*args, **kwargs)
            
    def clear(self):
        self._callbacks = []
        
    def disconnect(self, callback):
        try:
            self._callbacks.remove(callback)
        except ValueError:
            raise ValueError("Trying to disconnect that which is not connected.")