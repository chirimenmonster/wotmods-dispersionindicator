

def overrideMethod(cls, method):
    def decorator(handler):
        orig = getattr(cls, method)
        newm = lambda *args, **kwargs: handler(orig, *args, **kwargs)
        if type(orig) is not property:
            setattr(cls, method, newm)
        else:
            setattr(cls, method, property(newm))
    return decorator


def overrideClassMethod(cls, method):
    def decorator(handler):
        orig = getattr(cls, method)
        newm = classmethod(lambda *args, **kwargs: handler(orig, *args, **kwargs))
        if type(orig) is not property:
            setattr(cls, method, newm)
        else:
            setattr(cls, method, property(newm))
    return decorator
