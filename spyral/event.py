import pygame
import operator
try:
    import json
except ImportError:
    import simplejson as json
import spyral
import os
import random
import base64

_type_to_attrs = None
_type_to_type = None

class Event(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

_event_names = ['QUIT', 'ACTIVEEVENT', 'KEYDOWN', 'KEYUP', 'MOUSEMOTION',
                'MOUSEBUTTONUP', 'VIDEORESIZE', 'VIDEOEXPOSE', 'USEREVENT',
                'MOUSEBUTTONDOWN']

def init():
    global _type_to_attrs
    global _type_to_type

    _type_to_attrs = {
        pygame.QUIT: tuple(),
        pygame.ACTIVEEVENT: ('gain', 'state'),
        pygame.KEYDOWN: ('unicode', 'key', 'mod'),
        pygame.KEYUP: ('key', 'mod'),
        pygame.MOUSEMOTION: ('pos', 'rel', 'buttons'),
        pygame.MOUSEBUTTONUP: ('pos', 'button'),
        pygame.MOUSEBUTTONDOWN: ('pos', 'button'),
        pygame.VIDEORESIZE: ('size', 'w', 'h'),
        pygame.VIDEOEXPOSE: ('none'),
    }
    _type_to_type = {
        pygame.QUIT: "system.quit",
        pygame.ACTIVEEVENT: "system.focus_change",
        pygame.KEYDOWN: "input.keyboard.down",
        pygame.KEYUP: "input.keyboard.up",
        pygame.MOUSEMOTION: "input.mouse.motion",
        pygame.MOUSEBUTTONUP: "input.mouse.up",
        pygame.MOUSEBUTTONDOWN: "input.mouse.down",
        pygame.VIDEORESIZE: "system.video_resize",
        pygame.VIDEOEXPOSE: "system.video_expose",
    }
    
def queue(type, event = None, _scene = None):
    if _scene is None:
        _scene = spyral._get_executing_scene()
    _scene._queue_event(type, event)

def handle(type, event = None, _scene = None):
    if _scene is None:
        _scene = spyral._get_executing_scene()
    _scene._handle_event(type, event)

def _pygame_to_spyral(event):
    attrs = _type_to_attrs[event.type]
    type = _type_to_type[event.type]
    e = Event()
    for attr in attrs:
        setattr(e, attr, getattr(event, attr))
    if type.startswith("input"):
        setattr(e, "type", type.split(".")[-1])
    if type.startswith('input.keyboard'):
        k = pygame.key.name(event.key).replace(' ', '_').replace('.', 'dot')
        print k
        type += '.' + k
        
    return (type, e)
    

class EventHandler(object):
    """
    Base event handler class.
    """
    def __init__(self):
        self._events = []
        self._mouse_pos = (0, 0)

    def tick(self):
        """
        Should be called at the beginning of update cycle. For the
        event handler which is part of a scene, this function will be
        called automatically. For any additional event handlers, you
        must call this function manually.
        """
        pass

    def get(self, types=[]):
        """
        Gets events from the event handler. Types is an optional
        iterable which has types which you would like to get.
        """
        try:
            types[0]
        except IndexError:
            pass
        except TypeError:
            types = (types,)

        if types == []:
            ret = self._events
            self._events = []
            return ret

        ret = [e for e in self._events if e['type'] in types]
        self._events = [e for e in self._events if e['type'] not in types]
        return ret


class LiveEventHandler(EventHandler):
    def __init__(self, output_file=None):
        """
        An event handler which pulls events from the operating system.
        
        The optional output_file argument specifies the path to a file
        where the event handler will save a custom json file that can
        be used with the `ReplayEventHandler` to show replays of a
        game in action, or be used for other clever purposes.
        
        .. note::
            
            If you use the output_file parameter, this function will
            reseed the random number generator, save the seed used. It
            will then be restored by the ReplayEventHandler.        
        """
        EventHandler.__init__(self)
        self._save = output_file is not None
        if self._save:
            self._file = open(output_file, 'w')
            seed = os.urandom(4)
            info = {'random_seed': base64.encodestring(seed)}
            random.seed(seed)
            self._file.write(json.dumps(info) + "\n")

    def tick(self):
        mouse = pygame.mouse.get_pos()
        events = pygame.event.get()
        self._mouse_pos = mouse
        self._events.extend(events)
        # if self._save:
        #     d = {'mouse': mouse, 'events': events}
        #     self._file.write(json.dumps(d) + "\n")

    def __del__(self):
        if self._save:
            self._file.close()

        
class ReplayEventHandler(EventHandler):
    def __init__(self, input_file):
        """
        An event handler which replays the events from a custom json
        file saved by the `LiveEventHandler`.
        """
        EventHandler.__init__(self)
        self._file = open(input_file)
        info = json.loads(self._file.readline())
        random.seed(base64.decodestring(info['random_seed']))
        self.paused = False
        
    def pause(self):
        """
        Pauses the replay of the events, making tick() a noop until
        resume is called.
        """
        self.paused = True
        
    def resume(self):
        """
        Resumes the replay of events.
        """
        self.paused = False

    def tick(self):
        if self.paused:
            return
        try:
            d = json.loads(self._file.readline())
        except ValueError:
            spyral.director.pop()
        events = d['events']
        events = [EventDict(e) for e in events]
        self._mouse_pos = d['mouse']
        self._events.extend(events)        

class Mods(object):
    def __init__(self):
        self.none = pygame.KMOD_NONE
        self.lshift = pygame.KMOD_LSHIFT
        self.rshift = pygame.KMOD_RSHIFT
        self.shift = pygame.KMOD_SHIFT
        self.caps = pygame.KMOD_CAPS
        self.ctrl = pygame.KMOD_CTRL
        self.lctrl = pygame.KMOD_LCTRL
        self.rctrl = pygame.KMOD_RCTRL
        self.lalt = pygame.KMOD_LALT
        self.ralt = pygame.KMOD_RALT
        self.alt = pygame.KMOD_ALT

class Keys(object):
        
    def __init__(self):  
      self.load_keys_from_file(spyral._get_spyral_path() + 'resources/default_key_mappings.txt')   

    def load_keys_from_file(self, filename):
        fp = open(filename)
        keys = fp.readlines()
        fp.close()
        for singleMapping in keys:
            mapping = singleMapping[:-1].split(' ')
            if len(mapping) == 2:
                if mapping[1][0:2] == '0x':
                    setattr(self, mapping[0], int(mapping[1],16))
                else:
                    setattr(self, mapping[0], int(mapping[1]))

    def add_key_mapping(self, name, number):
        setattr(self, name, number)
            
keys = Keys()
mods = Mods()
