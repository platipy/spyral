Scenes and the Director
-----------------------
Scenes are the basic units that are executed by spyral for your game, and should be subclassed and filled in with code which is relevant to your game. The director, which is accessible at *spyral.director*, is a manager for Scenes, which maintains a stacks and actually executes the code.


.. autoclass:: spyral.Scene
    :members:
    
.. autoclass:: spyral.Sprite
    :members:
    
.. autoclass:: spyral.Vec2D
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