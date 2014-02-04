# We use a patcher here to add some functionality from Python 2.6+ to 2.5
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 5:
    _property = property

    class property(property):
        """
        Custom class meant to implement Python 2.6+ property functionality into
        Python 2.5.
        """
        def __init__(self, fget, *args, **kwargs):
            self.__doc__ = fget.__doc__
            super(property, self).__init__(fget, *args, **kwargs)

        def setter(self, fset):
            cls_ns = sys._getframe(1).f_locals
            for key, value in cls_ns.iteritems():
                if value == self:
                    propname = key
                    break
            cls_ns[propname] = property(self.fget, fset,
                                        self.fdel, self.__doc__)
            return cls_ns[propname]

    __builtins__['property'] = property
