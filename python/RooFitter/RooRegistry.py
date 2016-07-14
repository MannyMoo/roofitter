'''A registry of RooFit objects so you don't need to keep track
of all variables initialised in python.'''

class RooRegistry(set) :
    '''A registry of RooFit objects so you don't need to keep track
    of all variables initialised in python.'''

    def __init__(self, *objs) :
        set.__init__(self, objs)
    

defaultRegistry = RooRegistry()
