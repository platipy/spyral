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

Examples
--------

[test](examples/skel.py)

* [**skel.py**](examples/skel.py) : A simple starting point for a new Spyral-based program, with a custom Scene. If you're not developing for the XO, this is a good starting point.
* [**view.py**](examples/view.py>) : A walkthrough demonstration of the functionality of Views, which allow Sprites to be manipulated in groups. Use ``Space`` to walk through the steps.
* [**minimal.py**](examples/minimal.py>) : The simplest possible Spyral program with no custom functionality. Not recommended, simply here to show off the simplicity.

Known Bugs
----------

Check out the `tracked issues on github <https://github.com/platipy/spyral/issues?state=open>`_ or the `Open Issues <http://platipy.readthedocs.org/en/latest/openproblems.html>`_ on Platipy for a listing of the things still needed.

* Not compliant with 3.x (XO laptops use Python 2.5, so we don't target 3.x).
