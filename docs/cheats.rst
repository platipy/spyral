************
Cheat Sheets
************

The following are convenient listings of the attributes and methods of some of
the more common classes and modules.

Sprites
-------

========================================    ============================================================   =======================
Attribute                                   Type                                                           Description
========================================    ============================================================   =======================
:func:`pos <spyral.Sprite.pos>`             :class:`Vec2D <spyral.Vec2D>`                                  Sprite's position within the parent
:func:`x <spyral.Sprite.x>`                 ``int``                                                        Sprite's horizontal position within the parent
:func:`y <spyral.Sprite.y>`                 ``int``                                                        Sprite's vertical position within the parent
:func:`anchor <spyral.Sprite.anchor>`       ``str`` (:ref:`anchor point <ref.anchors>`)                    Where to offset this sprite
:func:`image <spyral.Sprite.image>`         :class:`Image <spyral.image.Image>`                            The image to display
:func:`visible <spyral.Sprite.visible>`     ``bool``                                                       Whether or not to render this sprite
:func:`layer <spyral.Sprite.layer>`         ``str`` (:ref:`layering <ref.layering>`)                       Which layer of the parent to place this sprite in
:func:`width <spyral.Sprite.width>`         ``float``                                                      Width of the sprite after all transforms
:func:`height <spyral.Sprite.height>`       ``float``                                                      Height of the sprite after all transforms
:func:`size <spyral.Sprite.size>`           :class:`Vec2D <spyral.Vec2D>`                                  Size of the sprite after all transforms
:func:`rect <spyral.Sprite.rect>`           :class:`Rect <spyral.Rect>`                                    A rect describing size and position
:func:`scale <spyral.Sprite.scale>`         :class:`Vec2D <spyral.Vec2D>` (can be set to ``float``)        Scale factor for resizing the image
:func:`scale_x <spyral.Sprite.scale_x>`     ``float``                                                      Scale factor for horizontally resizing the image
:func:`scale_y <spyral.Sprite.scale_y>`     ``float``                                                      Scale factor for vertically resizing the image
:func:`flip_x <spyral.Sprite.flip_x>`       ``bool``                                                       Whether the image should be flipped horizontally
:func:`flip_y <spyral.Sprite.flip_y>`       ``bool``                                                       Whether the image should be flipped vertically
:func:`angle <spyral.Sprite.angle>`         ``float``                                                      How much to rotate the image
:func:`mask <spyral.Sprite.mask>`           :class:`Rect <spyral.Rect>` or ``None``                        Alternate size of collision box
:func:`parent* <spyral.Sprite.parent>`      :class:`View <spyral.View>` or :class:`Scene <spyral.Scene>`   The immediate parent View or Scene
:func:`scene* <spyral.Sprite.scene>`        :class:`Scene <spyral.Scene>`                                  The top-most parent Scene
========================================    ============================================================   =======================

\*Read-only


Scenes
------
============================================  ============================================================   =======================
Attribute                                     Type                                                           Description
============================================  ============================================================   =======================
:func:`background <spyral.Scene.background>`  :class:`Image <spyral.image.Image>`                            The image to display as the static background
:func:`layers** <spyral.Scene.layers>`        ``list`` of ``str`` (:ref:`layering <ref.layering>`)           The layers for this scene
:func:`width* <spyral.Scene.width>`           ``int``                                                        Width of this scene internally (not the window).
:func:`height* <spyral.Scene.height>`         ``int``                                                        Height of this scene internally (not the window).
:func:`size* <spyral.Scene.size>`             :class:`Vec2D <spyral.Vec2D>`                                  Size of this scene internally (not the window).
:func:`rect <spyral.Scene.rect>`              :class:`Rect <spyral.Rect>`                                    A rect stretching from ``(0, 0)`` to the size of the window.
:func:`parent* <spyral.Sprite.parent>`        :class:`Scene <spyral.Scene>`                                  This Scene
:func:`scene* <spyral.Sprite.scene>`          :class:`Scene <spyral.Scene>`                                  This Scene
============================================  ============================================================   =======================

\*Read-only

\** Can only be set once

Views
-----

================================================= ============================================================   =======================
Attribute                                         Type                                                           Description
================================================= ============================================================   =======================
:func:`pos <spyral.View.pos>`                     :class:`Vec2D <spyral.Vec2D>`                                  View's position within the parent
:func:`x <spyral.View.x>`                         ``int``                                                        View's horizontal position within the parent
:func:`y <spyral.View.y>`                         ``int``                                                        View's vertical position within the parent
:func:`width <spyral.View.width>`                 ``float``                                                      Internal width of the view
:func:`height <spyral.View.height>`               ``float``                                                      Internal height of the view
:func:`size <spyral.View.size>`                   :class:`Vec2D <spyral.Vec2D>`                                  Internal size of the view
:func:`rect <spyral.View.rect>`                   :class:`Rect <spyral.Rect>`                                    A rect describing size and position
:func:`anchor <spyral.View.anchor>`               ``str`` (:ref:`anchor point <ref.anchors>`)                    Where to offset this view
:func:`visible <spyral.View.visible>`             ``bool``                                                       Whether or not to render this view
:func:`layer <spyral.View.layer>`                 ``str`` (:ref:`layering <ref.layering>`)                       Which layer of the parent to place this view in
:func:`layers** <spyral.View.layers>`             ``list`` of ``str`` (:ref:`layering <ref.layering>`)           The layers for this view
:func:`scale <spyral.View.scale>`                 :class:`Vec2D <spyral.Vec2D>` (can be set to ``float``)        Scale factor for resizing the view
:func:`scale_x <spyral.View.scale_x>`             ``float``                                                      Scale factor for horizontally resizing the view
:func:`scale_y <spyral.View.scale_y>`             ``float``                                                      Scale factor for vertically resizing the view
:func:`output_width <spyral.View.output_width>`   ``float``                                                      Width of the view after all transforms
:func:`output_height <spyral.View.output_height>` ``float``                                                      Height of the view after all transforms
:func:`output_size <spyral.View.output_size>`     :class:`Vec2D <spyral.Vec2D>`                                  Size of the sprite after all transforms
:func:`crop <spyral.View.crop>`                   ``bool``                                                       Whether this View should be cropped
:func:`crop_width <spyral.View.crop_width>`       ``float``                                                      Horizontal amount to keep uncropped
:func:`crop_height <spyral.View.crop_height>`     ``float``                                                      Vertical amount to keep uncropped
:func:`crop_size <spyral.View.crop_size>`         :class:`Vec2D <spyral.Vec2D>`                                  Size of the uncropped region within the View
:func:`mask <spyral.View.mask>`                   :class:`Rect <spyral.Rect>` or ``None``                        Alternate size of collision box
:func:`parent* <spyral.View.parent>`              :class:`View <spyral.View>` or :class:`Scene <spyral.Scene>`   The immediate parent View or Scene
:func:`scene* <spyral.View.scene>`                :class:`Scene <spyral.Scene>`                                  The top-most parent Scene
================================================= ============================================================   =======================

\*Read-only

\** Can only be set once