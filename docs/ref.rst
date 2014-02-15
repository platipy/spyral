***************
Quick Reference
***************

.. _ref.anchors:

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

.. _ref.events:

Event List
----------

Director
""""""""

.. function:: "director.update" : Event(delta)

    :param float delta: The amount of time progressed since the last tick
    :triggered by: Every tick of the clock

.. function:: "director.pre_update" : Event()

    :triggered by: Every tick of the clock, before ``"director.update"``

.. function:: "director.post_update" : Event()

    :triggered by: Every tick of the clock, after ``"director.update"``
    
.. function:: "director.render" : Event()

    :triggered by: Every time the director draws the scene

.. function:: "director.pre_render" : Event()

    :triggered by: Directly before ``"director.render"``

.. function:: "director.post_render" : Event()

    :triggered by: Directly after ``"director.render"``
    
.. function:: "director.redraw" : Event()
    
    :triggered by: Every time the Director is forced to redraw the screen (e.g., if the window regains focus after being minimized).
    
.. function:: "director.scene.enter" : Event(scene)
    
    :param scene: The new scene
    :type scene: :class:`Scene <spyral.Scene>`
    :triggered by: Whenever a new scene is on top of the stack, e.g., a new scene is pushed, another scene is popped
    
.. function:: "director.scene.exit" : Event(scene)
    
    :param scene: The old scene
    :type scene: :class:`Scene <spyral.Scene>`
    :triggered by: Whenever a scene is slips off the stack, e.g., a new scene is pushed on top, a scene is popped

Animations
""""""""""

.. function:: "sprites.<name>.animation.start" : Event(animation, sprite)
    
    :param animation: The animation that is starting
    :type animation: :class:`Animation <spyral.Animation>`
    :param sprite: The sprite the animation is being played on
    :type sprite: :class:`Sprite <spyral.Sprite>`
    :triggered by: A new animation starting on a sprite.

.. function:: "sprites.<name>.animation.end" : Event(animation, sprite)
    
    :param animation: The animation that is starting
    :type animation: :class:`Animation <spyral.Animation>`
    :param sprite: The sprite the animation is being played on
    :type sprite: :class:`Sprite <spyral.Sprite>`
    :triggered by: An animation on a sprite ending.
    
User Input
""""""""""

.. function:: "input.mouse.up" : Event(pos, button)
    
    :param pos: The location of the mouse cursor
    :type pos: 2-tuple
    :param 
    :param sprite: The sprite the animation is being played on
    :type sprite: :class:`Sprite <spyral.Sprite>`
    :triggered by: A new animation starting on a sprite.
    
System
""""""

.. function:: "system.quit" : Event()
    
    :triggered by: The OS killing this program, e.g., by pressing the exit button the window handle.
    
.. function:: "system.video_resize" : Event(size, width, height)

    :param size: The new size of the window
    :type size: 2-tuple
    :param int width: The new width of the window
    :param int height: The new height of the window
    :triggered by: Your game loses focus in the OS, e.g., by the window being minimized
    
.. function:: "system.video_expose" : Event()

    :triggered by: The OS requests that a portion of the display be redrawn.
    
.. function:: "system.focus_change" : Event(gain, state)

    :param ??? gain: ???
    :param ??? state: ???
    :triggered by: Your game loses focus in the OS, e.g., by the window being minimized

Forms
"""""


.. _ref.keys:

Keyboard Keys
-------------

.. _ref.mods:

Keyboard Modifiers
------------------

.. _ref.layering:

Layering
--------

Easings
Animations
Rects
Vec2Ds
Widgets

Styleable properties

.. _ref.image_formats:

Valid Image Formats
-------------------

* JPG
* PNG
* GIF (non animated)
* BMP
* PCX
* TGA (uncompressed)
* TIF
* LBM (and PBM)
* PBM (and PGM, PPM)
* XPM
