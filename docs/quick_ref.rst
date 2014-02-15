***************
Quick Reference
***************

Scene
    attributes
    methods
    
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
    attributes
    methods
    
Views
==============    ============
Attribute         Description
==============    ============
pos               The position of a sprite in 2D coordinates, represented as a :class:`Vec2D <spyral.Vec2D>`. (Default: (0, 0))
position          An alias for pos
x                 The x coordinate of the sprite, which will remain synced with the position
y                 The y coordinate of the sprite, which will remain synced with the position
size              The (width, height) of this view's coordinate space (:class:`Vec2D <spyral.Vec2d>`). (Default: size of the parent)
width             The width of the view.
height            The height of the view
output_size       The (width, height) of this view when drawn on the parent (:class:`Vec2D <spyral.Vec2d>`). (Default: size of the parent)
output_width      The width of this view when drawn on the parent.
output_height     The height of this view when drawn on the parent.
scale             A scale factor from the size to the output_size for the view. It will always contain a :class:`Vec2D <spyral.Vec2D>` with an x factor and a y factor, but it can be set to a numeric value which will be set for both coordinates.
scale_x           The x factor of the scaling. Kept in sync with scale
scale_y           The y factor of the scaling. Kept in sync with scale
anchor            Defines an `anchor point <anchors>` where coordinates are relative to in the view.
layer             The name of the layer this view belongs to in it's parent. See `layering <spyral_layering>` for more.
layers            A list of layers that the children of this view can be in. See `layering <spyral_layering>` for more.
visible           A boolean that represents whether this view should be drawn (default: True).
crop              A boolean that determines whether the view should crop anything outside of it's size (default: True)
crop_size         The (width, height) of the area that will be cropped; anything outside of this region will be removed
crop_width        The width of the cropped area
crop_height       The height of the cropped area
parent            The first parent View or Scene that this View belongs to. Read-only.
scene             The Scene that this View belongs to. Read-only.
rect              A rect represnting the position and size of this view.
mask              A rect to use instead of the current image's rect for computing collisions. `None` if the view's rect should be used.
visible           Whether or not this View and its children will be drawn.
==============    ============


Images
    Attributes
        size
        height (int) (read-only)
        width (int) (read-only)
        
    Methods
        draw_circle
        
Anchors
-------

* topleft
* midtop
* topright
* midleft
* center
* midright
* bottomleft
* midbottom
* bottomright

Events

.. _ref.keys:

Keyboard Keys
-------------

.. _ref.mods:

Keyboard Modifiers
------------------

Easings
Animations
Rects
Vec2Ds
Widgets

Styleable properties