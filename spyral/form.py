from pygame import key, mouse
import spyral
from bisect import bisect_right
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import operator
import pygame


class TextInputWidget(spyral.AggregateSprite, spyral.FormWidget):
    class _MouseCursor(spyral.Sprite):
        def __init__(self):
            spyral.Sprite.__init__(self)
            
    def __init__(self, value = '', default_value = True, width = None, max_length = None, style = None, validator = None):
        spyral.AggregateSprite.__init__(self)
        spyral.FormWidget.__init__(self)
        self._value = value
        self.default_value = default_value
        self.max_width = max_width
        self.max_length = max_length
        self.style = style
        self.font = self.style.text_input_form
        self.validator = validator
        
        self._cursor_pos = len(value)
        self._selected_pos = 0
        
        self._shift_was_down = False
        self._mouse_is_down = False
        
        self._compute_letter_widths()
        
        self._cursor = spyral.Sprite()
        self._text = spyral.Sprite()
        self.add_child(self._cursor)
        self.add_child(self._text)
            
    def _compute_letter_widths(self, text):
        self._letter_widths = [0]
        running_sum = 0
        for letter in self._value:
            running_sum+= self.font.size(letter)[0]
            self._letter_widths.append(running_sum)
            
    def _insert_text(self, position, char):
        if position == len(self._value):
            new_width= self._letter_widths[len(self._value)] + self.font.size(char)[0]
            self._letter_widths.append(new_width)
            self._value += char
        else:
            self._value = self._value[:position] + char + self._value[position:]
            self._compute_letter_widths()
        self.render()
                
            
    def _compute_cursor_pos(self, mouse_pos):
        x = mouse_pos[0]
        index = bisect_right(self._letter_widths, x)
        if index:
            diff = self._letter_widths[index] - self._letter_widths[index-1]
            if diff < x*2:
                return index-1
            else:
                return index
        
    def _get_value(self, value):
        return self._value
        
    def _set_value(self, value):
        self._cursor_pos = len(value)
        self._value = value
        self._compute_letter_widths()
        self.render()
    
    value = property(_get_value, _set_value)

        
    def render(self):
        # if highlighting
        #   print first segment of non-highlight
        #   print highlight text
        #   print second segment of non-highlight
        # else:
        #   print regular text
        # crop it if it's too far
        self._text.image = self.font.render(self._value)
    
    def handle_event(self, event):
        if event.type == 'KEYDOWN':
            # if key is shift: self._shift_was_down = True
            # if key is up/down/left/right: move cursor_pos
            # else:
            #   self._insert_text(self._cursor_pos, key_pressed)
            pass
        elif event.type == 'KEYUP':
            # if keyup was shift then self._shift_was_down = False
            pass
        elif event.type == 'MOUSEBUTTONUP':
            self._mouse_is_down = False
            if self._shift_was_down:
                pass
        elif event.type == 'MOUSEBUTTONDOWN':
            # set cursor position to mouse position
            if self.default_value: 
                self.value = ''
                self.default_value = False
            self._mouse_is_down = True
        elif event.type == 'MOUSEMOTION':
            if self._mouse_is_down:
                # set selected_pos to mouse_position
                pass

class ButtonWidget(spyral.Sprite, FormWidget):
    def __init__(self, text, style = None):
        pass
        
class ToggleButtonWidget(spyral.Sprite, FormWidget):
    def __init__(self, text, style = None):
        pass

class CheckboxWidget(spyral.Sprite, FormWidget):
    def __init__(self, text, style = None):
            pass

class RadioButton(spyral.Sprite):
    def __init__(self, value, style = None):
        pass
        
class RadioGroup(FormWidget):
    def __init__(self, *buttons):
        pass

class FormStyle(object):
    def __init__(self):    
        self.text_input_font = None
        self.text_input_padding = None
        
        self.text_input_font_color = None
        self.text_input_highlight_color = None
        self.text_input_highlight_background_color = None
        
        self.button_font = None
        self.button_padding = None
        self.button_font_color = None
        
        self.text_input = None
        self.text_input_selected = None
        
        self.button = None
        self.button_selected = None
        self.button_hover = None
        
        self.radio = None
        self.radio_selected = None
        self.radio_hover = None
        
        self.checkbox = None
        self.checkbox_selected = None
        self.checkbox_hover = None
    
    def render_button(self, size, style = 'plain'):
        if style == 'plain':
            image = self.button
        elif style == 'selected':
            image = self.button_selected
        elif style == 'hover':
            image = self.button_hover
            
        return self._render_nine_slice(size, image)
            
    def _render_nine_slice(self, size, image):
        bs = spyral.Vec2D(size)
        bw = size[0]
        bh = size[1]
        ps = image.get_size() / 3
        print ps
        pw = ps[0]
        ph = ps[1]
        surf = image._surf
        image = spyral.Image(size=bs + (1,1)) # Hack: If we don't make it one px large things get cut
        s = image._surf
        # should probably fix the math instead, but it works for now

        topleft = surf.subsurface(pygame.Rect((0,0), ps))
        top = surf.subsurface(pygame.Rect((0,pw), ps))
        topright = surf.subsurface(pygame.Rect((0, 2*pw), ps))
        left = surf.subsurface(pygame.Rect((ph, 0), ps))
        mid = surf.subsurface(pygame.Rect((ph, pw), ps))
        right = surf.subsurface(pygame.Rect((ph, 2*pw), ps))
        bottomleft = surf.subsurface(pygame.Rect((2*ph, 0), ps))
        bottom = surf.subsurface(pygame.Rect((2*ph, pw), ps))
        bottomright = surf.subsurface(pygame.Rect((2*ph, 2*pw), ps))

        # corners
        s.blit(topleft, (0,0))
        s.blit(topright, (bw - pw, 0))
        s.blit(bottomleft, (0, bh - ph))
        s.blit(bottomright, bs - ps)

        # left and right border
        for y in range(ph, bh - ph - ph, ph):
            s.blit(left, (0, y))
            s.blit(right, (bw - pw, y))
        if bh % ph != 0:
            s.blit(left, (0, bh - ph - ph))
            s.blit(right, (bw - pw, bh - ph - ph))
        # top and bottom border
        for x in range(pw, bw - pw - pw, pw):
            s.blit(top, (x, 0))
            s.blit(bottom, (x, bh - ph))
        if bw % pw != 0:
            s.blit(top, (bw - pw - pw, 0))
            s.blit(bottom, (bw - pw - pw, bh - ph))
            
        # center
        for x in range(pw, bw - pw - pw, pw):
            for y in range(ph, bh - ph - ph, ph):
                s.blit(mid, (x, y))

        for x in range(pw, bw - pw - pw, pw):
                s.blit(mid, (x, bh - ph - ph))
        for y in range(ph, bh - ph - ph, ph):
                s.blit(mid, (bw - pw - pw, y))
        s.blit(mid, (bw - pw - pw, bh - ph - ph))
        return image  
    
class Form(spyral.AggregateSprite):
    def __init__(self, name, manager, group, style = None):
        """
        [INSERT DESCRIPTION HERE]
        
        `manager` is an `EventManager` which relevant events will be
        sent to. The event types will be
        "%(form_name)s_%(field_name)_%(event_type)" where event_type is
        from [INSERT LINK TO DOCUMENTATION FOR FORM EVENTS].
        """
        spyral.AggregateSprite.__init__(self, group)
        class Fields(object):
            pass
        self.fields = Fields()
        self._widgets = {}
        self._tab_orders = {}
        self._labels = {}
        self._current_focus = None
        self._name = name
        self._manager = manager
        
        self.image = spyral.Image(size=(1,1))
        
    def handle_event(self, event):
        print event

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
        self._widgets[name].focused = None
        e = spyral.Event("%s_%s_%s" % (self._name, name, "on_blur"))
        e.widget = self._widgets[name]
        e.form = self
        self._manager.send_event(e)

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
        self._widgets[name].focused = True
        e = spyral.Event("%s_%s_%s" % (self._name, name, "on_focus"))
        e.widget = self._widgets[name]
        e.form = self
        self._manager.send_event(e)
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
        print candidates
        if len(candidates) == 0:
            if not wrap:
                return
            name = max(self._tab_orders.iteritems(), key=operator.itemgetter(1))[0]
        else:
            name = max(candidates, key=operator.itemgetter(1))[0]
        
        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(name)
