import pygame
import spyral

class Director(object):
    def __init__(self):
        self._initialized = False
        pass

    def init(self, size = (0, 0),
                   fullscreen       = False,
                   caption          = "spyral",
                   resizable        = False,
                   noframe          = False,
                   depth            = 0,
                   max_fps          = 60,
                   ticks_per_second = 30):
        """
        Initializes the director which controls the main window.
        The size will be the logical size of the window.
        """
        if self._initialized:
            print 'Warning: Tried to initialize the director twice. Ignoring.'
        pygame.init()
        pygame.font.init()

        flags = 0
        if resizable:
            flags |= pygame.RESIZABLE
        if noframe:
            flags |= pygame.NOFRAME
        if fullscreen:
            flags |= pygame.FULLSCREEN
        self._screen = pygame.display.set_mode(size, flags)

        self._initialized = True

        self._camera = spyral.camera.Camera(virtual_size=size, root=True)
        pygame.display.set_caption(caption)

        self._stack = []
        self._tick = 0

        from sys import platform

        if platform in('win32', 'cygwin'):
            time_source = None
        else:
            time_source = lambda: pygame.time.get_ticks() / 1000.
        self.clock = spyral._lib.gameclock.GameClock(time_source=time_source,
                                                     max_fps=max_fps,
                                                     ticks_per_second=
                                                     ticks_per_second)

        self._max_fps = max_fps
        self._tps = ticks_per_second

    def camera(self):
        return self._camera

    def new_camera(self, size = None):
        """
        Returns a new Camera instance which has the full window, scaling to
        the speified size. Defaults to the same size as the logical display.
        """
        return spyral.camera.Camera(virtual_size=size, root=True)

    def get_screen(self):
        """
        Returns the pygame surface corresponding to the main window.
        This should be used for advanced functionality only."""
        return pygame.display.get_surface()

    def get_scene(self):
        """
        Returns the currently running scene.
        """
        if len(self._stack) > 0:
            return self._stack[-1]
        return None

    def get_tick(self):
        return self._tick

    def replace(self, scene):
        _switch_scene()
        if len(self._stack) > 0:
            old = self._stack.pop()
            old.on_exit()
            _switch_scene()
            self._camera.clear()
        self._stack.append(scene)
        scene.on_enter()
        pygame.event.get()

    def pop(self):
        from Sprite import _switch_scene
        if len(self._stack) < 1:
            return
        scene = self._stack.pop()
        scene.on_exit()
        _switch_scene()
        self._camera.clear()
        director.clock.max_fps = self._max_fps
        director.clock.ticks_per_second = self._tps
        if len(self._stack) > 0:
            scene = self._stack[-1]
            scene.on_enter()
        pygame.event.get()

    def push(self, scene):
        if len(self._stack) > 0:
            old = self._stack[-1]
            old.on_exit()
            spyral._switch_scene()
            self._camera.clear()
        self._stack.append(scene)
        scene.on_enter()
        pygame.event.get()

    def run(self):
        clock = self.clock

        if self._stack > 0:
            while True:
                clock.tick()
                if clock.update_ready:
                    self._stack[-1].update(self._tick)
                    self._tick += 1
                if clock.frame_ready:
                    self._stack[-1].render()


class Scene(object):
    def on_exit(self):
        pass

    def on_enter(self):
        pass

    def render(self):
        pass

    def update(self, tick):
        pass
