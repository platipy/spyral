# import spyral
from functools import partial

def source(f):
    return partial(f, '')

def dest(f):
    return partial(f, '_dest')

class View(object):
    def __init__(self, view):
        self.view = view
        self.scene = view.scene
        self._age = -1

        self._subviews = set()

        self._pos = (0, 0)
        self._dest_pos = (0, 0)
        self._width = view.width
        self._dest_width = view.width
        self._height = view.height
        self._dest_height = view.height
        self._anchor = 'topleft'
        self._dest_anchor = 'topleft'
        self._offset = (0, 0)
        self._dest_offset = (0, 0)

    def _get_parents(self):
        view = self.view
        parents = []
        while view is not self.scene:
            parents.append(view)
            view = view.view
        return parents

    def _get_size(s, self):
        # Todo: Make these Vec2D
        return (getattr(self, s + '_width'),
                getattr(self, s + '_height'))

    def _set_size(s, self, value):
        if getattr(s, self + '_size') == value:
            return
        setattr(self, s + '_width', value[0])
        setattr(self, s + '_height', value[1])
        self._age = 0

    size = property(source(_get_size), source(_set_size))
    dest_size = property(dest(_get_size), dest(_set_size))

    def _get_anchor(s, self):
        return getattr(self, s + '_anchor')

    def _set_anchor(s, self, value):
        a = getattr(self, s + '_anchor')
        if a == value:
            return
        setattr(s, s + '_anchor', value[0])
        setattr(s,
                s + '_offset',
                spyral.util.anchor_offset(
                    a,
                    getattr(self, s + '_width'),
                    getattr(self, s + '_height')))
        self._age = 0

    def _compute_layer(self, layer):
        # Stub
        return 1
#        spyral.util.compute_layer(self._layers, layer)


    def _static_blit(self, key, blit):
        self.scene._static_blit(key, blit)

    def _blit(self, blit):
        self.scene._blit(blit)





if __name__ == "__main__":
    pass