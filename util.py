import pygame

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
    except pygame.error as message:
        print("Cannot load image:", path)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey)
    return image.convert_alpha()
    
class Spritesheet(object):
    """
    http://pygame.org/wiki/Spritesheet
    """
    def __init__(self, filename, colorkey=None):
        try:
            self.sheet = pygame.image.load(filename)
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image.convert_alpha()
    def images_at(self, rects, colorkey = None):
        """
        Loads multiple images from a list of coordinates, returns them as a list
        """
        return [self.image_at(rect, colorkey) for rect in rects]
    def load_strip(self, rect, image_count, colorkey = None):
        """
        Loads a strip of images and returns them as a list
        """
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
    def unload(self):
        self.sheet= None;    