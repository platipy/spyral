import spyral

class View(object):
    def __init__(self, parent):
        """
        Creates a new view with a scene or view as a parent.

        Views have the following built-in attributes
    
        ============    ============
        Attribute       Description
        ============    ============
        pos             The position of a sprite in 2D coordinates, represented as a :class:`Vec2D <spyral.Vec2D>`. (Default: (0, 0))
        position        An alias for pos
        x               The x coordinate of the sprite, which will remain synced with the position`
        y               The y coordinate of the sprite, which will remain synced with the position`
        size            The (width, height) of this view's coordinate space (:class:`Vec2D <spyral.Vec2d>`). (Default: size of the parent)
        width           The width of the view.
        height          The height of the view
        output_size     The (width, height) of this view when drawn on the parent (:class:`Vec2D <spyral.Vec2d>`). (Default: size of the parent)
        output_width    The width of this view when drawn on the parent.
        output_height   The height of this view when drawn on the parent.
        scale           A scale factor from the size to the output_size for the view. It will always contain a :class:`spyral.Vec2D` with an x factor and a y factor, but it can be set to a numeric value which will be set for both coordinates.
        scale_x         The x factor of the scaling. Kept in sync with scale
        scale_y         The y factor of the scaling. Kept in sync with scale
        anchor          Defines an `anchor point <anchors>` where coordinates are relative to in the view.
        layer           The name of the layer this view belongs to in it's parent. See `layering <spyral_layering>` for more.
        layers          A list of layers that the children of this view can be in. See `layering <spyral_layering>` for more.
        visible         A boolean that represents whether this view should be drawn (default: True).
        crop            A boolean that determines whether the view should crop anything outside of it's size (default: True)
        ============    ============
        """

        self._size = parent.size
        self._dest_size = parent.size

        self._pos = spyral.Vec2D(0,0)
        self._crop = True
        self._parent = parent

        self.scene = scene = parent.scene

        scene.register("spyral.internal.view.changed.%s" %
                           (spyral.event.get_identifier(parent)),
                       self._changed)

    def _get_size(self):
        return self._size

    def _set_size(self, size):
        if self._size == size:
            return
        self._size = spyral.Vec2D(size)
        self._changed()

    def _get_dest_size(self):
        return self._dest_size

    def _set_dest_size(self, size):
        if self._dest_size == size:
            return
        self._dest_size = spyral.Vec2D(size)
        self._changed()

    def _changed(self):
        spyral.event.handle("spyral.internal.view.changed.%s" %
                                spyral.event.get_identifier(self))
