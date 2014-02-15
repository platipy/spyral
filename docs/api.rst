**********************
Complete API Reference
**********************

The following is complete documentation on all public functions and classes
within Spyral. If you need further information on how the internals of a class
work, please consider checking the source code attached.

.. _api.actor:

Actors
------

.. autoclass:: spyral.Actor
    :members:

.. _api.animation:

Animations
----------

.. autoclass:: spyral.Animation
    :members:

.. _api.director:

Director
--------

The director handles initializing and running your game. It is also 
responsible for keeping track of the game's scenes. If you are not using 
the Example.Activity, then you will need to call 
:func:`init <spyral.director.init>` at the very start of your game, before you try
to :func:`run <spyral.director.run>` run your first scene. 

.. code::
    
    spyral.director.init((640, 480))
    # Scene and sprite creation
    spyral.director.run(scene=MyScene())
    
Note that the director provides three ways to change the current scene:

* :func:`Pushing <spyral.director.push>` new Scenes on top of old ones.
* :func:`Popping <spyral.director.pop>`  the current Scene, revealing the one
  underneath (or ending the game if this is the only scene on the stack)
* :func:`Replacing <spyral.director.replace>`  the current Scene with a new one.

.. automodule:: spyral.director
    :members:
    
.. _api.easings:

Easings
-------

.. automodule:: spyral.easing
    :members:
    
.. _api.events:

Events
------

.. automodule:: spyral.event
    :members:
    
.. _api.fonts:

Fonts
-----
    
.. autoclass:: spyral.Font
    :members:
    
.. _api.forms:

Forms
-----
    
.. autoclass:: spyral.Form
    :members:
    
.. _api.images:

Images
------

.. autoclass:: spyral.Image
    :members:
    
.. _api.keyboard:

Keyboard
--------

.. automodule:: spyral.keyboard
    :members:
    
.. _api.mouse:

Mouse
-----
    
.. automodule:: spyral.mouse
    :members:
    
.. _api.rects:

Rects
-----
    
.. autoclass:: spyral.Rect
    :members:
    
.. _api.scenes:

Scenes
------

Scenes are the basic units that are executed by spyral for your game, and should
be subclassed and filled in with code which is relevant to your game. The
:class:`Director <spyral.director>`, is a manager for Scenes,
which maintains a stacks and actually executes the code.


.. autoclass:: spyral.Scene
    :members:
    
.. _api.sprites:

Sprites
-------

.. autoclass:: spyral.Sprite
    :members:

.. _api.vec2ds:

Vec2Ds
------

.. autoclass:: spyral.Vec2D
    :members:

.. _api.views:

Views
-----
    
.. autoclass:: spyral.View
    :members:
    
.. _api.widgets:
    
Widgets
-------

.. autoclass:: spyral.widgets.ButtonWidget
    :members:

.. autoclass:: spyral.widgets.CheckboxWidget
    :members:

.. autoclass:: spyral.widgets.ToggleButtonWidget
    :members:
    
.. autoclass:: spyral.widgets.TextInputWidget
    :members:
