import spyral
import operator
import inspect

class FormFieldMeta(type):
    def __new__(meta, name, bases, dict):
        cls = type.__new__(meta, name, bases, dict)
        cls.fields = sorted(inspect.getmembers(cls, lambda o: isinstance(o, spyral.widgets._WidgetWrapper)), key=lambda i:i[1].creation_counter)
        return cls

class Form(spyral.AggregateSprite):
    __metaclass__ = FormFieldMeta

    def __init__(self, scene):
        """
        
        """
        spyral.AggregateSprite.__init__(self, scene)
        class Fields(object):
            pass
        self._widgets = {}
        self._tab_orders = {}
        self._labels = {}
        self._current_focus = None
        self._name = "Get rid of the name"
        self._mouse_currently_over = None
        self._mouse_down_on = None
        
        scene.register("input.mouse.up", self.handle_mouse_up)
        scene.register("input.mouse.down", self.handle_mouse_down)
        scene.register("input.mouse.motion", self.handle_mouse_motion)
        scene.register("input.keyboard.down.tab", self.handle_tab)
        scene.register("input.keyboard.up.tab", self.handle_tab)
        scene.register("input.keyboard.up", self.handle_key_up)
        scene.register("input.keyboard.down", self.handle_key_down)
        

        fields = self.fields
        self.fields = Fields()
        for name, widget in fields:
            w = widget(self, name)
            setattr(self, name, w)
            self.add_widget(name, w)

    def handle_mouse_up(self, event):
        if self._mouse_down_on is None:
            return False
        self._widgets[self._mouse_down_on].handle_mouse_up(event)
        self._mouse_down_on = None
        
    def handle_mouse_down(self, event):
        for name, widget in self._widgets.iteritems():
            if widget.get_rect().collide_point(event.pos):
                self.focus(name)
                self._mouse_down_on = name
                widget.handle_mouse_down(event)
                return True
        return False
    
    def handle_mouse_motion(self, event):
        if self._mouse_down_on is not None:
            self._widgets[self._mouse_down_on].handle_mouse_motion(event)
        now_hover = None
        for name, widget in self._widgets.iteritems():
            if widget.get_rect().collide_point(event.pos):
                widget.handle_mouse_motion(event)
                now_hover = name
            if now_hover != self._mouse_currently_over:
                if self._mouse_currently_over is not None:
                    widget.handle_mouse_out(event)
                self._mouse_currently_over = now_hover
                if now_hover is not None:
                    widget.handle_mouse_over(event)
                
    def handle_tab(self, event):
        if self._current_focus is None:
            return
        if event.ascii == '\t':
            if event.type == 'KEYDOWN':
                return True
            if event.mod & spyral.mods.shift:
                self.previous()
                return True
            self.next()
            return True
        if self._current_focus is not None:
            self._widgets[self._current_focus].handle_focus(event)
            
    def handle_key_down(self, event):
        if self._current_focus is not None:
            self._widgets[self._current_focus].handle_key_down(event)
    def handle_key_up(self, event):
        if self._current_focus is not None:
            self._widgets[self._current_focus].handle_key_up(event)
            

    def add_widget(self, name, widget, tab_order = None):
        """
        If tab-order is None, it is set to one higher than the highest tab order.
        """
        self._widgets[name] = widget
        if tab_order is None:
            if len(self._tab_orders) > 0:
                tab_order = max(self._tab_orders.itervalues())+1
            else:
                tab_order = 0
            self._tab_orders[name] = tab_order
        self.add_child(widget)
        setattr(self.fields, name, widget)
        
    def add_label(self, name, sprite):
        """
        Adds a non-widget spyral.Sprite as part of the form.
        """
        self._labels[name] = sprite
        self.add_child(sprite)
        setattr(self.fields, name, sprite)
                
    def get_values(self):
        """
        Returns a dictionary of the values for all the fields.
        """
        return dict((name, widget.value) for (name, widget) in self._widgets.iteritems())
        
    def _blur(self, name):
        e = spyral.Event()
        e.name = "blurred"
        self._widgets[name].handle_blur(e)
        e = spyral.Event()
        e.name= "%s_%s_%s" % (self._name, name, "on_blur")
        e.widget = self._widgets[name]
        e.form = self
        #self._manager.send_event(e)

    def focus(self, name = None):
        """
        Sets the focus to be on a specific widget. Focus by default goes
        to the first widget added to the form.
        """
        if name is None:
            if len(self._widgets) == 0:
                return
            name = min(self._tab_orders.iteritems(), key=operator.itemgetter(1))[0]
        if self._current_focus is not None:
            self._blur(self._current_focus)
        self._current_focus = name
        e = spyral.Event()
        e.name = "focused"
        self._widgets[name].handle_focus(e)
        #e = spyral.Event("%s_%s_%s" % (self._name, name, "on_focus"))
        #e.widget = self._widgets[name]
        #e.form = self
        #self._manager.send_event(e)
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
        if len(self._widgets) == 0:
            return
        cur = self._tab_orders[self._current_focus]
        candidates = [(name, order) for (name, order) in self._tab_orders.iteritems() if order > cur]
        if len(candidates) == 0:
            if not wrap:
                return
            name = None
        else:
            name = min(candidates, key=operator.itemgetter(1))[0]
        
        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(name)
        
    def previous(self, wrap = True):
        """
        Focuses the previous widget
        """
        if self._current_focus is None:
            self.focus()
            return
        if len(self._widgets) == 0:
            return
        cur = self._tab_orders[self._current_focus]
        candidates = [(name, order) for (name, order) in self._tab_orders.iteritems() if order < cur]
        if len(candidates) == 0:
            if not wrap:
                return
            name = max(self._tab_orders.iteritems(), key=operator.itemgetter(1))[0]
        else:
            name = max(candidates, key=operator.itemgetter(1))[0]
        
        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(name)
