import spyral
import time

class Scene(object):
    """
    Represents a state of the game as it runs.

    *self.clock* will contain an instance of GameClock which can be replaced
    or changed as is needed.
    *self.parent_camera* will contain a Camera object that this scene should
    use as the basis for all of it's cameras.
    """
    def __init__(self, parent_camera=None, max_ups=None, max_fps=None):
        """
        By default, max_ups and max_fps are pulled from the director.
        """
        time_source = time.time
        self.clock = spyral.GameClock(
            time_source=time_source,
            max_fps=max_fps or spyral.director._max_fps,
            max_ups=max_ups or spyral.director._max_ups)
        self.clock.use_wait = True
        if parent_camera is None:
            parent_camera = spyral.director.get_camera()

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
