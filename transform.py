def smooth_rotate(surf, angle, scale=10):
    """
    Performs a smoother rotation of a surface by scaling, rotating, and
    rescaling on rotations.
    """
    s = max(surf.get_width(), surf.get_height())
    surf2 = pygame.transform.rotozoom(surf, angle, scale)
    d = int(round((surf2.get_width() - s * scale) / 2.))
    surf2 = pygame.transform.chop(surf2, (0, 0, d, d))
    surf2 = pygame.transform.chop(surf2, (s * scale, s * scale, 2 * d, 2 * d))
    surf2 = pygame.transform.scale(surf2, (s, s))
    return surf2


def smooth_rotate_set(surf, nangles=36, scale=10):
    """
    Provides a set of rotated images.
    """
    return [smooth_rotate(surf, theta * 360. / nangles, scale) for theta in range(nangles)]
