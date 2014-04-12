======
Spyral
======

Spyral is a library/engine for developing 2D games in Python 2.X, with a focus in rapid development and clean design. Any system that runs Pygame should be able to run Spyral. Instead of ``import pygame``, you'll just use ``import spyral`` instead.

Pre-requisites
--------------

* `Pygame <http://www.pygame.org/download.shtml>`_
* `Parsley <https://pypi.python.org/pypi/Parsley>`_
* `Greenlets <https://pypi.python.org/pypi/greenlet>`_ (optional, if you want to use the powerful Actors feature for multi-processing)

Using Spyral on the XO Laptop
-----------------------------

Spyral was specifically designed for developing XO laptop games. Spyral's main source of documentation can be found at the Platipy project, which documents Spyral in the context of a university course for which it was developed. `Visit the Platipy Project <http://platipy.org>`_

Using Spyral Elsewhere
----------------------

A simple `Skeleton <https://github.com/platipy/spyral/blob/master/examples/skel.py>`_ , along with many other `examples <https://github.com/platipy/spyral/tree/master/examples>`_ are available.

Known Bugs
----------

Check out the `tracked issues on github <https://github.com/platipy/spyral/issues?state=open>`_ or the `Open Issues <http://platipy.readthedocs.org/en/latest/openproblems.html>`_ on Platipy for a listing of the things still needed.

* Not compliant with 3.x (XO laptops use Python 2.5, so we don't target 3.x).
