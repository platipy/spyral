import spyral
import parsley
import string
from collections import defaultdict
from ast import literal_eval

class StyleParser(object):
    def __init__(self):
        self.symbols = {}
        # Todo: Maybe cache the parser generation, if possible?
        self.parser = parsley.makeGrammar(open(spyral._get_spyral_path() + 'resources/style.parsley', "r").read(),
                                          {"string": string,
                                           "parser": self,
                                           "leval": literal_eval})
        self.classes = []
        self.properties = defaultdict(lambda: {})

    def assign(self, identifier, value):
        print 'Assign %s = %s' % (identifier, value)
        self.symbols[identifier] = value

    def lookup(self, identifier):
        if identifier not in self.symbols:
            raise NameError("%s is not a previously defined name in the styles" % identifier)
        return self.symbols[identifier]

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
                if value not in self.properties:
                    raise ValueError("Requested to inherit from '%s' which has no style" % value)
                self.properties[cls].update(self.properties[value])
            else:
                self.properties[cls][property] = value

    def parse(self, style):
        parse = self.parser(style).all()

        # print 'Input Style:'
        # print style
        # print 'At the end of the parse, symbol table:'
        # import pprint
        # pprint.pprint(self.symbols)
        # print 'Now the properties'
        # pprint.pprint(dict(self.properties))