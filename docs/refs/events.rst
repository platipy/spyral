.. _ref.events:

**********
Event List
**********

There are many events that are built into Spyral. The following is a complete
lists of them. You can :func:`register <spyral.event.register>` a handler
for an event, and even :func:`queue <spyral.event.queue>` your own
custom events.

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

.. function:: "input.mouse.down[.left | .right | .middle | .scroll_up | .scroll_down]" : Event(pos, button)
    
    :param pos: The location of the mouse cursor
    :type pos: 2-tuple
    :param str button: Either ``"left"``, ``"right"``, ``"middle"``, ``"scroll_up"``, or ``"scroll_down"``.
    :triggered by: Either any mouse button being pressed, or a specific mouse button being pressed

.. function:: "input.mouse.up[.left | .right | .middle | .scroll_up | .scroll_down]" : Event(pos, button)
    
    :param pos: The location of the mouse cursor
    :type pos: 2-tuple
    :param str button: Either ``"left"``, ``"right"``, ``"middle"``, ``"scroll_up"``, or ``"scroll_down"``.
    :triggered by: Either any mouse button being released, or a specific mouse button being released
    
.. function:: "input.mouse.motion" : Event(pos, rel, buttons, left, right, middle)
    
    :param pos: The location of the mouse cursor
    :type pos: 2-tuple
    :param rel: The relative change in the location of the mouse cursor
    :type rel: 2-tuple
    :param buttons: a 3-tuple of boolean values corresponding to whether the left, middle, and right buttons are being pressed
    :type buttons: 3-tuple
    :param bool left: whether the left button is being pressed
    :param bool middle: whether the middle button is being pressed
    :param bool right: whether the right button is being pressed
    :triggered by: The mouse being moved

.. function:: "input.keyboard.up[.* | .f | .down | etc...]" : Event(unicode, key, mod)

    :param unicode unicode: A printable representation of this key
    :param int key: A keycode for this key, comparable to one found in :class:`Keys <spyral.event.keys>`
    :param int mod: A keycode for this modifier, comparable to one found in :class:`Mods <spyral.event.mods>`
    :triggered by: A key being released
    
.. function:: "input.keyboard.down[.* | .f | .down | etc...]" : Event(key, mod)

    :param int key: A keycode for this key, comparable to one found in :class:`Keys <spyral.event.keys>`
    :param int mod: A keycode for this modifier, comparable to one found in :class:`Mods <spyral.event.mods>`
    :triggered by: A key being pressed
    
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

    
.. function:: "form.<form name>.<widget name>.changed" : Event(widget, form, value)

    :param widget: The widget being changed
    :type widget: :ref:`Widget <api.widgets>`
    :param form: The form that this widget belongs to
    :type form: :class:`Form <spyral.Form>`
    :param str value: The value of this widget
    :triggered by: The widget having its value changed (e.g., Button being pressed or released, TextInput being edited)

.. function:: "form.<form name>.<widget name>.clicked" : Event(widget, form, value)

    .. note::

        Only :class:`Button <spyral.widgets.ButtonWidget>`'s trigger this event.

    :param widget: The widget being clicked
    :type widget: :ref:`Widget <api.widgets>`
    :param form: The form that this widget belongs to
    :type form: :class:`Form <spyral.Form>`
    :param str value: The value of this widget
    :triggered by: The widget being pressed and then released.