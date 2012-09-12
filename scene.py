import pygame
import spyral
import time


class Director(object):
    """
    The director, accessible at *spyral.director*, handles running the game.
    It will switch between scenes and call their render and update methods
    as necessary.
        """
    def __init__(self):
        self._initialized = False
        pass

    def init(self,
             size=(0, 0),
             max_ups = 30,
             max_fps = 30,
             fullscreen = False,
             caption = "spyral"):
        """
        Initializes the director.

        | *size* is the resolution of the display. (0,0) uses the screen resolution
        | *max_ups* sets the number of times scene.update() should be
           called per frame. This will remain the same, even if fps drops.
        | *max_fps* sets the fps cap on the game.
        | *fullscreen* determines whether the display starts fullscreen
        | *caption* is the window caption
        """
        if self._initialized:
            print('Warning: Tried to initialize the director twice. Ignoring.')
        pygame.init()
        pygame.font.init()

        flags = 0
        # These flags are going to be managed better or elsewhere later
        resizable = False
        noframe = False

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

        self._max_ups = max_ups
        self._max_fps = max_fps

    def get_camera(self):
        """
        Returns the root camera for the display.
        """
        return self._camera

    def get_scene(self):
        """
        Returns the currently running scene.
        """
        try:
            return self._stack[-1]
        except IndexError:
            return None

    def get_tick(self):
        """
        Returns the current tick number, where ticks happen on each update,
        not on each frame.
        """
        return self._tick

    def replace(self, scene):
        """
        Replace the currently running scene on the stack with *scene*.
        This does return control, so remember to return after calling it.
        """
        if self._stack:
            old = self._stack.pop()
            old.on_exit()
            spyral.sprite._switch_scene()
            self._camera._exit_scene(old)
        self._stack.append(scene)
        self._camera._enter_scene(scene)
        scene.on_enter()
        pygame.event.get()

    def pop(self):
        """
        Pop the top scene off the stack, returning control to the next scene
        on the stack. If the stack is empty, the program will quit.

        This does return control, so remember to return after calling it.
        """
        if len(self._stack) < 1:
            return
        scene = self._stack.pop()
        scene.on_exit()
        spyral.sprite._switch_scene()
        self._camera._exit_scene(scene)
        if self._stack:
            scene = self._stack[-1]
            self._camera._enter_scene(scene)
            scene.on_enter()
        else:
            exit(0)
        pygame.event.get()

    def push(self, scene):
        """
        Place *scene* on the top of the stack, and move control to it.

        This does return control, so remember to return after calling it.
        """
        if self._stack:
            old = self._stack[-1]
            old.on_exit()
            spyral.sprite._switch_scene()
            self._camera._exit_scene(old)
        self._stack.append(scene)
        self._camera._enter_scene(scene)
        scene.on_enter()
        pygame.event.get()

    def run(self, sugar=False, profiling=False):
        """
        Runs the scene as dictated by the stack.

        If profiling is enabled, this function will return on every
        scene change so that scenes can be profiled independently.
        """
        if sugar:
            import gtk
        if not self._stack:
            return
        old_scene = None
        scene = self.get_scene()
        camera = self._camera
        clock = scene.clock
        stack = self._stack
        while True:
            scene = stack[-1]
            if scene is not old_scene:
                if profiling and old_scene is not None:
                    return
                clock = scene.clock
                old_scene = scene

                def frame_callback(interpolation):
                    scene.render()
                    camera._draw()

                def update_callback(dt):
                    if sugar:
                        while gtk.events_pending():
                            gtk.main_iteration()
                    if len(pygame.event.get([pygame.VIDEOEXPOSE])) > 0:
                        camera.redraw()
                        scene.redraw()
                    scene.event_handler.tick()
                    scene.update(dt)
                    self._tick += 1
                clock.frame_callback = frame_callback
                clock.update_callback = update_callback
            clock.tick()


class Scene(object):
    """
    Represents a state of the game as it runs.

    *self.clock* will contain an instance of GameClock which can be replaced
    or changed as is needed.
    *self.event_handler* will contain an EventHandler object that this scene
    should use to pull events.
    *self.parent_camera* will contain a Camera object that this scene should
    use as the basis for all of it's cameras.
    """
    def __init__(self, event_handler=None, parent_camera=None, max_ups=None, max_fps=None):
        """
        By default, max_ups and max_fps are pulled from the director.
        """
        from sys import platform
        time_source = time.time
        self.clock = spyral._lib.gameclock.GameClock(
            time_source=time_source,
            max_fps=max_fps or spyral.director._max_fps,
            max_ups=max_ups or spyral.director._max_ups)
        self.clock.use_wait = True
        if event_handler is None:
            event_handler = spyral.event.LiveEventHandler()
        if parent_camera is None:
            parent_camera = spyral.director.get_camera()

        self.event_handler = event_handler
        self.parent_camera = parent_camera

    def on_exit(self):
        """
        Called by the director when this scene is about to run.
        """
        pass

    def on_enter(self):
        """
        Called by the director when this scene is exiting.
        """
        pass

    def render(self):
        """
        Called by the director when a new frame needs to be rendered.
        """
        pass

    def update(self, tick):
        """
        Called by the director when a new game logic step should be taken.
        """
        pass

    def redraw(self):
        """
        Advanced: Called by the director if the scene should force redraw of non-spyral based assets, like PGU
        """
        pass
