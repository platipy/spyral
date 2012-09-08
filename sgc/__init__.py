"""
All widgets are imported into sgc namespace. This means you can access
widgets in sgc namespace, such as ``sgc.Button``.

Module Packages:
  :py:mod:`widgets<sgc.widgets>`: All the widgets available for use in this toolkit.

Modules:
  :py:mod:`locals<sgc.locals>`: Constants to be imported into the local namespace for convenience.
  :py:mod:`surface<sgc.surface>`: Extended pygame.surface classes.

"""
__version__ = "0.1.9"

#import spyral.sgc.surface
import spyral.sgc.locals
import spyral.sgc.widgets
from spyral.sgc.widgets._locals import Font, update, event

# Import widgets
from widgets.base_widget import Simple
from widgets.boxes import VBox, HBox
from widgets.button import Button
from widgets.container import Container
from widgets.composite.dialogs import DialogSaveQuit
from widgets.dialog import Dialog
from widgets.fps_counter import FPSCounter
from widgets.input_box import InputBox
from widgets.label import Label
from widgets.radio_button import Radio
from widgets.scroll_box import ScrollBox
from widgets.settings import Keys
from widgets.switch import Switch

# Import Menu last, so it can import the other widgets from here.
from widgets.menu import Menu
