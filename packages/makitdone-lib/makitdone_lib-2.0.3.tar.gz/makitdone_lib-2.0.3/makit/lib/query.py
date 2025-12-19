# coding:utf-8
import typing as t

from makit.lib import validate

T = t.TypeVar('T')


class _Index:
    """
    数据索引
    """

    def __init__(self, key):
        self.key = key
        self.start_index = 0
        self.end_index = None


class ListQuery(t.Generic[T]):
    """
    对list数据执行类似于orm的操作，不适用于大数据量，一般配合缓存适用
    """

    def __init__(self, data: t.List[T]):
        self.data = data
        self._select_fields = []
        self._conditions = dict()
        self._indexes = []  # 索引

    def where(self, **kwargs):
        """
        按给定条件查询数据
        :param kwargs:
        :return:
        """
        clone = self._clone()
        clone._conditions.update(kwargs)
        return clone

    filter = where

    def with_index(self, *fields):
        clone = self._clone()
        for key in fields:
            clone._indexes.append(_Index(key))
        return clone

    def all(self):
        """
        选择所有符合条件的对象
        :return:
        """
        return list(self.__execute(self.data))

    def value_list(self, *fields):
        clone = self._clone()
        clone._select_fields.extend(fields)
        return clone

    def values(self, *fields):
        clone = self._clone()
        clone._select_fields.extend(fields)
        return clone

    def first(self):
        """
        选择第一个符合条件的对象
        :return:
        """
        for item in self.__execute(self.data):
            return item

    def last(self):
        """
        选择最后一个符合条件的对象
        :return:
        """
        for item in self.__execute(reversed(self.data)):
            return item

    def count(self):
        return len(self.all())

    def __execute(self, data):
        for item in data:
            if validate.check(item, **self._conditions):
                yield item

    def _clone(self):
        clone = ListQuery(self.data)
        clone._conditions = dict(**self._conditions)
        return clone
