import spyral
from bisect import bisect_right
import operator
import pygame
import math
import string

            
class MultiStateWidget(spyral.AggregateSprite):
    def __init__(self, scene, states):
        self._states = states
        self._state = self._states[0]
        
        spyral.AggregateSprite.__init__(self, scene)
        
        self._images = {}
        self._content_size = (0, 0)
        
    def _render_images(self):
        for state in self._states:
            if self._nine_slice:
                size = spyral.Vec2D(self._padding, self._padding) + self._content_size
                nine_slice_image = spyral.Image(self._image_locations[state])
                self._images[state] = spyral.Image.render_nine_slice(nine_slice_image, size)
            else:
                self._images[state] = spyral.Image(self._image_locations[state])
        self.image = self._images[self._state]
        self._on_size_change()
    
    def _set_state(self, state):
        self._state = state
        self.image = self._images[state]
        
    def _get_state(self):
        return self._state
        
    def _set_nine_slice(self, nine_slice):
        self._nine_slice = nine_slice
        self._render_images()
        
    def _get_nine_slice(self):
        return self._nine_slice
        
    def _set_padding(self, padding):
        self._padding = padding
        self._render_images()
        
    def _get_padding(self):
        return self._padding
        
    def _set_content_size(self, size):
        self._content_size = size
        self._render_images()
        
    def _get_content_size(self):
        return self._get_content_size
        
    def _on_size_change(self):
        pass
    
    nine_slice = property(_get_nine_slice, _set_nine_slice)
    state = property(_get_state, _set_state)
    content_size = property(_get_content_size, _set_content_size)
    
    def __stylize__(self, properties):
        self._padding = properties.pop('padding', 4)
        self._nine_slice = properties.pop('nine_slice', False)
        self._image_locations = {}
        for state in self._states:
            # TODO: try/catch to ensure that the property is set?
            self._image_locations[state] = properties.pop('image_%s' % (state,))
        spyral.AggregateSprite.__stylize__(self, properties)
        
class ButtonWidget(MultiStateWidget):
    """
    A ButtonWidget is a simple button that can be pressed. It can have some
    text. If you don't specify an explicit width, then it will be sized
    according to it's text.
    """
    def __init__(self, scene, text = "Okay"):
        spyral.MultiStateWidget.__init__(self, scene, ['up', 'down', 'focused', 'hovered'])
        
        self._text_sprite = spyral.Sprite(scene)
        self.add_child(self._text_sprite)

        self.text = text
        
    def _get_text(self):
        return self._text
    
    def _set_text(self, text):
        self._text = text
        self._text_sprite.image = self.font.render(self._text)
        self._content_size = self._text_sprite.image.get_size()
        self._render_images()
        
    def _on_size_change(self):
        self._text_sprite.pos = spyral.Vec2D(self._padding, self._padding) / 2
                
    text = property(_get_text, _set_text)
    
    def handle_mouse_up(self, event):
        self.state = 'up'
        
    def handle_mouse_down(self, event):
        self.state = 'down'
        
    def handle_mouse_motion(self, event):
        self.state = 'hovered'
        
    def handle_focus(self, event):
        self.state = 'focused'
    
    def handle_blur(self, event):
        self.state = 'up'
        
    def __stylize__(self, properties):
        self.font = spyral.Font(*properties.pop('font'))
        self._text = properties.pop('text', "Button")

        spyral.MultiStateWidget.__stylize__(self, properties)
    
        
class ToggleButtonWidget(spyral.Sprite):
    """
    A ToggleButtonWidget is similar to a Button, except that it will stay down
    after it's been clicked, until it is clicked again.
    """
    def __init__(self, scene, text = "Okay"):
        spyral.Sprite.__init__(self, scene)

class CheckboxWidget(spyral.Sprite):
    """
    A CheckboxWidget is similar to a ToggleButtonWidget, only it doesn't have text.
    """
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)

class RadioButtonWidget(spyral.Sprite):
    """
    A RadioButton is similar to a CheckBox, except it is to be placed into a
    RadioGroup, which will ensure that only one RadioButton in it's group is
    selected at a time.
    """
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        
class RadioGroup(object):
    """
    Only one RadioButton in a RadioGroup can be selected at a time.
    """
    def __init__(self, buttons, selected = None):
        spyral.Sprite.__init__(self, scene)
    
class Form(spyral.AggregateSprite):
    def __init__(self, scene, name):
        """
        
        """
        spyral.AggregateSprite.__init__(self, scene)
        class Fields(object):
            pass
        self.fields = Fields()
        self._widgets = {}
        self._tab_orders = {}
        self._labels = {}
        self._current_focus = None
        self._name = name
        self._mouse_currently_over = None
        self._mouse_down_on = None
        
        scene.register("input.mouse.up", self.handle_mouse_up)
        scene.register("input.mouse.down", self.handle_mouse_down)
        scene.register("input.mouse.motion", self.handle_mouse_motion)
        
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
        
    def handle_event(self, event):
        if event.type == 'down':
            for name, widget in self._widgets.iteritems():
                if widget.get_rect().collide_point(event.pos):
                    self.focus(name)
                    self._mouse_down_on = name
                    widget.handle_event(event)
                    return True
            return False
        if event.type == 'up':
            if self._mouse_down_on is None:
                return False
            self._widgets[self._mouse_down_on].handle_event(event)
            self._mouse_down_on = None
        if event.type == 'motion':
            
            if self._mouse_down_on is not None:
                self._widgets[self._mouse_down_on].handle_event(event)
            now_hover = None
            for name, widget in self._widgets.iteritems():
                if widget.get_rect().collide_point(event.pos):
                    widget.handle_event(event)
                    #now_hover = name
            #if now_hover != self._mouse_currently_over:
                #if self._mouse_currently_over is not None:
                #    e = spyral.Event("%s_%s" % (self._name, "on_mouse_out"))
                #    e.form = self
                #    e.widget = self._widgets[self._mouse_currently_over]
                #    e.widget_name = self._mouse_currently_over
                    #self._manager.send_event(e)
                #self._mouse_currently_over = now_hover
                #if now_hover is not None:
                 #   e = spyral.Event("%s_%s" % (self._name, "on_mouse_over"))
                 #   e.form = self
                 #   e.widget = self._widgets[self._mouse_currently_over]
                 #   e.widget_name = self._mouse_currently_over
                    #self._manager.send_event(e)
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


class TextInputWidget(spyral.AggregateSprite):            
    def __init__(self, scene, width, value = '', default_value = True, max_length = None, validator = None):
        spyral.AggregateSprite.__init__(self, scene)
        
        if style is None:
            style = get_default_style()
        self._style = style
    
        self._padding = padding = int(style.get("TextInput", "padding"))
        self.child_anchor = (padding, padding)
        self._cursor = spyral.Sprite(camera)
        self._cursor.anchor = (padding, padding)
        self._text = spyral.Sprite(camera)
        self._text.pos = (padding, padding)
        self.add_child(self._cursor)
        self.add_child(self._text)
        
        self._focused = False
        self._cursor.visible = False
        self._selection_pos = 0
        self._selecting = False
        self._shift_was_down = False
        self._mouse_is_down = False
        
        self._cursor_time = 0.
        self._cursor_blink_interval = float(self._style.get("TextInput", "cursor_blink_interval"))
        
        self.default_value = default_value
        self._default_value_permanant = default_value

        self._view_x = 0
        self.box_width = width - 2*padding
        self.max_length = max_length
        self.style = style
        
        self.font = spyral.Font(style.get("TextInput", "font"),
                                int(style.get("TextInput", "font_size")),
                                style.get("TextInput", "font_color"))

        self._box_height = int(math.ceil(self.font.get_linesize()))

        self._cursor.image = spyral.Image(size=(2,self._box_height))
        self._cursor.image.fill(style.get("TextInput", "font_color"))

        if validator is None:
            self.validator = string.printable
        else:
            self.validator = validator
        
        if max_length is not None and len(value) < max_length:
            value = value[:max_length]
        self.value = value
        
        self._image_plain = style.render_nine_slice((width, self._box_height + 2*padding), style.get_image("TextInput", "background"))
        self._image_focused = style.render_nine_slice((width, self._box_height + 2*padding), style.get_image("TextInput", "background_focused"))
        self.image = self._image_plain
        
            
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
        mouse_pos = self.camera.world_to_local(mouse_pos)
        x = mouse_pos[0] + self._view_x - self.x - self._padding
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
    def _stop_blinking(self):
        self._cursor_time = 0
        self._cursor.visible = True
        
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
        
    def validate(self, char):
        valid_length = self.max_length is None or (self.max_length is not None and len(self._value) < self.max_length)
        valid_char = str(char) in self.validator
        return valid_length and valid_char

    value = property(_get_value, _set_value)
    cursor_pos = property(_get_cursor_pos, _set_cursor_pos)
        
    def _render_text(self):
        if self._selecting and (self._cursor_pos != self._selection_pos):
            start, end = sorted((self._cursor_pos, self._selection_pos))
            
            pre = self.font.render(self._value[:start])
            highlight = self.font.render(self._value[start:end], color=self._style.get("TextInput", "font_color_highlight"))
            post = self.font.render(self._value[end:])
            
            pre_missed = self.font.get_size(self._value[:end])[0] - pre.get_width() - highlight.get_width() + 1
            if self._value[:start]:
                post_missed = self.font.get_size(self._value)[0] - post.get_width() - pre.get_width() - highlight.get_width() - 1
                self._rendered_text = spyral.Image.from_sequence((pre, highlight, post), 'right', [pre_missed, post_missed])
            else:
                post_missed = self.font.get_size(self._value)[0] - post.get_width() - highlight.get_width()
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
        self._text.image = image
        # if highlighting
        #   print first segment of non-highlight
        #   print highlight text
        #   print second segment of non-highlight
        # else:
        #   print regular text
        
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
                    if self.validate(event.unicode):
                        self._insert_char(self.cursor_pos, event.unicode)
                        self.cursor_pos+= 1
                    
            if not shift_is_down or (shift_is_down and key not in TextInputWidget._non_insertable_keys):
                self._selecting = False
                self._render_text()
            if self._selecting:
                self._render_text()
                
        elif event.type == 'MOUSEBUTTONUP':
            self.cursor_pos = self._compute_cursor_pos(event.pos)
        elif event.type == 'MOUSEBUTTONDOWN':
            if not self._selecting:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self._selection_pos = self.cursor_pos
                    self._selecting = True
            elif not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                self._selecting = False
            self.cursor_pos = self._compute_cursor_pos(event.pos)
            # set cursor position to mouse position
            if self.default_value: 
                self.value = ''
                self.default_value = False
            self._render_text()
            self._stop_blinking()
        elif event.type == 'MOUSEMOTION':
            if not self._selecting:
                self._selecting = True
                self._selection_pos = self.cursor_pos
            self.cursor_pos = self._compute_cursor_pos(event.pos)
            self._render_text()
            self._stop_blinking()
        elif event.type == 'focused':
            self._focused = True
            self.image = self._image_focused
            if self.default_value:
                self._selecting = True
                self._selection_pos = 0
            else:
                self._selecting = False
            self.cursor_pos= len(self._value)
            self._render_text()
        elif event.type == 'blurred':
            self.image = self._image_plain
            self._focused = False
            self._cursor.visible = False
            self.default_value = self._default_value_permanant
