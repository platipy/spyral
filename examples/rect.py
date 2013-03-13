import _path
import spyral
a1 = spyral.Rect((0,0), (10, 10))
b1 = spyral.Rect((5,5), (15, 15))

print b1.clip(a1)