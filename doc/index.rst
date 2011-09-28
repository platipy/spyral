.. Spyral documentation master file, created by
   sphinx-quickstart on Sun Sep 11 19:03:04 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Spyral
======

What is spyral?
---------------
spyral is a 2D game engine/framework built on top of pygame. Its purpose is to
support rapid prototyping and development of efficient games. It started as a
project to allow easy optimization of games for the `OLPC XO`_, and has evolved
into a semi-complete but still evolving framework for developing games.

Getting started
---------------
To get spyral, you can clone the git repository, or download packages, from the
`github site`_. For now, you can simply include the spyral directory in your
project. A setup.py will be included at a later date. For a barebones example,
see spyral/examples/skel.py, which provides a skeleton example of a program,
complete with comments.	

The Core API
------------

.. toctree::
   :maxdepth: 2
   
   scene
   sprite
   camera

Convenience API
---------------

.. toctree::
   :maxdepth: 2
   
   util
   point
   gui
   memoize

..	Features
	--------
	* Optimized Sprite and Group classes that minimize the amount of drawing.
	* A named layering system, to simplify code by allowing out of order rendering.
	* Automatic scaling to arbitrary resolutions.

FAQ
---

I'm stuck! I need help!
#######################
E-mail me at rdeaton@udel.edu. For generic pygame help, or even asking me questions about spyral, you can also use IRC and visit #pygame at irc.freenode.net. You can find me there under the handle masquerade.

Why are the render and update loops separate?
#############################################
Often example pygame code you will see uses one main loop for the whole program.
In spyral, the two loops are separate because it provides for a more consistent
experience across platforms. Often, a game with one main loop is written to run
at whatever the framerate is capped at. If the machine it is running on can no
longer handle this, the game mechanics slow down, making a less than pleasurable
experience and an unfair advantage in some situations.

If we instead separate the render loop, which is known to be slow, and the
update loop, we can make sure that all game mechanics and input handling happens
at the same rate even if the framerate drops.

How are Sprites and Groups in spyral different?
###############################################
In spyral, the built in sprites have functionality which is akin to that you
would find in the LayeredDirty group in pygame, without the programmer logic
being necessary. This means that sprites automatically detect when they are
dirty, and rerender themselves accordingly, so you can use the base Spyral
Sprite and Group classes and see a speed boost automatically. Sprites mark
themselves as dirty if you change any of the following attributes: *pos*,
*position*, *image*, *rect*, *blend_flags*, *layer*.

spyrals sprites and groups support layers similar to the LayeredDirty group,
but they use named layers, specified in the camera. This makes it easier to
manage and remember the layers sprites are on.

spyral sprites also support subpixel positioning using the *pos* or *position*
attributes (which are the same) and specifying surface blend flags for pygame
via the *blend_flags* attribute.

spyral groups are given a camera to draw to, whereas LayeredDirty is
traditionally given a surface. spyral's cameras all automatically scale and
translate all drawing to the display so that drawing is done only once, whereas
LayeredDirty may in some situations require you to draw to auxiliary surfaces
first.

How do I use sprite layering?
#############################
Layering in spyral is really easy. When your camera is initialized, you provide
it with a list of layers that you wish to draw on, from bottommost to topmost.
Then, you set the *layer* attribute on all of your sprites to put them into the
proper layers, and spyral will handle the rest.

.. _`OLPC XO`: http://laptop.org
.. _`github site`: https://github.com/rdeaton/spyral

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`