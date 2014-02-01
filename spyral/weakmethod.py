import weakref

class WeakMethodBound :
    def __init__( self , f ) :
        self.f = f.im_func
        self.c = weakref.ref( f.im_self )
    def _f(self):
        return self.f
    method = property(_f)
    def __call__( self , *arg ) :
        if self.c() == None :
            raise TypeError , 'Method called on dead object'
        return apply( self.f , ( self.c() , ) + arg )

class WeakMethodFree :
    def __init__( self , f ) :
        self.f = weakref.ref( f )
    def _f(self):
        return self.f()
    method = property(_f)
    def __call__( self , *arg ) :
        if self.f() == None :
            raise TypeError , 'Function no longer exist'
        return apply( self.f() , arg )

def WeakMethod( f ) :
    try:
        f.im_func
    except AttributeError :
        return f
    return WeakMethodBound( f )