import spyral
import parsley
import string
from collections import defaultdict
from ast import literal_eval

parser = None

def init():
    global parser
    parser = StyleParser()
    parser.parser = parsley.makeGrammar(open(spyral._get_spyral_path() + 'resources/style.parsley', "r").read(),
                                          {"string": string,
                                           "parser": parser,
                                           "leval": literal_eval,
                                           "Vec2D": spyral.Vec2D})

def parse(style, scene):
    parser.scene = scene
    parser.parse(style)

class StyleParser(object):
    def __init__(self):
        self.scene = None
        self.classes = []

    def assign(self, identifier, value):
        self.scene._style_symbols[identifier] = value

    def lookup(self, identifier):
        if identifier not in self.scene._style_.symbols:
            raise NameError("%s is not a previously defined name in the styles" % identifier)
        return self.scene._style_symbols[identifier]

    def calculate(self, ret, ops):
        for op in ops:
            if op[0] == '+':
                ret += op[1]
            elif op[0] == '-':
                ret -= op[1]
            elif op[0] == '*':
                ret *= op[1]
            elif op[0] == '/':
                ret /= op[1]
        return ret

    def push(self, classes):
        self.classes = classes

    def pop(self):
        self.classes = []

    def set_property(self, property, value):
        for cls in self.classes:
            if property == 'inherit':
                if value not in self.scene._style_properties:
                    raise ValueError("Requested to inherit from '%s' which has no style" % value)
                self.scene._style_properties[cls].update(self.properties[value])
            else:
                self.scene._style_properties[cls][property] = value

    def parse(self, style):
        parse = self.parser(style).all()

        # print 'Input Style:'
        # print style
        # print 'At the end of the parse, symbol table:'
        # import pprint
        # pprint.pprint(self.symbols)
        # print 'Now the properties'
        # pprint.pprint(dict(self.properties))