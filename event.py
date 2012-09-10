import pygame
try:
    import json
except ImportError:
    import simplejson as json
import spyral
import os
import random
import base64

_event_names = ['QUIT', 'ACTIVEEVENT', 'KEYDOWN', 'KEYUP', 'MOUSEMOTION',
                'MOUSEBUTTONUP', 'JOYAXISMOTION', 'JOYBALLMOTION', 
                'JOYHATMOTION', 'JOYBUTTONUP', 'JOYBUTTONDOWN',
                'VIDEORESIZE', 'VIDEOEXPOSE', 'USEREVENT', 'MOUSEBUTTONDOWN']

_type_to_name = {getattr(pygame, name) : name for name in _event_names}

_type_to_attrs = {
    pygame.QUIT           : ('type', ),
    pygame.ACTIVEEVENT    : ('type', 'gain', 'state'),
    pygame.KEYDOWN        : ('type', 'unicode', 'key', 'mod'),
    pygame.KEYUP          : ('type', 'key', 'mod'),
    pygame.MOUSEMOTION    : ('type', 'pos', 'rel', 'buttons'),
    pygame.MOUSEBUTTONUP  : ('type', 'pos', 'button'),
    pygame.MOUSEBUTTONDOWN: ('type', 'pos', 'button'),
    pygame.JOYAXISMOTION  : ('type', 'joy', 'axis', 'value'),
    pygame.JOYBALLMOTION  : ('type', 'joy', 'ball', 'rel'),
    pygame.JOYHATMOTION   : ('type', 'joy', 'hat', 'value'),
    pygame.JOYBUTTONUP    : ('type', 'joy', 'button'),
    pygame.JOYBUTTONDOWN  : ('type', 'joy', 'button'),
    pygame.VIDEORESIZE    : ('type', 'size, w, h'),
    pygame.VIDEOEXPOSE    : ('type', 'none'),
    pygame.USEREVENT      : ('type', 'code')
}

def _event_to_dict(event):
    attrs = _type_to_attrs[event.type]
    d = dict((attr, getattr(event, attr)) for attr in attrs)
    d['type'] = _type_to_name[event.type]
    return d

class EventHandler(object):
    """
    Base event handler class.
    """
    def __init__(self):
        self._events = []
        self._mouse_pos = (0,0)

    def tick(self):
        """
        Should be called at the beginning of each tick. It will pre-select all
        the relevant events.
        """
        pass

    def get(self, types = []):
        """
        Analagous to pygame.event.get(). Can take either a type or an iterable
        of types. Events are pulled from self._events, populated by each
        implementation.
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
    def __init__(self, output_file = None):
        EventHandler.__init__(self)
        self._save = output_file is not None
        if self._save:
            self._file = open(output_file, 'w')
            seed = os.urandom(4)
            info = {'random_seed' : base64.encodestring(seed)}
            random.seed(seed)
            self._file.write(json.dumps(info) + "\n")
        
    def tick(self):
        mouse = pygame.mouse.get_pos()
        events = [_event_to_dict(e) for e in pygame.event.get()]
        self._mouse_pos = mouse
        self._events.extend(events)
        if self._save:
            d = {'mouse' : mouse, 'events' : events}
            self._file.write(json.dumps(d) + "\n")
        
    def __del__(self):
        if self._save:
            self._file.close()
        
class ReplayEventHandler(EventHandler):
    def __init__(self, input_file):
        EventHandler.__init__(self)
        self._file = open(input_file)
        info = json.loads(self._file.readline())
        random.seed(base64.decodestring(info['random_seed']))
        
    def tick(self):
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
        
class AnnotationOverworld(spyral.scene.Scene):
    def __init__(self, scene, annotation_file, annotation_sprites):
        #####
        ##### Warning, we currently hardcode the screen resolution at 1200, 900
        #####
        spyral.scene.Scene.__init__(self)
        self.clock = scene.clock
        self.scene = scene
        self.camera = spyral.director.get_camera().make_child(virtual_size=(1200,900))
        
        self.tick = 0
        
        self.group = spyral.sprite.Group(self.camera)
        f = open(annotation_file)
        self.annotations = json.loads(f.read())
        self.sprites = annotation_sprites
        print self.annotations
        
        self.pause = 0
        self.paused = False
        
    def pause_for(self, seconds):
        self.pause = self.clock.ticks_per_second * seconds
        print self.pause

    def on_enter(self):
        self.scene.on_enter()

    def on_exit(self):
        self.scene.on_exit()

    def update(self, tick):
        self.group.update()
        if self.pause > 0:
            self.pause -= 1
            return
        if self.paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    self.paused = False
            return

        self.tick += 1
        if str(self.tick) in self.annotations:
            actions = self.annotations[str(self.tick)]
            for a in actions:
                print a
                if a['action'] == 'skip_frames':
                    skip_until = a['next_frame']
                    while self.tick < skip_until:
                        self.scene.update(self.tick)
                        self.tick += 1
                elif a['action'] == 'show_annotation':
                    self.group.add(self.sprites[a['name']])
                elif a['action'] == 'hide_annotation':
                    self.group.remove(self.sprites[a['name']])
                elif a['action'] == 'pause':
                    self.pause_for(a['seconds'])
                elif a['action'] == 'pause_until_space':
                    self.paused = True
                    
        self.scene.update(self.tick)
        
    def render(self):
        self.group.draw()
        self.scene.render()