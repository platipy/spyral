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
        self._on_state_change()
    
    def _set_state(self, state):
        self._state = state
        self.image = self._images[state]
        self._on_state_change()
        
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
        MultiStateWidget.__init__(self, scene, ['up', 'down', 'down_focused', 'down_hovered', 'up_focused', 'up_hovered'])
        
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
        
    def _on_state_change(self):
        self._text_sprite.pos = spyral.Vec2D(self._padding, self._padding) / 2
                
    text = property(_get_text, _set_text)
    
    def handle_mouse_up(self, event):
        if self.state.startswith('down'):
            self.state = self.state.replace('down', 'up')
        
    def handle_mouse_down(self, event):
        if self.state.startswith('up'):
            self.state = self.state.replace('up', 'down')
        
    def handle_mouse_out(self, event):
        if "_hovered" in self.state:
            self.state = self.state.replace('_hovered', '')
        
    def handle_mouse_over(self, event):
        if not "_hovered" in self.state:
            self.state = self.state.replace('_focused', '') + "_hovered"
        
    def handle_mouse_motion(self, event):
        pass
        
    def handle_focus(self, event):
        if self.state in ('up', 'down'):
            self.state+= '_focused'
    
    def handle_blur(self, event):
        if self.state in ('up_focused', 'down_focused'):
            self.state = self.state.replace('_focused', '')
            
    def handle_key_down(self, event): pass
    def handle_key_up(self, event): pass
        
        
    def __stylize__(self, properties):
        self.font = spyral.Font(*properties.pop('font'))
        self._text = properties.pop('text', "Button")

        spyral.MultiStateWidget.__stylize__(self, properties)
    
        
class ToggleButtonWidget(ButtonWidget):
    """
    A ToggleButtonWidget is similar to a Button, except that it will stay down
    after it's been clicked, until it is clicked again.
    """
    def __init__(self, scene, text = "Okay"):
        ButtonWidget.__init__(self, scene, text)
        
    def handle_mouse_up(self, event):
        pass
        
    def handle_mouse_down(self, event):
        if self.state.startswith('down'):
            self.state = self.state.replace('down', 'up')
        elif self.state.startswith('up'):
            self.state = self.state.replace('up', 'down')
        

class CheckboxWidget(ToggleButtonWidget):
    """
    A CheckboxWidget is similar to a ToggleButtonWidget, only it doesn't have text.
    """
    def __init__(self, scene):
        ToggleButtonWidget.__init__(self, scene, "")

class RadioButtonWidget(ToggleButtonWidget):
    """
    A RadioButton is similar to a CheckBox, except it is to be placed into a
    RadioGroup, which will ensure that only one RadioButton in it's group is
    selected at a time.
    """
    def __init__(self, scene, group):
        ToggleButtonWidget.__init__(self, scene)
        
class RadioGroup(object):
    """
    Only one RadioButton in a RadioGroup can be selected at a time.
    """
    def __init__(self, buttons, selected = None):
        pass
    
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
        scene.register("input.keyboard.down.tab", self.handle_tab)
        scene.register("input.keyboard.up.tab", self.handle_tab)
        scene.register("input.keyboard.up", self.handle_key_down)
        scene.register("input.keyboard.down", self.handle_key_up)
        
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


# Default Value stuff
class TextInputWidget(spyral.AggregateSprite):            
    def __init__(self, scene, width = 10, value = '', default_value = True, text_length = None, validator = None):
        spyral.AggregateSprite.__init__(self, scene)

        # Make text cursor
        child_anchor = (self._padding, self._padding)
        self._cursor = spyral.Sprite(scene)
        self._cursor.anchor = child_anchor
        self._cursor._time = 0.
        self._cursor_pos = 0
        self.add_child(self._cursor)
        
        # Make text viewport/sprite
        self._text = spyral.Sprite(scene)
        self._text_viewport = spyral.ViewPort(scene)
        self._text_viewport.pos = child_anchor
        self._text_viewport.crop = spyral.Rect(0, 0, width - 2 * self._padding, int(math.ceil(self.font.get_linesize())))
        self._text_viewport.add(self._text)
        self.add_child(self._text_viewport)
        
        # Focusing
        self.focused = False
        
        # Selection
        self._selection_pos = 0
        self._selecting = False
        self._shift_was_down = False

        # Validation
        if validator is None:
            self.validator = string.printable
        else:
            self.validator = validator
        
        # Text value
        self.default_value = self._default_value_permanant = default_value
        self.text_length = text_length
        if text_length is not None and len(value) < text_length:
            value = value[:text_length]
        self.value = value
        self.cursor_pos = 0
        
        # Rendering
        self._render_cursor()
        self._render_backs()
        
    def __stylize__(self, properties):
        self._padding = properties.pop('padding', 4)
        self._nine_slice = properties.pop('nine_slice', False)
        self._image_locations = {}
        self._image_locations['focused'] = properties.pop('image_focused')
        self._image_locations['unfocused'] = properties.pop('image_unfocused')
        self._cursor_blink_interval = properties.pop('cursor_blink_interval', .5)
        self._cursor_color = properties.pop('cursor_color', (0, 0, 0))
        self._highlight_color = properties.pop('highlight_color', (0, 140, 255))
        self._highlight_background_color = properties.pop('highlight_background_color', (0, 140, 255))
        self.font = spyral.Font(*properties.pop('font'))

        spyral.AggregateSprite.__stylize__(self, properties)
            
    def _compute_letter_widths(self):
        self._letter_widths = [0]
        for index, value in enumerate(self._value, 1):
            width, height= self.font.get_size(self._value[:index])
            self._letter_widths.append(width)
            
    def _insert_char(self, position, char):
        """
        Insert a character into this textbox at the position.
        """
        if position == len(self._value):
            self._value += char
            new_width= self.font.get_size(self._value)[0]
            self._letter_widths.append(new_width)
        else:
            self._value = self._value[:position] + char + self._value[position:]
            self._compute_letter_widths()
        self._render_text()
        
    def _remove_char(self, position, end = None):
        """
        Remove the character at position, or from position to end if the
        optional parameter is given.
        """
        if end is None:
            end = position+1
        if position == len(self._value): 
            pass
        else:
            self._value = self._value[:position]+self._value[end:]
            self._compute_letter_widths()
        self._render_text()
        self.cursor = self.cursor
        
    def _get_value(self):
        return self._value
        
    def _set_value(self, value):
        self._value = value
        self._compute_letter_widths()
        self._render_text()
        self.cursor_pos = 0
    
    def _get_cursor_pos(self):
        return self._cursor_pos
    
    def _set_cursor_pos(self, position):
        self._cursor_pos = position
        crop = self._move_viewport()
        left, top = crop.topleft
        width, height = crop.size
        self._cursor.x = min(max(self._letter_widths[self.cursor_pos] - left, 0), width)
        self._cursor.y = 0
        
    def validate(self, char):
        valid_length = self.text_length is None or (self.text_length is not None and len(self._value) < self.text_length)
        valid_char = str(char) in self.validator
        return valid_length and valid_char
        
    def _get_padding(self):
        return self._padding
    
    def _set_padding(self, padding):
        self._padding = padding
        self._render_cursor()
        self._render_backs()
        
    def _get_focused(self):
        return self._focused
        
    def _set_focused(self, focused):
        self._focused = focused
        self._cursor.visible = focused

    focused = property(_get_focused, _set_focused)
    value = property(_get_value, _set_value)
    cursor_pos = property(_get_cursor_pos, _set_cursor_pos)
    padding = property(_get_padding, _set_padding)
    
    # Text
        
    def _render_text(self):
        if self._selecting and (self._cursor_pos != self._selection_pos):
            start, end = sorted((self._cursor_pos, self._selection_pos))
            
            pre = self.font.render(self._value[:start])
            highlight = self.font.render(self._value[start:end], color=self._highlight_color)
            post = self.font.render(self._value[end:])
            
            pre_missed = self.font.get_size(self._value[:end])[0] - pre.get_width() - highlight.get_width() + 1
            if self._value[:start]:
                post_missed = self.font.get_size(self._value)[0] - post.get_width() - pre.get_width() - highlight.get_width() - 1
                self._text.image = spyral.Image.from_sequence((pre, highlight, post), 'right', [pre_missed, post_missed])
            else:
                post_missed = self.font.get_size(self._value)[0] - post.get_width() - highlight.get_width()
                self._text.image = spyral.Image.from_sequence((highlight, post), 'right', [post_missed])

        else:
            self._text.image = self.font.render(self._value)
        self._move_viewport()
        
    def _move_viewport(self):
        width = self._letter_widths[self.cursor_pos]
        max_width = self._letter_widths[-1]
        cursor_width = 2
        left, top = self._text_viewport.crop.topleft
        view_width, view_height = self._text_viewport.crop.size
        x = width - left
        if x < 0: 
            left += x
        if x+cursor_width > view_width:
            left += x + cursor_width - view_width
        if left+view_width> max_width and max_width > view_width:
            left = max_width - view_width
        self._text_viewport.crop = spyral.Rect(left, top, view_width, view_height)
        return self._text_viewport.crop
    # Cursor
        
    def _render_cursor(self):
        self._cursor.image = spyral.Image(size=(2,self._text_viewport.crop.height))
        self._cursor.image.fill(self._cursor_color)
        
    def _compute_cursor_pos(self, mouse_pos):
        x = mouse_pos[0] + self._text_viewport.crop.left - self.x - self._padding
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
        self._cursor._time = 0
        self._cursor.visible = True
    
    # Backs
        
    def _render_backs(self):
        self._images = {}
        self._images['unfocused'] = spyral.Image(self._image_locations['unfocused'])
        self._images['focused'] = spyral.Image(self._image_locations['focused'])
        if self._nine_slice:
            size = (self._text_viewport.crop.width + 2*self.padding, self._text_viewport.crop.height + 2*self.padding)
            self._images['unfocused'] = spyral.Image.render_nine_slice(self._images['unfocused'], size)
            self._images['focused'] = spyral.Image.render_nine_slice(self._images['focused'], size)
        
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
            self._cursor._time += dt
            if self._cursor._time > self._cursor_blink_interval:
                self._cursor._time -= self._cursor_blink_interval
                self._cursor.visible = not self._cursor.visible
    
    
    def handle_key_down(self, event):
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
            
    def handle_key_up(self, event):
        pass
        
    def handle_mouse_over(self, event):
        pass
        
    def handle_mouse_out(self, event):
        pass
        
    def handle_mouse_down(self, event):
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
        
    def handle_mouse_up(self, event):
        self.cursor_pos = self._compute_cursor_pos(event.pos)
        
    def handle_mouse_motion(self, event):
        if not self._selecting:
            self._selecting = True
            self._selection_pos = self.cursor_pos
        self.cursor_pos = self._compute_cursor_pos(event.pos)
        self._render_text()
        self._stop_blinking()
        
    def handle_focus(self, event):
        self._focused = True
        self.image = self._images['focused']
        if self.default_value:
            self._selecting = True
            self._selection_pos = 0
        else:
            self._selecting = False
        self.cursor_pos= len(self._value)
        self._render_text()
        
    def handle_blur(self, event):
        self._focused = False
        self.image = self._images['unfocused']
        self._cursor.visible = False
        self.default_value = self._default_value_permanant