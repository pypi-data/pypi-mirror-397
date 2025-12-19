# coding:utf-8

import threading
from functools import wraps


def synchronized(func):
    """
    装饰器，用于方法加锁
    :param func:
    :return:
    """
    func.__lock__ = threading.Lock()

    @wraps(func)
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


def singleton(cls):
    if not hasattr(cls, '_instance_lock'):
        cls._instance_lock = threading.Lock()

    _old_new = getattr(cls, '__new__')

    def _new_(c, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(c, '_instance'):
                    cls._instance = _old_new(cls, *args, **kwargs)
        return cls._instance

    setattr(cls, '__new__', _new_)

    return cls
