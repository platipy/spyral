import pygame
import spyral


class MouseSprite(spyral.sprite.Sprite):
    """
    A Sprite class to handle mouse hovering and clicks. It conforms to layers
    for event prioritizing. The following attributes may be useful:

    | *click_rect = None* represents a rectangle for clickable area. If None,
      the sprite's *rect* is used.
    | *hover_rect = None* represents a rectangle for hoverable area. If None,
      the sprite's *rect* is used.
    | *consume_clicks = True* is whether a click on this sprite should be
      consumed, or allowed to pass on to other Sprites on this update.
    | *consume_hover = False* is whether this sprite blocks lower sprites from
      being hovered over. Only consumes per group, not globally.
    | *enable_right = False* is whether right clicks should trigger a click
      event
    | *enable_middle = False* is whether middle clicks should trigger a click
      event
    """

    def __init__(self, *args):
        spyral.sprite.Sprite.__init__(self, *args)

        self.click_rect = None
        self.hover_rect = None
        self.consume_clicks = True
        self.consume_hover = False
        self.enable_right = False
        self.enable_middle = False

    def on_click(self, event):
        """ Called when this sprite is clicked. """
        pass

    def on_right_click(self, event):
        """ Called when this sprite is right clicked, if enabled. """
        pass

    def on_middle_click(self, event):
        """ Called when this sprite is middle clicked, if enabled. """
        pass

    def on_mouse_over(self):
        """ Called when the mouse begins hovering over this sprite. """
        pass

    def on_mouse_off(self):
        """ Called when the mouse stops hovering over this sprite. """
        pass

    def _handle_click(self, event):
        if event.button == 3 and self.enable_right is False:
            return False
        elif event.button == 2 and self.enable_middle is False:
            return False
        if self.click_rect is None:
            r = self.rect
        else:
            r = self.click_rect
        if not r.collidepoint(event.pos):
            return False
        if event.button == 1:
            self.on_click(event)
        elif event.button == 3:
            self.on_right_click(event)
        else:
            self.on_middle_click(event)
        return self.consume_clicks

    def _hover(self, pos):
        if self.hover_rect is None:
            r = self.rect
        else:
            r = self.hover_rect
        if r.collidepoint(pos):
            return (True, self.consume_hover)
        return (False, False)


class DragSprite(MouseSprite):
    """
    A Sprite which derives from MouseSprite, and supports all of its features,
    but allows for dragging and dropping the sprite.
    """
    def __init__(self):
        MouseSprite.__init__(self)
        self.dragging = False
        self._real_layer = ''

    def on_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True
            self.drag_offset = (self.position[0] - event.pos[0],
                                self.position[1] - event.pos[1])
            self._real_layer = self.layer
            self.layer = '_DragTop'
        else:
            self.dragging = False
            self.layer = self._real_layer

    def update(self, camera):
        if self.dragging:
            local = camera.world_to_local(pygame.mouse.get_pos())
            if local is not None:
                self.pos = (spyral.point.add(
                            camera.world_to_local(pygame.mouse.get_pos()),
                            self.drag_offset))


class GUIGroup(spyral.sprite.Group):
    """
    A group class which automatically handles the behavior of GUI sprites.
    The behavior is otherwise the same in every way.s
    """
    def __init__(self, *args):
        spyral.sprite.Group.__init__(self, *args)
        self._mouse_previously_over = []

    def update(self, *args):
        spyral.sprite.Group.update(self, *args)
        layers = self.camera.layers()
        mapping = dict((layer, index) for layer, sprite in enumerate(layers))

        def sort_key(sprite):
            try:
                return mapping[x.layer]
            except ValueError:
                if y.layer[0] == '_':
                    return 100
                return -1
        self._sprites.sort(key=sort_key)

        # Let's handle mouse clicks first
        for event in pygame.event.get([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]):
            # We should fix the event to camera coordinates.
            new_pos = self.camera.world_to_local(event.pos)
            if new_pos is None:
                pygame.event.post(event)
                continue
            event = pygame.event.Event(event.type,
                                       {'pos': new_pos,
                                        'button': event.button})
            used = False
            for sprite in self._sprites:
                if not isinstance(sprite, MouseSprite):
                    continue
                if sprite._handle_click(event):
                    used = True
                    break
            if not used:
                pygame.event.post(event)

        # Now let's handle mouseover.
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos is None:
            return
        mouse_pos = self.camera.world_to_local(mouse_pos)
        mouse_now_over = []
        for sprite in self._sprites:
            if not isinstance(sprite, MouseSprite):
                continue
            hover = sprite._hover(mouse_pos)
            if hover[0] is True:
                mouse_now_over.append(sprite)
                # first, is this one that the mouse was previously over
                if sprite in self._mouse_previously_over:
                    if hover[1] is True:  # It wants to consume the hover
                        break
                    continue
                sprite.on_mouse_over()
                if hover[1] is True:
                    break

        for sprite in self._mouse_previously_over:
            if sprite in mouse_now_over:
                continue
            sprite.on_mouse_off()
        self._mouse_previously_over = mouse_now_over
