# coding:utf-8

from makit.lib import inspect


class BaseCallback:
    def __init__(self, func, count=None):
        self.func = func
        self.count = count
        self.next = None


class Callback(BaseCallback):

    def __call__(self, *args, **kwargs):
        if self.count is not None:
            self.count -= 1
        inspect.run(self.func, *args, **kwargs)

    def __repr__(self):
        return f'<Callback {self.func.__name__}>'


class AsyncCallback(BaseCallback):
    async def __call__(self, *args, **kwargs):
        if self.count is not None:
            self.count -= 1
        return await inspect.async_run(self.func, *args, **kwargs)

    def __repr__(self):
        return f'<AsyncCallback {self.func.__name__}>'


class Event:
    """
    事件
    """
    __callback_class__ = Callback

    def __init__(self):
        self._callbacks = []

    def clear(self):
        """
        清空所有事件回调
        :return:
        """
        self._callbacks.clear()

    def trigger(self, *args, **kwargs):
        """
        触发事件回调
        :param args:
        :param kwargs:
        :return:
        """
        for callback in [*self._callbacks]:
            callback(*args, **kwargs)
            if callback.count == 0:
                self._callbacks.remove(callback)

    def iter_trigger(self, *args, **kwargs):
        """
        迭代方式触发事件回调，允许根据需要中断
        :param args:
        :param kwargs:
        :return:
        """
        for callback in [*self._callbacks]:
            result = callback(*args, **kwargs)
            if callback.count == 0:
                self._callbacks.remove(callback)
            yield result

    def __add__(self, other):
        if isinstance(other, tuple):
            callback, count = other
        else:
            callback, count = other, None
        assert callable(callback), f'Event callback must be callable: {other}'
        assert count is None or isinstance(count, int), 'Event callback count must be None or an int value.'
        self._callbacks.append(self.__callback_class__(*other))
        return self

    def __call__(self, count=None):
        def deco(func):
            self._callbacks.append(self.__callback_class__(func, count))
            return func

        return deco


class AsyncEvent(Event):
    __callback_class__ = AsyncCallback

    async def trigger(self, *args, **kwargs):
        """
        触发事件回调
        :param args:
        :param kwargs:
        :return:
        """
        for callback in [*self._callbacks]:
            await callback(*args, **kwargs)
            if callback.count == 0:
                self._callbacks.remove(callback)

    async def iter_trigger(self, *args, **kwargs):
        """
        迭代方式触发事件回调，允许根据需要中断
        :param args:
        :param kwargs:
        :return:
        """
        for callback in [*self._callbacks]:
            result = await callback(*args, **kwargs)
            if callback.count == 0:
                self._callbacks.remove(callback)
            yield result
