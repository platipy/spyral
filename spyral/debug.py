"""Various functions and classes meant for prototyping and debugging. These
should never show up in a production game."""

import os
import spyral
import pygame

class DebugText(spyral.Sprite):
    """
    A simple Sprite subclass for rapidly rendering text on the screen.

    :param scene: The parent View or Scene that this will live in.
    :type scene: :class:`View <spyral.View>` or :class:`Scene <spyral.Scene>`
    :param str text: The string that will be rendered.
    :param color: A three-tuple of RGB values ranging from 0-255. Defaults to
                  black (0, 0, 0).
    :type color: A three-tuple.

    .. attribute:: text

        The string that will be rendered. Line breaks ("\\\\n") and other
        special characters will not be rendered correctly. Set-only (as opposed
        to read-only).

    """
    def __init__(self, scene, text, color=(0, 0, 0)):
        spyral.Sprite.__init__(self, scene)
        self._font = spyral.Font(spyral._get_spyral_path() +
                                os.path.join("resources", "fonts",
                                             "DejaVuSans.ttf"),
                                15, color)
        self._render(text)

    def _render(self, text):
        """
        Updates the sprite's image based on the new text.
        :param str text: The string that will be rendered.
        """
        self.image = self._font.render(text)
    # Intentionally impossible to get text; don't rely on it!
    text = property(lambda self: "", _render)

class FPSSprite(spyral.Sprite):
    """
    A simple Sprite subclass for rapidly rendering the current frames-per-second
    and updates-per-second on the screen.

    :param scene: The parent View or Scene that this will live in.
    :type scene: :class:`View <spyral.View>` or :class:`Scene <spyral.Scene>`
    :param color: A three-tuple of RGB values ranging from 0-255. Defaults to
                  black (0, 0, 0).
    :type color: A three-tuple.

    """
    def __init__(self, scene, color):
        spyral.Sprite.__init__(self, scene)
        self._font = spyral.Font(spyral._get_spyral_path() +
                                os.path.join("resources", "fonts",
                                             "DejaVuSans.ttf"),
                                15, color)
        self._render(0, 0)
        self._update_in = 5
        spyral.event.register("director.update", self._update, scene=scene)

    def _render(self, fps, ups):
        """
        Updates the sprite's image based on the current fps/ups.
        :param int fps: The string that will be rendered.
        """
        self.image = self._font.render("%d / %d" % (fps, ups))

    def _update(self):
        """
        Updates the clock with information about the FPS, every 5 seconds.
        """
        self._update_in -= 1
        if self._update_in == 0:
            self._update_in = 5
            clock = self.scene.clock
            self._render(clock.fps, clock.ups)
