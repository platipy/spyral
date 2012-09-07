#!/usr/bin/env python

# Copyright (C) 2012  Sam Bull

"""
Imports useful objects into the local namespace.

Constants:
  GUI: Event type for any event emitted by this toolkit.

"""

import types

from spyral.sgc.widgets._locals import GUI

class EventSlot(object):
    """
    Event slots object. Allows dynamic allocation of events.

    """

    __slots__ = ("_funcs",)

    def __init__(self, widget, event, funcs=()):
        """
        Args:
          widget: The widget you want to bind this event slot to.
          event: ``str`` The attribute you want to bind to (e.g. 'on_click').
          funcs: A sequence of functions you want to include by default.

        """
        assert event.startswith("on_") and hasattr(widget, event), \
            "%r is not a valid event for %s" % (event, widget.__class__)
        self._funcs = list(funcs)
        setattr(widget, event, types.MethodType(self, widget, widget.__class__))

    def __call__(self, widget):
        """Callback all registered functions for this event."""
        for f in self._funcs:
            f(widget)

    def add(self, func):
        """
        Add additional functions to be called.

        Args:
          func: A function or sequence of functions to be added.

        """
        if callable(func):
            self._funcs.append(func)
        else:
            self._funcs.extend(func)

    def remove(self, func):
        """
        Remove functions from the existing set of functions.

        Args:
          func: A function or sequence of functions to be removed.

        """
        try:
            self._funcs.remove(func)
        except ValueError:
            for f in func:
                self._funcs.remove(f)
