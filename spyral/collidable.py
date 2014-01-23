class Collidable(object):
    
    def init_collidable(self, rect):
        """
        Initializes the information required for a collidable
        """
        self.rect = rect
    
    def collide_point(self, point):
        """
        Determines if this collidable is overlapping with an absolute point.
        """
        pass
        
    def collide_rect(self, rect):
        """
        Determines if this collidable is overlapping with an absolute rectangle.
        """
        pass
        
    def collide_collidable(self, other):
        """
        Determines if this collidable is overlapping with another collidable.
        """
        pass
        