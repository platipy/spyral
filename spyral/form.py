from pygame import key, mouse
import spyral
from bisect import bisect_right

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
        
    