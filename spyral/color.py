_scheme = {}

sample = """
color,r,g,b
color1,r,g,b,a
"""

def install_color_scheme(filename):
    """
    Loads a colorscheme from a file, and installs the colors there for
    use with any spyral function which accepts a color by passing a
    string as the color name.
    
    You can install more than one scheme, but each installation will
    overwrite any colors which were already installed. 
    
    Color schemes are CSV files which follow the form *name,r,g,b* or
    *name,r,g,b,a* where r,g,b,a are integers from 0-255 for the red,
    green, blue, and alpha channels respectively.    
    """
    f = open(filename, 'r')
    for line in f.readlines():
        values = line.split(',')
        if len(values) == 4:
            color, r, g, b = values
            a = 0
        elif len(values) == 5:
            color, r, g, b, a = values
        else:
            continue
        r = int(r)
        b = int(b)
        g = int(g)
        a = int(a)
        _scheme[color] = (r,g,b,a)
        
def get_color(name):
    """
    Takes a color name as a string and returns the rgba version of the color.
    """
    try:
        return _scheme[name]
    except KeyError:
        raise ValueError("%s is not a color from an installed scheme." % name)
        
def _determine(color):
    """
    Internal to figure out what color representation was passed in.
    """
    if isinstance(color, str):
        pieces = color.strip(" ()").split(",")
        if len(pieces) in (3, 4):
            return [int(c) for c in pieces]
        else:
            return get_color(name)
    else:
        return color