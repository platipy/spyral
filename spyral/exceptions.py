import warnings

class SceneHasNoSizeError(Exception):
	pass
class NotStylableError(Exception):
	pass
class NoImageError(Exception):
	pass
class BackgroundSizeError(Exception):
	pass
class LayersAlreadySetError(Exception):
	pass

# Warnings
class UnusedStyleWarning(Warning):
	pass


# Convenience Wrappers
def unused_style_warning(object, properties):
    warnings.warn("%r does not understand style properties %s" % (object, ','.join(properties)),
                      UnusedStyleWarning)
