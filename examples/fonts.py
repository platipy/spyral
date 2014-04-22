try:
    import _path
except NameError:
    pass
import spyral

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

class Text(spyral.Sprite):
    def __init__(self, scene, font, text):
        spyral.Sprite.__init__(self, scene)
        self.image = font.render(text)

class GuidedText(spyral.Sprite):
    def __init__(self, scene, font, text, y):
        spyral.Sprite.__init__(self, scene)
        big_font = spyral.Font(font, 36)
        small_font = spyral.Font(font, 11)
        self.image = big_font.render(text)

        self.anchor = 'center'
        self.pos = scene.rect.center
        self.y = y

        guides = [("baseline", big_font.ascent),
                  ("linesize", big_font.linesize)]
        for name, height in guides:
            self.image.draw_rect((0,0,0),
                                 (0,0),
                                 (self.width, height),
                                 border_width = 1,
                                 anchor= 'topleft')
            guide = Text(scene, small_font, name)
            guide.pos = self.pos
            guide.x += self.width / 2
            guide.y += - self.height / 2 + height
            guide.anchor = 'midleft'

class Game(spyral.Scene):
    """
    A Scene represents a distinct state of your game. They could be menus,
    different subgames, or any other things which are mostly distinct.
    """
    def __init__(self):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill((255,255,255))

        text = GuidedText(self, "DejaVuSans.ttf", "ABCDEFGHIJKLM", self.height * 1. / 8)
        text = GuidedText(self, "DejaVuSans.ttf", "NOPQRSTUVWXYZ", self.height * 2. / 8)
        text = GuidedText(self, "DejaVuSans.ttf", "abcdefghijklm", self.height * 3. / 8)
        text = GuidedText(self, "DejaVuSans.ttf", "nopqrstuvwxyz", self.height * 4. / 8)
        text = GuidedText(self, "DejaVuSans.ttf", "1234567890-=,", self.height * 5. / 8)
        text = GuidedText(self, "DejaVuSans.ttf", "!@#$%^&*()_+<", self.height * 6. / 8)
        text = GuidedText(self, "DejaVuSans.ttf", ".>/?;:'\"[{]}|\\~`", self.height * 7. / 8)

        spyral.event.register("system.quit", spyral.director.quit)

if __name__ == "__main__":
    spyral.director.init(SIZE) # the director is the manager for your scenes
    spyral.director.run(scene=Game()) # This will run your game. It will not return.
