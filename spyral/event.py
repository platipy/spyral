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
from collections import defaultdict

class Event(object):
    def __init__(self, type):
        self.type = type

class EventDict(dict):
    def __getattr__(self, attr):
        return self[attr]
        
    def __setattr__(self, attr, value):
        self[attr] = value

_event_names = ['QUIT', 'ACTIVEEVENT', 'KEYDOWN', 'KEYUP', 'MOUSEMOTION',
                'MOUSEBUTTONUP', 'JOYAXISMOTION', 'JOYBALLMOTION',
                'JOYHATMOTION', 'JOYBUTTONUP', 'JOYBUTTONDOWN',
                'VIDEORESIZE', 'VIDEOEXPOSE', 'USEREVENT', 'MOUSEBUTTONDOWN']

def init():
    global _type_to_name
    global _type_to_attrs
    _type_to_name = dict((getattr(pygame, name), name) for name in _event_names)

    _type_to_attrs = {
        pygame.QUIT: ('type', ),
        pygame.ACTIVEEVENT: ('type', 'gain', 'state'),
        pygame.KEYDOWN: ('type', 'unicode', 'key', 'mod'),
        pygame.KEYUP: ('type', 'key', 'mod'),
        pygame.MOUSEMOTION: ('type', 'pos', 'rel', 'buttons'),
        pygame.MOUSEBUTTONUP: ('type', 'pos', 'button'),
        pygame.MOUSEBUTTONDOWN: ('type', 'pos', 'button'),
        pygame.JOYAXISMOTION: ('type', 'joy', 'axis', 'value'),
        pygame.JOYBALLMOTION: ('type', 'joy', 'ball', 'rel'),
        pygame.JOYHATMOTION: ('type', 'joy', 'hat', 'value'),
        pygame.JOYBUTTONUP: ('type', 'joy', 'button'),
        pygame.JOYBUTTONDOWN: ('type', 'joy', 'button'),
        pygame.VIDEORESIZE: ('type', 'size', 'w', 'h'),
        pygame.VIDEOEXPOSE: ('type', 'none'),
        pygame.USEREVENT: ('type', 'code')
    }


def _event_to_dict(event):
    attrs = _type_to_attrs[event.type]
    d = EventDict((attr, getattr(event, attr)) for attr in attrs)
    d['type'] = _type_to_name[event.type]
    if d['type'] in ('KEYDOWN', 'KEYUP'):
        try:
            d['ascii'] = chr(d['key'])
        except ValueError:
            d['ascii'] = ''
    return d


class EventHandler(object):
    """
    Base event handler class.
    """
    def __init__(self):
        self._events = []
        self._mouse_pos = (0, 0)

    def _tick(self):
        """
        Should be called at the beginning of each tick. It will pre-select all
        the relevant events.
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
        EventHandler.__init__(self)
        self._save = output_file is not None
        if self._save:
            self._file = open(output_file, 'w')
            seed = os.urandom(4)
            info = {'random_seed': base64.encodestring(seed)}
            random.seed(seed)
            self._file.write(json.dumps(info) + "\n")

    def _tick(self):
        mouse = pygame.mouse.get_pos()
        events = [_event_to_dict(e) for e in pygame.event.get()]
        self._mouse_pos = mouse
        self._events.extend(events)
        if self._save:
            d = {'mouse': mouse, 'events': events}
            self._file.write(json.dumps(d) + "\n")

    def __del__(self):
        if self._save:
            self._file.close()

class EventManager(object):
    def __init__(self):
        """
        The event manager's task is to take events and send them to
        listeners which have registered to receive events.
        
        Events are any object which have a type attribute, which is a
        string. There are a number of built-in events.
        
        A listener is an object which has a handle_event method which
        takes one event as an argument.
        
        If handle_event returns True, the manager does not pass the
        event to any other listeners. To ensure the right listeners
        handle events, ensure that their priority is set accordingly.
        
        
        """
        self._listeners = defaultdict(lambda : [])
        self._events = []
        self._busy = False
        
    def register_listener(self, listener, event_types, priority = 5):
        # We may switch to bisect here at some point, but for now, we'll just resort
        for event_type in event_types:
            self._listeners[event_type].append((listener, priority))
            self._listeners[event_type] = sorted(self._listeners[event_type], key=operator.itemgetter(1), reverse = True)
            
    def unregister_listener(self, listener, event_types = None, priority = None):
        """
        Remove the listener for the given event types and priority. If
        event_types is None, remove it for all event types, and if 
        priority is None, remove it for any priority.
        """
        if event_types is None:
            event_types = list(self._listeners.iterkeys())
        for e in event_types:
            self._listeners[e] = [l for l in self._listeners[e] if not (l[0] is listener and l[1] == priority)]
        
    def send_events(self, events):
        """
        Sends an event to the relevant listeners.
        
        If events are currently being processed by the manager, the
        events are added to the list of events to be sent out.
        """
        if not self._busy:
            self._busy = True
            self._events.extend(events)
            while len(self._events) > 0:
                events = self._events
                self._events = []
                for event in events:
                    # Make sure we avoid futzing with things while iterating
                    listeners = self._listeners[event.type][:]
                    for listener in listeners:
                        r = listener[0].handle_event(event)
                        if r is True:
                            break
            self._busy = False
        else:
           self._events.extend(events) 
        
        
    def send_event(self, event): #, immediate = False):
        """
        Sends an event to the relevant listeners.
        """
        self.send_events([event])
        
        # Old version with some potentially interesting things here
        # """
        # If events are currently being processed by the manager, the
        # event is added to the list of events to be sent out, unless
        # immediate is set to True, in which case it is sent immediately.
        # Use immediate sparingly, as it may lead to a large stack if
        # events trigger more immediate calls.
        # """
        # if not self._busy or immediate is True:
        #     print event.type
        #     # Make sure we avoid futzing with things while iterating
        #     listeners = self._listeners[event.type][:]
        #     for listener in listeners:
        #         r = listener[0].handle_event(event)
        #         if r is True:
        #             break
        # else:
        #     self._events.append(event)
        
class ReplayEventHandler(EventHandler):
    def __init__(self, input_file):
        EventHandler.__init__(self)
        self._file = open(input_file)
        info = json.loads(self._file.readline())
        random.seed(base64.decodestring(info['random_seed']))

    def _tick(self):
        try:
            d = json.loads(self._file.readline())
        except ValueError:
            spyral.director.pop()
        events = d['events']
        events = [pygame.event.Event(e['type'], e) for e in events]
        self._mouse_pos = d['mouse']
        self._events.extend(events)

    def __del__(self):
        self._file.close()

class Keys(object):
    def __init__(self):
        self.up = 273
        self.down = 274
        self.right = 275
        self.left = 276
        self.space = 32
        self.shift = pygame.key.KMOD_SHIFT
        self.lshift = pygame.key.KMOD_LSHIFT
        self.rshift = pygame.key.KMOD_RSHIFT
        

keys = Keys()
