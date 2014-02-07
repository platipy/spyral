import spyral
import operator
import inspect

class _FormFieldMeta(type):
    def __new__(meta, name, bases, dict):
        cls = type.__new__(meta, name, bases, dict)
        cls.fields = sorted(inspect.getmembers(cls,
                                               lambda o: isinstance(o, spyral.widgets._WidgetWrapper)),
                            key=lambda i:i[1].creation_counter)
        return cls

class Form(spyral.View):
    """
    Forms are a subclass of :class:`Views <spyral.View>` that hold a set of
    widgets. Forms will manage focus and event delegation between the widgets,
    ensuring that only one widget is active at a given time.
    
    Forms are defined using a class-based syntax::
    
        class MyForm(spyral.Form):
            name = spyral.widgets.TextInput(100, "Current Name")
            remember_me = spyral.widgets.Checkbox()
            save = spyral.widgets.ToggleButton("Save")
            
        my_form = MyForm()
    
    Every widget in a form is accessible as an attribute of the form:
    
        >>> print my_form.name.value
        "Current Name"
    
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
        # Maintain a mapping of each label from its name
        self._labels = {}
        # The instance of the currently focused widget
        self._current_focus = None
        # The instance of the currently mouse-overed widget
        self._mouse_currently_over = None
        # The instance of the currently mouse-downed widget
        self._mouse_down_on = None

        self.scene.register("input.mouse.up", self._handle_mouse_up)
        self.scene.register("input.mouse.down", self._handle_mouse_down)
        self.scene.register("input.mouse.motion", self._handle_mouse_motion)
        self.scene.register("input.keyboard.down.tab", self._handle_tab)
        self.scene.register("input.keyboard.up.tab", self._handle_tab)
        self.scene.register("input.keyboard.up", self._handle_key_up)
        self.scene.register("input.keyboard.down", self._handle_key_down)

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
        
        """
        if self._mouse_down_on is None:
            return False
        self._mouse_down_on._handle_mouse_up(event)
        self._mouse_down_on = None

    def _handle_mouse_down(self, event):
        for widget in self._widgets:
            if widget.collide_point(event.pos):
                self.focus(widget)
                self._mouse_down_on = widget
                widget._handle_mouse_down(event)
                return True
        return False

    def _handle_mouse_motion(self, event):
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
        if self._current_focus is not None:
            self._current_focus._handle_key_down(event)
    def _handle_key_up(self, event):
        if self._current_focus is not None:
            self._current_focus._handle_key_up(event)


    def add_widget(self, name, widget, tab_order = None):
        """
        If tab-order is None, it is set to one higher than the highest tab order.
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

    def add_label(self, name, sprite):
        """
        Adds a non-widget spyral.Sprite as part of the form.
        """
        self._labels[name] = sprite
        #self.add_child(sprite)
        setattr(self.fields, name, sprite)

    def get_values(self):
        """
        Returns a dictionary of the values for all the fields.
        """
        return dict((widget.name, widget.value) for widget in self._widgets)

    def _blur(self, widget):
        e = spyral.Event(name="blurred", widget=widget, form=self)
        self.scene._queue_event("form.%(form_name)s.%(widget)s.blurred" %
                                    {"form_name": self.__class__.__name__,
                                     "widget": widget.name},
                                e)
        widget._handle_blur(e)

    def focus(self, widget = None):
        """
        Sets the focus to be on a specific widget. Focus by default goes
        to the first widget added to the form.
        """
        # By default, we focus on the first widget added to the form
        if widget is None:
            if not self._widgets:
                return
            widget = min(self._tab_orders.iteritems(), key=operator.itemgetter(1))[0]

        # If we'd focused on something before, we blur it
        if self._current_focus is not None:
            self._blur(self._current_focus)

        # We keep track of our newly focused thing
        self._current_focus = widget

        # Make and send the "focused" event
        e = spyral.Event(name="focused", widget=widget, form = self)
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

    def next(self, wrap = True):
        """
        Focuses the next widget
        """
        if self._current_focus is None:
            self.focus()
            return
        if not self._widgets:
            return
        cur = self._tab_orders[self._current_focus]
        candidates = [(widget, order) for (widget, order) in self._tab_orders.iteritems() if order > cur]
        if len(candidates) == 0:
            if not wrap:
                return
            widget = None
        else:
            widget = min(candidates, key=operator.itemgetter(1))[0]

        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(widget)

    def previous(self, wrap = True):
        """
        Focuses the previous widget
        """
        if self._current_focus is None:
            self.focus()
            return
        if not self._widgets:
            return
        cur = self._tab_orders[self._current_focus]
        candidates = [(widget, order) for (widget, order) in self._tab_orders.iteritems() if order < cur]
        if len(candidates) == 0:
            if not wrap:
                return
            widget = max(self._tab_orders.iteritems(), key=operator.itemgetter(1))[0]
        else:
            widget = max(candidates, key=operator.itemgetter(1))[0]

        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(widget)
