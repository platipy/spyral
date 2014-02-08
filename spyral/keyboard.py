"""The keyboard modules provides an interface to adjust the keyboard's repeat
rate.

.. attribute:: repeat

    When the keyboard repeat is enabled, keys that are held down will keep
    generating new events over time. Defaults to `False`.

.. attribute:: delay

    `int` to control how many milliseconds before the repeats start.

.. attribute:: interval

    `int` to control how many milliseconds to wait between repeated events.

"""

import sys
import types
import pygame

old = sys.modules[__name__]

class _KeyboardModule(types.ModuleType):
    def __init__(self, *args):
        types.ModuleType.__init__(self, *args)
        self._repeat = False
        self._delay = 600
        self._interval = 100

    def _update_repeat_status(self):
        if self._repeat:
            pygame.key.set_repeat(self._delay, self._interval)
        else:
            pygame.key.set_repeat()

    def _set_repeat(self, repeat):
        self._repeat = repeat
        self._update_repeat_status()

    def _get_repeat(self):
        return self._repeat

    def _set_interval(self, interval):
        self._interval = interval
        self._update_repeat_status()

    def _get_interval(self):
        return self._interval

    def _set_delay(self, delay):
        self._delay = delay
        if delay == 0:
            self._repeat = False
        self._update_repeat_status()

    def _get_delay(self):
        return self._delay

    repeat = property(_get_repeat, _set_repeat)
    delay = property(_get_delay, _set_delay)
    interval = property(_get_interval, _set_interval)

# Keep the refcount from going to 0
keyboard = _KeyboardModule(__name__)
sys.modules[__name__] = keyboard
keyboard.__dict__.update(old.__dict__)
