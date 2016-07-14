from RooRegistry import defaultRegistry

def RooNew(cls, *args, **kwargs) :
    if not 'registry' in kwargs or not kwargs['registry'] :
        kwargs['registry'] = defaultRegistry
    registry = kwargs['registry']

    if 'addToRegistry' in kwargs :
        addToRegistry = kwargs['addToRegistry']
        del kwargs['addToRegistry']
    else :
        addToRegistry = True
        
    if isinstance(cls, str) :
        cls = __import__(cls)
        
    if hasattr(cls, 'new') and \
       (not 'useNew' in kwargs or not kwargs['useNew']) :
        try :
            # Try passing the registry to the new object's new
            # method first. Else remove it from kwargs.
            obj = cls.new(*args, **kwargs)
        except TypeError :
            del kwargs['registry']
            obj = cls.new(*args, **kwargs)
    else :
        del kwargs['registry']
        try :
            obj = cls(*args, **kwargs)
        except Exception as excpt :
            raise excpt.__class__(excpt.message + '''
Constructor failed with args: {0!r}, kwargs: {1!r}'''.format(args, kwargs))
                                  
    if addToRegistry :
        registry.add(obj)
    return obj
