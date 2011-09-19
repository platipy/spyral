.. Spyral documentation master file, created by
   sphinx-quickstart on Sun Sep 11 19:03:04 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Spyral
======

What is spyral?
---------------
spyral is a 2D game engine/framework built on top of pygame. Its purpose is to rapid prototyping and development of efficient games. It started as a project to allow easy optimization of games for the `OLPC XO`_, and has evolved into a semi-complete but still evolving framework for developing games.

Getting started
---------------
To get spyral, you can clone the git repository, or download packages, from the `github site`_. For now, you can simply include the spyral directory in your project. A setup.py will be included at a later date. For a barebones example, see spyral/examples/skel.py, which provides a skeleton example of a program, complete with comments.	

The API
-------

.. toctree::
   :maxdepth: 2

   director
   scenes


..	Features
	--------
	* Optimized Sprite and Group classes that minimize the amount of drawing.
	* A named layering system, to simplify code by allowing out of order rendering.
	* Automatic scaling to arbitrary resolutions.

..	FAQ
	---

	How are Sprites and Groups in spyral different?
	###############################################
	There are a few differences:
	* sprite.position and sprite.pos can be used for positioning, like sprite.rect is. They automatically reflect changes in one another
	* sprite.special_flags
	

.. _`OLPC XO`: http://laptop.org
.. _`github site`: https://github.com/rdeaton/spyral

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. automodule:: spyral.sprite
	:members:
	