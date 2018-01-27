""" XFW Library (c) https://modxvm.com 2013-2018 """

#from logger import *

#####################################################################
# EventHook

class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self.__handlers:
            self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler


#####################################################################
# Register events

def _RegisterEvent(handler, cls, method, prepend=False):
    evt = '__event_%i_%s' % ((1 if prepend else 0), method)
    if hasattr(cls, evt):
        e = getattr(cls, evt)
    else:
        newm = '__orig_%i_%s' % ((1 if prepend else 0), method)
        setattr(cls, evt, EventHook())
        setattr(cls, newm, getattr(cls, method))
        e = getattr(cls, evt)
        m = getattr(cls, newm)
        l = lambda *a, **k: __event_handler(prepend, e, m, *a, **k)
        l.__name__ = method
        setattr(cls, method, l)
    e += handler

def __event_handler(prepend, e, m, *a, **k):
    try:
        if prepend:
            e.fire(*a, **k)
            r = m(*a, **k)
        else:
            r = m(*a, **k)
            e.fire(*a, **k)
        return r
    except:
        logtrace(__file__)

def _override(cls, method, newm):
    orig = getattr(cls, method)
    if type(orig) is not property:
        setattr(cls, method, newm)
    else:
        setattr(cls, method, property(newm))

def _OverrideMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = lambda *a, **k: handler(orig, *a, **k)
    newm.__name__ = method
    _override(cls, method, newm)

def _OverrideStaticMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = staticmethod(lambda *a, **k: handler(orig, *a, **k))
    _override(cls, method, newm)

def _OverrideClassMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = classmethod(lambda *a, **k: handler(orig, *a, **k))
    _override(cls, method, newm)


#####################################################################
# Decorators

def _hook_decorator(func):
    def decorator1(*a, **k):
        def decorator2(handler):
            func(handler, *a, **k)
        return decorator2
    return decorator1

registerEvent = _hook_decorator(_RegisterEvent)
overrideMethod = _hook_decorator(_OverrideMethod)
overrideStaticMethod = _hook_decorator(_OverrideStaticMethod)
overrideClassMethod = _hook_decorator(_OverrideClassMethod)
