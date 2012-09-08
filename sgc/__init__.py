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
from spyral.sgc.widgets.base_widget import Simple
#from spyral.sgc.widgets.boxes import VBox, HBox
from spyral.sgc.widgets.button import Button
#from spyral.sgc.widgets.container import Container
#from spyral.sgc.widgets.composite.dialogs import DialogSaveQuit
#from spyral.sgc.widgets.dialog import Dialog
#from spyral.sgc.widgets.fps_counter import FPSCounter
#from spyral.sgc.widgets.input_box import InputBox
#from spyral.sgc.widgets.label import Label
#from spyral.sgc.widgets.radio_button import Radio
#from spyral.sgc.widgets.scroll_box import ScrollBox
#from spyral.sgc.widgets.settings import Keys
#from spyral.sgc.widgets.switch import Switch

# Import Menu last, so it can import the other widgets from here.
#from spyral.sgc.widgets.menu import Menu
