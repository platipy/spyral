"""This module defines the Form class, a subclass of Views that can manage
widgets."""

import spyral
import operator
import inspect

class _FormFieldMeta(type):
    """
    Black magic for wrapping widgets defined as class attributes. See python
    documentation on overriding Python
    `__metaclass__ <http://docs.python.org/2/reference/datamodel.html#customizing-class-creation>`_
    for more information.
    """
    def __new__(meta, name, bases, dict):
        cls = type.__new__(meta, name, bases, dict)
        is_wrapper = lambda obj: isinstance(obj, spyral.widgets._WidgetWrapper)
        cls.fields = sorted(inspect.getmembers(cls, is_wrapper),
                            key=lambda i: i[1].creation_counter)
        return cls

class Form(spyral.View):
    """
    Forms are a subclass of :class:`Views <spyral.View>` that hold a set of
    :ref:`Widgets <api.widgets>`. Forms will manage focus and event delegation between the widgets,
    ensuring that only one widget is active at a given time. Forms are defined 
    using a special class-based syntax::

        class MyForm(spyral.Form):
            name = spyral.widgets.TextInput(100, "Current Name")
            remember_me = spyral.widgets.Checkbox()
            save = spyral.widgets.ToggleButton("Save")

        my_form = MyForm()

    When referencing widgets in this way, the "Widget" part of the widget's name
    is dropped: ``spyral.widgets.ButtonWidget`` becomes ``spyral.widgets.Button``.
    Every widget in a form is accessible as an attribute of the form:

        >>> print my_form.remember_me.value
        "up"

    :param scene: The Scene or View that this Form belongs to.
    :type scene: :class:`Scene <spyral.Scene>` or :class:`View <spyral.View>`.
    """
    __metaclass__ = _FormFieldMeta

    def __init__(self, scene):
        spyral.View.__init__(self, scene)
        class Fields(object):
            pass

        # Maintain a list of all the widget instances
        self._widgets = []
        # Map each widget instance to its tab order
        self._tab_orders = {}
        # The instance of the currently focused widget
        self._current_focus = None
        # The instance of the currently mouse-overed widget
        self._mouse_currently_over = None
        # The instance of the currently mouse-downed widget
        self._mouse_down_on = None

        spyral.event.register("input.mouse.up.left", self._handle_mouse_up,
                              scene=scene)
        spyral.event.register("input.mouse.down.left", self._handle_mouse_down,
                              scene=scene)
        spyral.event.register("input.mouse.motion", self._handle_mouse_motion,
                              scene=scene)
        spyral.event.register("input.keyboard.down.tab", self._handle_tab,
                              scene=scene)
        spyral.event.register("input.keyboard.up.tab", self._handle_tab,
                              scene=scene)
        spyral.event.register("input.keyboard.up", self._handle_key_up,
                              scene=scene)
        spyral.event.register("input.keyboard.down", self._handle_key_down,
                              scene=scene)

        fields = self.fields
        self.fields = Fields()
        for name, widget in fields:
            w = widget(self, name)
            setattr(w, "name", name)
            setattr(self, name, w)
            self.add_widget(name, w)
        self.focus()

    def _handle_mouse_up(self, event):
        """
        Delegate the mouse being released to the widget that is currently being
        clicked.

        :param event: The associated event data.
        :type event: :class:`Event <spyral.Event>`
        """
        if self._mouse_down_on is None:
            return False
        self._mouse_down_on._handle_mouse_up(event)
        self._mouse_down_on = None

    def _handle_mouse_down(self, event):
        """
        Delegate the mouse being clicked down to any widget that it is currently
        hovering over.

        :param event: The associated event data.
        :type event: :class:`Event <spyral.Event>`
        """
        for widget in self._widgets:
            if widget.collide_point(event.pos):
                self.focus(widget)
                self._mouse_down_on = widget
                widget._handle_mouse_down(event)
                return True
        return False

    def _handle_mouse_motion(self, event):
        """
        Delegate the mouse being hovered over any widget that it is currently
        hovering over. If the widget being hovered over is no longer the
        previous widget that was being hovered over, it notifies the old widget
        (mouse out event) and the new widget (mouse over event).

        :param event: The associated event data.
        :type event: :class:`Event <spyral.Event>`
        """
        if self._mouse_down_on is not None:
            self._mouse_down_on._handle_mouse_motion(event)
        now_hover = None
        for widget in self._widgets:
            if widget.collide_point(event.pos):
                widget._handle_mouse_motion(event)
                now_hover = widget
        if now_hover != self._mouse_currently_over:
            if self._mouse_currently_over is not None:
                self._mouse_currently_over._handle_mouse_out(event)
            self._mouse_currently_over = now_hover
            if now_hover is not None:
                now_hover._handle_mouse_over(event)

    def _handle_tab(self, event):
        """
        If this form has focus, advances to the next widget in the tab order.
        Unless the shift key is held, in which case the previous widget is
        focused.

        :param event: The associated event data.
        :type event: :class:`Event <spyral.Event>`
        """
        if self._current_focus is None:
            return
        if event.type == 'down':
            return True
        if event.mod & spyral.mods.shift:
            self.previous()
            return True
        self.next()
        return True

    def _handle_key_down(self, event):
        """
        Notifies the currently focused widget that a key has been pressed.

        :param event: The associated event data.
        :type event: :class:`Event <spyral.Event>`
        """
        if self._current_focus is not None:
            self._current_focus._handle_key_down(event)

    def _handle_key_up(self, event):
        """
        Notifies the currently focused widget that a key has been released.

        :param event: The associated event data.
        :type event: :class:`Event <spyral.Event>`
        """
        if self._current_focus is not None:
            self._current_focus._handle_key_up(event)


    def add_widget(self, name, widget, tab_order=None):
        """
        Adds a new widget to this form. When this method is used to add a Widget
        to a Form, you create the Widget as you would create a normal Sprite. It
        is preferred to use the class-based method instead of this; consider
        carefully whether you can achieve dynamicity through visibility and
        disabling.

        >>> my_widget = spyral.widgets.ButtonWidget(my_form, "save")
        >>> my_form.add_widget("save", my_widget)

        :param str name: A unique name for this widget.
        :param widget: The new Widget.
        :type widget: :ref:`Widget <api.widgets>`
        :param int tab_order: Sets the tab order for this widget explicitly. If
                              tab-order is None, it is set to one higher than
                              the highest tab order.
        """
        if tab_order is None:
            if len(self._tab_orders) > 0:
                tab_order = max(self._tab_orders.itervalues())+1
            else:
                tab_order = 0
            self._tab_orders[widget] = tab_order
        self._widgets.append(widget)
        #self.add_child(widget)
        setattr(self.fields, name, widget)

    def _get_values(self):
        """
        A dictionary of the values for all the fields, mapping the name
        of each widget with the value associated with that widget. Read-only.
        """
        return dict((widget.name, widget.value) for widget in self._widgets)
    
    values = property(_get_values)
    
    def _blur(self, widget):
        """
        Queues an event indicating that a widget has lost focus.

        :param widget: The widget that is losing focus.
        :type widget: :ref:`Widget <api.widgets>`
        """
        e = spyral.Event(name="blurred", widget=widget, form=self)
        self.scene._queue_event("form.%(form_name)s.%(widget)s.blurred" %
                                    {"form_name": self.__class__.__name__,
                                     "widget": widget.name},
                                e)
        widget._handle_blur(e)

    def focus(self, widget=None):
        """
        Sets the focus to be on a specific widget. Focus by default goes
        to the first widget added to the form.

        :param widget: The widget that is gaining focus; if None, then the first
                       widget gains focus.
        :type widget: :ref:`Widget <api.widgets>`
        """
        # By default, we focus on the first widget added to the form
        if widget is None:
            if not self._widgets:
                return
            widget = min(self._tab_orders.iteritems(),
                         key=operator.itemgetter(1))[0]

        # If we'd focused on something before, we blur it
        if self._current_focus is not None:
            self._blur(self._current_focus)

        # We keep track of our newly focused thing
        self._current_focus = widget

        # Make and send the "focused" event
        e = spyral.Event(name="focused", widget=widget, form=self)
        self.scene._queue_event("form.%(form_name)s.%(widget)s.focused" %
                                    {"form_name": self.__class__.__name__,
                                     "widget": widget.name},
                                e)
        widget._handle_focus(e)
        return

    def blur(self):
        """
        Defocuses the entire form.
        """
        if self._current_focus is not None:
            self._blur(self._current_focus)
            self._current_focus = None

    def next(self, wrap=True):
        """
        Focuses on the next widget in tab order.

        :param bool wrap: Whether to continue to the first widget when the end
                          of the tab order is reached.
        """
        if self._current_focus is None:
            self.focus()
            return
        if not self._widgets:
            return
        cur = self._tab_orders[self._current_focus]
        candidates = [(widget, order) for (widget, order)
                                      in self._tab_orders.iteritems()
                                      if order > cur]
        if len(candidates) == 0:
            if not wrap:
                return
            widget = None
        else:
            widget = min(candidates, key=operator.itemgetter(1))[0]

        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(widget)

    def previous(self, wrap=True):
        """
        Focuses the previous widget in tab order.

        :param bool wrap: Whether to continue to the last widget when the first
                          of the tab order is reached.
        """
        if self._current_focus is None:
            self.focus()
            return
        if not self._widgets:
            return
        cur = self._tab_orders[self._current_focus]
        candidates = [(widget, order) for (widget, order)
                                      in self._tab_orders.iteritems()
                                      if order < cur]
        if len(candidates) == 0:
            if not wrap:
                return
            widget = max(self._tab_orders.iteritems(),
                         key=operator.itemgetter(1))[0]
        else:
            widget = max(candidates, key=operator.itemgetter(1))[0]

        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(widget)
