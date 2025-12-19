# coding:utf-8
import inspect


def cannot_encode(obj):
    """
    判断对象是否支持 encode
    """
    if inspect.isroutine(obj):
        return True
    elif inspect.isclass(obj):
        return True
    elif inspect.ismodule(obj):
        return True
    elif inspect.iscode(obj):
        return True
    elif inspect.isasyncgen(obj):
        return True
    elif inspect.isasyncgenfunction(obj):
        return True
    elif inspect.isawaitable(obj):
        return True
    elif inspect.iscoroutine(obj):
        return True
    elif inspect.isdatadescriptor(obj):
        return True
    elif inspect.isframe(obj):
        return True
    elif inspect.isgenerator(obj):
        return True
    elif inspect.isgetsetdescriptor(obj):
        return True
    elif inspect.istraceback(obj):
        return True
    elif inspect.ismethodwrapper(obj):
        return True
    return False
