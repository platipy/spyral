"""Styling offers a way to offshore static data from your game into a .spys
file, improving the separation of code and data."""

import spyral
import parsley
import string
from ast import literal_eval

parser = None

def init():
    """
    Initializes the Styler.
    """
    global parser
    parser = StyleParser()
    style_file = open(spyral._get_spyral_path() +
                      'resources/style.parsley').read()
    parser.parser = parsley.makeGrammar(style_file,
                                        {"string": string,
                                         "parser": parser,
                                         "leval": literal_eval,
                                         "Vec2D": spyral.Vec2D})

def parse(style, scene):
    """
    Parses a style and applies it to the scene.

    :param str style: The style definition
    :param scene: The scene to apply this definition to.
    :type scene: :class:`Scene <spyral.Scene>`
    """
    parser.scene = scene
    parser.parse(style)

class StyleParser(object):
    """
    The style parser is a single instance class that converts a style file into
    attributes to be applied to an object (e.g., a Scene, View, or Sprite).
    """
    def __init__(self):
        self.scene = None
        self.classes = []

    def assign(self, identifier, value):
        """
        Assigns the identifier to the particular style symbol.

        :param str identifier: The identifier (?)
        :param ? value: ?
        """
        self.scene._style_symbols[identifier] = value

    def lookup(self, identifier):
        """
        Return the style symbols associated with this identifier in the scene.

        :param str identifier: The identifier (e.g., ?)
        """
        if identifier not in self.scene._style_symbols:
            raise NameError("%s is not a previously defined name in the styles"
                            % identifier)
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
                    raise ValueError(("Requested to inherit from "
                                     "'%s' which has no style") % value)
                self.scene._style_properties[cls].update(self.properties[value])
            else:
                self.scene._style_properties[cls][property] = value

    def apply_func(self, f, args):
        if f not in self.scene._style_functions:
            raise ValueError("Function '%s' is undefined" % f)
        return self.scene._style_functions[f](*args)

    def parse(self, style):
        parse = self.parser(style).all()

        # print 'Input Style:'
        # print style
        # print 'At the end of the parse, symbol table:'
        # import pprint
        # pprint.pprint(self.symbols)
        # print 'Now the properties'
        # pprint.pprint(dict(self.properties))
