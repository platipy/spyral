import spyral


class FPSSprite(spyral.sprite.Sprite):
    def __init__(self, font, color):
        spyral.sprite.Sprite.__init__(self)
        self.font = font
        self.color = color
        self.render(0, 0)
        self.update_in = 5

    def render(self, fps, ups):
        self.image = self.font.render("%d / %d" % (fps, ups), 0, self.color)

    def update(self, *args, **kwargs):
        self.update_in -= 1
        if self.update_in == 0:
            self.update_in = 5
            clock = spyral.director.get_scene().clock
            self.render(clock.fps, clock.ups)
