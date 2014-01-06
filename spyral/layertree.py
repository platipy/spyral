class LayerTree(object):
    MAX_LAYERS = 10
    def __init__(self, scene):
        self.layers = {scene : []}
        self.child_views = {scene : []}
        self.layer_location = {scene : [0]}
        self.scene = scene
        self.tree_height = {scene : 1}
        self._precompute_positions()
        
    def add_view(self, view):
        parent = view._view
        self.layers[view] = []
        self.child_views[view] = []
        self.child_views[parent].append(view)
        self.tree_height[view] = 1
        if len(self.child_views[parent]) == 1:
            self.tree_height[parent] += 1
            while parent != self.scene:
                parent = parent._view
                self.tree_height[parent] += 1
        self._precompute_positions()
        
    def set_view_layer(self, view, layer):
        view.layer = layer
        self._precompute_positions()
        
    def set_view_layers(self, view, layers):
        self.layers[view] = layers
        self._precompute_positions()
    
    def _compute_positional_chain(self, chain):
        total = 0
        for index, value in enumerate(chain):
            total += value * self.MAX_LAYERS ** (self.maximum_height - index - 1)
        return total
        
    def _precompute_positions(self):
        self.maximum_height = self.tree_height[self.scene]
        self.layer_location = {}
        self._precompute_position_for_layer(self.scene, [])
        for layer_key, value in self.layer_location.iteritems():
            self.layer_location[layer_key] = self._compute_positional_chain(value)
        
    def _precompute_position_for_layer(self, view, current_position):
        position = 0
        for position, layer in enumerate(self.layers[view], 1):
            self.layer_location[(view, layer)] = current_position + [position]
        self.layer_location[view] = current_position + [1+position]
        for subview in self.child_views[view]:
            if subview.layer is None:
                new_position = self.layer_location[view]
            else:
                new_position = self.layer_location[(view, subview.layer)]
            self._precompute_position_for_layer(subview, new_position)
    
    def get_layer_position(self, parent, layer):
        s = layer.split(':')
        layer = s[0]
        offset = 0
        if len(s) > 1:
            mod = s[1]
            if mod == 'above':
                offset = 0.5
            if mod == 'below':
                offset = -0.5
        if (parent, layer) in self.layer_location:
            position = self.layer_location[(parent, layer)]
        elif parent in self.layer_location:
            position = self.layer_location[parent]
        else:
            position = self.layer_location[self.scene]
        return position + offset
        
"""
# These should be re-implemented as tests
    
class Scene(object):
    def __str__(self):
        return "Scene"
    __repr__ = __str__
class View(object):
    def __init__(self, scene, name):
        self.parent = self.scene = scene
        self.layer = None
        self.name = name
    def __str__(self):
        return self.name + " - " + str(self.layer)
    __repr__ = __str__
scene = Scene()
view = View(scene, "V#1")
view2 = View(scene, "V#2")
view3 = View(view2, "V#3")
view2_1 = View(view2, "V#2_1")
view4 = View(view3, "V#4")

lt = LayerTree(scene)
lt.set_view_layers(scene, ["bottom", "top"])
lt.add_view(view)
lt.set_view_layer(view, "top")
lt.add_view(view2)
lt.set_view_layer(view2, "bottom")
lt.add_view(view3)
lt.add_view(view2_1)
lt.set_view_layers(view2, ["alpha", "beta", "gamma"])
lt.set_view_layer(view2_1, "beta")
lt.add_view(view4)
lt._precompute_positions()
for name, order in sorted(lt.layer_location.iteritems(), key=lambda x:x[1]):
    print name, order
print "*" * 10
for name, children in lt.child_views.iteritems():
    print name, ":::", map(str, children)
print "*" * 10
"""