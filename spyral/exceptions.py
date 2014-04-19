"""
This module defines custom exceptions that are thrown throughout spyral.
"""

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
class GameEndException(Exception):
    pass
    
# Warnings
class UnusedStyleWarning(Warning):
    pass
class ActorsNotAvailableWarning(Warning):
    pass


# Convenience Wrappers
def unused_style_warning(obj, properties):
    warnings.warn("%r does not understand style properties %s" %
                  (obj, ','.join(properties)),
                  UnusedStyleWarning)
def actors_not_available_warning():
    warnings.warn("You do not have Greenlets installed, so you cannot use Actors.", ActorsNotAvailableWarning)