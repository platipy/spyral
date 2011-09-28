import pygame as pygame

def new_surface(size, size2 = None):
    """
    new_surface((width,height)) or new_surface(width, height)
    Returns a new surface guaranteed to work with spyral.
    """
    if size2 is None:
        return pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA, 32)
    return pygame.Surface((int(size), int(size2)), pygame.SRCALPHA, 32)
    
def load_image(path, colorkey=None):
    """
    Load an image from a filename. colorkey is an optional parameter, if it
    is set, then the colorkey of the image is set. If colorkey is -1, then the
    colorkey is automatically determined from the top left corner.
    """
    try:
        image = pygame.image.load(path)
    except pygame.error, message:
        print "Cannot load image:", path
        raise SystemExit, message
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image.convert_alpha()