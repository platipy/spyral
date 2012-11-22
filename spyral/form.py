import spyral
from bisect import bisect_right
import operator
import pygame


class TextInputWidget(spyral.AggregateSprite):
    class _MouseCursor(spyral.Sprite):
        def __init__(self):
            spyral.Sprite.__init__(self)
            
    def __init__(self, value = '', width = None, default_value = True, max_length = None, style = None, validator = None):
        spyral.AggregateSprite.__init__(self)
    
        self._cursor = spyral.Sprite()
        self.add_child(self._cursor)
        
        self._focused = False
        self._cursor.visible = False
        self._selection_pos = 0
        self._selecting = False
        self._shift_was_down = False
        self._mouse_is_down = False
        
        self._cursor_blink_interval = 0.5
        self._cursor_time = 0.
        
        self.default_value = default_value
        if width is None:
            width = 200
        self._view_x = 0
        self.box_width = width
        self.max_length = max_length
        self.style = style
        if style is not None and style.text_input_font is not None:
            self.font = style.text_input_font
        else:
            self.font = spyral.Font(None, 32, (255,255,255))
            self.style.text_input_highlight_color= (255, 0, 0)
        self._box_height = self.font.get_linesize()

        self._cursor.image = spyral.Image(size=(2,self._box_height))
        self._cursor.image.fill((255, 255, 255))

        self.validator = validator
        self.value = value
        
            
    def _compute_letter_widths(self):
        self._letter_widths = []
        running_sum = 0
        for index in range(len(self._value)+1):
            running_sum= self.font.get_size(self._value[:index])[0]
            self._letter_widths.append(running_sum)
            
    def _insert_char(self, position, char):
        if position == len(self._value):
            self._value += char
            new_width= self.font.get_size(self._value)[0]
            self._letter_widths.append(new_width)
        else:
            self._value = self._value[:position] + char + self._value[position:]
            self._compute_letter_widths()
        self._render_text()
        
    def _remove_char(self, position, end = None):
        if end is None:
            end = position+1
        if position == len(self._value): 
            pass
        else:
            self._value = self._value[:position]+self._value[end:]
            self._compute_letter_widths()
        self._render_text()
        self._render_cursor()
                
            
    def _compute_cursor_pos(self, mouse_pos):
        mouse_pos = self.group.camera.world_to_local(mouse_pos)
        x = mouse_pos[0] + self._view_x - self.x
        index = bisect_right(self._letter_widths, x)
        if index >= len(self._value):
            return len(self._value)
        elif index:
            diff = self._letter_widths[index] - self._letter_widths[index-1]
            x -= self._letter_widths[index-1]
            if diff > x*2:
                return index-1
            else:
                return index
        else:
            return 0
        
    def _get_value(self):
        return self._value
        
    def _set_value(self, value):
        self._value = value
        self._compute_letter_widths()
        self._cursor_pos = 0#len(value)
        self._render_text()
        self._render_cursor()
    
    def _get_cursor_pos(self):
        return self._cursor_pos
    
    def _set_cursor_pos(self, position):
        self._cursor_pos = position
        self._move_rendered_text()
        self._render_cursor()

    value = property(_get_value, _set_value)
    cursor_pos = property(_get_cursor_pos, _set_cursor_pos)
        
    def _render_text(self):
        if self._selecting and (self._cursor_pos != self._selection_pos):
            start, end = sorted((self._cursor_pos, self._selection_pos))
            
            pre = self.font.render(self._value[:start])
            highlight = self.font.render(self._value[start:end], color=self.style.text_input_highlight_color)
            post = self.font.render(self._value[end:])
            
            pre_missed = self.font.get_size(self._value[:end])[0] - pre.get_width() - highlight.get_width() + 1
            if self._value[:start]:
                post_missed = self.font.get_size(self._value)[0] - post.get_width() - pre.get_width() - highlight.get_width() - 1
                self._rendered_text = spyral.Image.from_sequence((pre, highlight, post), 'right', [pre_missed, post_missed])
            else:
                post_missed = self.font.get_size(self._value)[0] - (post.get_width() + highlight.get_width())
                self._rendered_text = spyral.Image.from_sequence((highlight, post), 'right', [post_missed])

        else:
            self._rendered_text = self.font.render(self._value)
        self._move_rendered_text()
        
    def _move_rendered_text(self):
        width = self._letter_widths[self.cursor_pos]
        max_width = self._letter_widths[len(self._value)]
        cursor_width = 2
        x = width - self._view_x
        if x < 0: 
            self._view_x += x
        if x+cursor_width > self.box_width:
            self._view_x += x + cursor_width - self.box_width
        if self._view_x+self.box_width> max_width and max_width > self.box_width:
            self._view_x = max_width - self.box_width
        image = self._rendered_text.copy()
        image.crop((self._view_x, 0), 
                   (self.box_width, self._box_height))
        self.image = image
        
    def _render_cursor(self):
        self._cursor.x = min(max(self._letter_widths[self.cursor_pos] - self._view_x, 0), self.box_width)
        self._cursor.y = 0
        
    _non_insertable_keys =(spyral.keys.up, spyral.keys.down, 
                           spyral.keys.left, spyral.keys.right,
                           spyral.keys.home, spyral.keys.end, 
                           spyral.keys.pageup, spyral.keys.pagedown,
                           spyral.keys.numlock, spyral.keys.capslock,
                           spyral.keys.scrollock, spyral.keys.rctrl,
                           spyral.keys.rshift, spyral.keys.lshift,
                           spyral.keys.lctrl, spyral.keys.rmeta,
                           spyral.keys.ralt, spyral.keys.lalt,
                           spyral.keys.lmeta, spyral.keys.lsuper, 
                           spyral.keys.rsuper, spyral.keys.mode)
    _non_skippable_keys = (' ', '.', '?', '!', '@', '#', '$',
                           '%', '^', '&', '*', '(', ')', '+',
                           '=', '{', '}', '[', ']', ';', ':',
                           '<', '>', ',', '/', '\\', '|', '"',
                           "'", '~', '`')
    _non_printable_keys = ('\t', '')+_non_insertable_keys
                           
    def _find_next_word(self, text, start=0, end=None):
        if end is None:
            end = len(text)
        for index, letter in enumerate(text[start:end]):
            if letter in self._non_skippable_keys:
                return start+(index+1)
        return end

    def _find_previous_word(self, text, start=0, end=None):
        if end is None:
            end = len(text)
        for index, letter in enumerate(reversed(text[start:end])):
            if letter in self._non_skippable_keys:
                return end-(index+1)
        return start
        
    def _delete(self, by_word = False):
        if self._selecting:
            start, end = sorted((self.cursor_pos, self._selection_pos))
            self.cursor_pos = start
            self._remove_char(start, end)
        elif by_word:
            start = self.cursor_pos
            end = self._find_next_word(self.value, self.cursor_pos, len(self._value))
            self._remove_char(start, end)
        else:
            self._remove_char(self.cursor_pos)
        
    def _backspace(self, by_word = False):
        if self._selecting:
            start, end = sorted((self.cursor_pos, self._selection_pos))
            self.cursor_pos = start
            self._remove_char(start, end)
        elif not self._cursor_pos:
            pass
        elif by_word:
            start = self._find_previous_word(self.value, 0, self.cursor_pos-1)
            end = self.cursor_pos
            self.cursor_pos= start
            self._remove_char(start, end)
        elif self._cursor_pos:
            self.cursor_pos-= 1
            self._remove_char(self.cursor_pos)
    
    def _move_cursor_left(self, by_word = False):
        if by_word:
            self.cursor_pos = self._find_previous_word(self.value, 0, self.cursor_pos)
        else:
            self.cursor_pos= max(self.cursor_pos-1, 0)
    
    def _move_cursor_right(self, by_word = False):
        if by_word:
            self.cursor_pos = self._find_next_word(self.value, self.cursor_pos, len(self.value))
        else:
            self.cursor_pos= min(self.cursor_pos+1, len(self.value))
            
    def update(self, dt):
        if self._focused:
            self._cursor_time += dt
            if self._cursor_time > self._cursor_blink_interval:
                self._cursor_time -= self._cursor_blink_interval
                self._cursor.visible = not self._cursor.visible
    
    def _stop_blinking(self):
        self._cursor_time = 0
        self._cursor.visible = True
    
    def handle_event(self, event):
        if event.type == 'KEYDOWN':
            key = event.key
            mods = event.mod
            shift_is_down= (mods & spyral.mods.shift) or (key in (spyral.keys.lshift, spyral.keys.rshift))
            shift_clicked = not self._shift_was_down and shift_is_down
            self._shift_was_down = shift_is_down
            
            if shift_clicked or (shift_is_down and not 
                                 self._selecting and 
                                 key in TextInputWidget._non_insertable_keys):
                self._selection_pos = self.cursor_pos
                self._selecting = True
                
            if key == spyral.keys.left:
                self._move_cursor_left(mods & spyral.mods.ctrl)
            elif key == spyral.keys.right: 
                self._move_cursor_right(mods & spyral.mods.ctrl)
            elif key == spyral.keys.home:
                self.cursor_pos = 0
            elif key == spyral.keys.end:
                self.cursor_pos = len(self.value)
            elif key == spyral.keys.delete:
                self._delete(mods & spyral.mods.ctrl)
            elif key == spyral.keys.backspace:
                self._backspace(mods & spyral.mods.ctrl)
            else:
                if key not in TextInputWidget._non_printable_keys:
                    if self._selecting:
                        self._delete()
                    self._insert_char(self.cursor_pos, event.unicode)
                    self.cursor_pos+= 1
                    
            if not shift_is_down or (shift_is_down and key not in TextInputWidget._non_insertable_keys):
                self._selecting = False
                self._render_text()
                print "RESET", shift_is_down
            if self._selecting:
                self._render_text()
                
        elif event.type == 'MOUSEBUTTONUP':
            self.cursor_pos = self._compute_cursor_pos(event.pos)
        elif event.type == 'MOUSEBUTTONDOWN':
            if not self._selecting:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self._selection_pos = self.cursor_pos
                    self._selecting = True
                else:
                    self._selecting = True
                    self._selection_pos = self.cursor_pos
            elif not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                self._selecting = False
            self.cursor_pos = self._compute_cursor_pos(event.pos)
            self._stop_blinking()
            # set cursor position to mouse position
            if self.default_value: 
                self.value = ''
                self.default_value = False
            self._render_text()
        elif event.type == 'MOUSEMOTION':
            if not self._selecting:
                self._selecting = True
                self._selection_pos = self.cursor_pos
                print "SET"
            self.cursor_pos = self._compute_cursor_pos(event.pos)
            self._render_text()
            self._stop_blinking()
        elif event.type == 'focused':
            self._focused = True
        elif event.type == 'blurred':
            self._focused = False
            self._cursor.visible = False


class ButtonWidget(spyral.Sprite):
    def __init__(self, text, width = None, style = None):
        spyral.Sprite.__init__(self)
        style = spyral.FormStyle()
        
        style.button = spyral.Image("game/res/input.normal.png")
        style.button_selected = style.button
        
        
        self.image = style.render_button((200, 48))

        pass
    
    def handle_event(self, event):
        pass
        
class ToggleButtonWidget(spyral.Sprite):
    def __init__(self, text, style = None):
        pass

class CheckboxWidget(spyral.Sprite):
    def __init__(self, text, style = None):
            pass

class RadioButton(spyral.Sprite):
    def __init__(self, value, style = None):
        pass
        
class RadioGroup(object):
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
        pw = ps[0]
        ph = ps[1]
        surf = image._surf
        image = spyral.Image(size=bs + (1,1)) # Hack: If we don't make it one px large things get cut
        s = image._surf
        # should probably fix the math instead, but it works for now

        topleft = surf.subsurface(pygame.Rect((0,0), ps))
        left = surf.subsurface(pygame.Rect((0,ph), ps))
        bottomleft = surf.subsurface(pygame.Rect((0, 2*pw), ps))
        top = surf.subsurface(pygame.Rect((pw, 0), ps))
        mid = surf.subsurface(pygame.Rect((pw, ph), ps))
        bottom = surf.subsurface(pygame.Rect((pw, 2*ph), ps))
        topright = surf.subsurface(pygame.Rect((2*pw, 0), ps))
        right = surf.subsurface(pygame.Rect((2*ph, pw), ps))
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
        s.blit(left, (0, bh - ph - ph))
        s.blit(right, (bw - pw, bh - ph - ph))
        # top and bottom border
        for x in range(pw, bw - pw - pw, pw):
            s.blit(top, (x, 0))
            s.blit(bottom, (x, bh - ph))
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
    def __init__(self, name, manager, style = None):
        """
        [INSERT DESCRIPTION HERE]
        
        `manager` is an `EventManager` which relevant events will be
        sent to. The event types will be
        "%(form_name)s_%(field_name)_%(event_type)" where event_type is
        from [INSERT LINK TO DOCUMENTATION FOR FORM EVENTS].
        """
        spyral.AggregateSprite.__init__(self)
        class Fields(object):
            pass
        self.fields = Fields()
        self._widgets = {}
        self._tab_orders = {}
        self._labels = {}
        self._current_focus = None
        self._name = name
        self._manager = manager        
        self._mouse_currently_over = None
        self._mouse_down_on = None
        
    def handle_event(self, event):
        if event.type == 'MOUSEBUTTONDOWN':
            for name, widget in self._widgets.iteritems():
                if widget.get_rect().collide_point(widget.group.camera.world_to_local(event.pos)):
                    self.focus(name)
                    self._mouse_down_on = name
                    widget.handle_event(event)
                    return True
            return False
        if event.type == 'MOUSEBUTTONUP':
            if self._mouse_down_on is None:
                return False
            self._widgets[self._mouse_down_on].handle_event(event)
            self._mouse_down_on = None
        if event.type == 'MOUSEMOTION':
            if self._mouse_down_on is not None:
                self._widgets[self._mouse_down_on].handle_event(event)
            now_hover = None
            for name, widget in self._widgets.iteritems():
                if widget.get_rect().collide_point(event.pos):
                    now_hover = name
            if now_hover != self._mouse_currently_over:
                if self._mouse_currently_over is not None:
                    e = spyral.Event("%s_%s" % (self._name, "on_mouse_out"))
                    e.form = self
                    e.widget = self._widgets[self._mouse_currently_over]
                    e.widget_name = self._mouse_currently_over
                    self._manager.send_event(e)
                self._mouse_currently_over = now_hover
                if now_hover is not None:
                    e = spyral.Event("%s_%s" % (self._name, "on_mouse_over"))
                    e.form = self
                    e.widget = self._widgets[self._mouse_currently_over]
                    e.widget_name = self._mouse_currently_over
                    self._manager.send_event(e)
            return
        if event.type == 'KEYDOWN' or event.type == 'KEYUP':
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
                self._widgets[self._current_focus].handle_event(event)
            

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
        e = spyral.Event("blurred")
        self._widgets[name].handle_event(e)
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
        e = spyral.Event("focused")
        self._widgets[name].handle_event(e)
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
        if len(candidates) == 0:
            if not wrap:
                return
            name = max(self._tab_orders.iteritems(), key=operator.itemgetter(1))[0]
        else:
            name = max(candidates, key=operator.itemgetter(1))[0]
        
        self._blur(self._current_focus)
        self._current_focus = None
        self.focus(name)
