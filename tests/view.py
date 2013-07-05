import unittest
import spyral

class TestView(spyral.Scene):
    def __init__(self):
        spyral.init()
        spyral.director.init((100, 100))
        spyral.Scene.__init__(self, (100, 100))

    def test_properties(self):
        v = spyral.View(self)
        assert v.size == (100, 100)
        assert v.output_size == (100, 100)

        v.size = (150, 150)
        assert v.size == (150, 150)
        assert v.output_size == (100, 100)

        v.scale = 2
        assert v.size == (150, 150)
        assert v.output_size == (300, 300)

        v.scale = (2, 3)
        assert v.size == (150, 150)
        assert v.output_size == (300, 450)

        # Test Aliases
        v.pos = (20, 30)
        assert v.position == (20, 30)
        assert v.x == 20
        assert v.y == 30

        v.size = (1, 2)
        v.scale = 10
        assert v.width == 1
        assert v.output_width == 10
        assert v.height == 2
        assert v.output_height == 20

        assert v.anchor == 'topleft'
        v.anchor = 'center'