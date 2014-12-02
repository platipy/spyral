try:
    import _path
except NameError:
    pass
import spyral

resolution = (640, 480)
spyral.director.init(resolution)
my_scene = spyral.Scene(resolution)
my_scene.background = spyral.Image(size=resolution).fill((0,0,0))
my_scene._namespaces = ("input.keyboard.down.q", "input.keyboard.down",
                        "input.keyboard.down.quoteright", "input.mouse.down",
                        "input.mouse", "animation.Sprite.x.end")

def test(key, *correct_namespaces):
    assert set(my_scene._get_namespaces(key)) == set(correct_namespaces) , \
           "Expected {}, got {}".format(set(correct_namespaces),
                                        set(my_scene._get_namespaces(key)))

test("input.keyboard", "input.keyboard.down.q", "input.keyboard.down", 
                       "input.keyboard.down.quoteright")            
test("input.keyboard.down.q", "input.keyboard.down.q", "input.keyboard.down")
test("input.keyboard.down", "input.keyboard.down.q", "input.keyboard.down",
                            "input.keyboard.down.quoteright")
test("input.keyboard.down.quoteright", "input.keyboard.down", 
                                       "input.keyboard.down.quoteright")
test("input.mouse.down", "input.mouse.down", "input.mouse")
test("animation.Sprite.x.end", "animation.Sprite.x.end")