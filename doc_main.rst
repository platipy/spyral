Scenes and the Director

Sprites have the following built-in attributes.
    
    ============    ============
    Attribute       Description
    ============    ============
    pos             The position of a sprite in 2D coordinates, represented as a :class:`Vec2D <spyral.Vec2D>`
    position        An alias for pos
    x               The x coordinate of the sprite, which will remain synced with the position`
    y               The y coordinate of the sprite, which will remain synced with the position`
    anchor          Defines an `anchor point <anchors>` where coordinates are relative to on the image.
    layer           The name of the layer this sprite belongs to. See `layering <spyral_layering>` for more.
    image           The image for this sprite
    visible         A boolean that represents whether this sprite should be drawn.
    width           Width of the image after all transforms.
    height          Height of the image after all transforms.
    size            (width, height) of the image after all transforms.
    scale           A scale factor for resizing the image. It will always contain a :class:`spyral.Vec2D` with an x factor and a y factor, but it can be set to a numeric value which will be set for both coordinates.
    scale_x         The x factor of the scaling. Kept in sync with scale
    scale_y         The y factor of the scaling. Kept in sync with scale
    flip_x          A boolean that determines whether the image should be flipped horizontally
    flip_y          A boolean that determines whether the image should be flipped vertically
    angle           An angle to rotate the image by. Rotation is computed after scaling and flipping, and keeps the center of the original image aligned with the center of the rotated image.
    parent          The parent of this sprite, either a View or a Scene. Read-only.
    scene           The scene that this sprite belongs to. Read-only.
    mask            A rect to use instead of the current image's rect for computing collisions. `None` if the image's rect should be used.
    ============    ============

Sprites

Rects and Vec2Ds

Events

    Keyboard - list of common keyboard events (complete list in appendix)
    Mouse - complete list of mouse events

Collision Tests

Views and Layers

Forms and Widgets

Actors

Animations and Easings

Fonts

Images

Mouse

Styles


Scenes and the Director
-----------------------
Scenes are the basic units that are executed by spyral for your game, and should be subclassed and filled in with code which is relevant to your game. The director, which is accessible at *spyral.director*, is a manager for Scenes, which maintains a stacks and actually executes the code.

API Reference
-------------

.. autoclass:: spyral.Rect
    :members:

.. automodule:: spyral.mouse
    :members:

.. automodule:: spyral.keyboard
    :members:
    
.. autoclass:: spyral.Image
    :members:

.. autoclass:: spyral.Form
    :members:

.. autoclass:: spyral.Font
    :members:

.. automodule:: spyral.event
    :members:

.. automodule:: spyral.director
    :members:
    
.. automodule:: spyral.easing
    :members:

.. autoclass:: spyral.Animation
    :members:

.. autoclass:: spyral.DebugText
    :members:

.. autoclass:: spyral.Scene
    :members:
    
.. autoclass:: spyral.Sprite
    :members:

.. autoclass:: spyral.Vec2D
    :members:
    
.. autoclass:: spyral.View
    :members:
    
=========================
View size and Window size
=========================
The size of the View is the "internal" or "virtual" size, whereas the window size is the "external" or "real" size.

===================
Stylable Properties
===================

Scenes:

===========    ===============
Property       Value
===========    ===============
size           A tuple or :class:spyral.Vec2D: (width,height) for the virtual, or  "internal", size
background     Either a string (indiciating the filename of the background) or a color three-tuple.
layers         A sequence of strings representing the layers of the scene.
===========    ===============

================
Event Namespaces
================
Something about event namespaces

===================
Anchor Offset Lists
===================

TODO: Image using these anchors

* topleft
* midtop
* topright
* midleft
* center
* midright
* bottomleft
* midbottom
* bottomright