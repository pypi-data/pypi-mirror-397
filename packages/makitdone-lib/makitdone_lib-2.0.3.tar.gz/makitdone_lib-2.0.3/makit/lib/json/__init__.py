# coding:utf-8

from makit.lib.json.decode import JsonDecoder
from makit.lib.json.encode import *
from makit.lib.json.lookup import Json

__all__ = [
    'Json',
    'loads',
    'predumps',
    'dumps',
    'lookup',
    'JsonDecoder'
]


def loads(s: str, model=None, decoder=JsonDecoder):
    """
    将json格式字符串反序列化，支持直接转换为实例对象
    """
    return decoder(model=model).decode(s)


def bind(model_class, data: list | dict):
    """
    将数据绑定到模型，并得到实例对象，适用于没有复杂初始化过程的类型
    :param model_class:
    :param data:
    :return:
    """
    assert inspect.isclass(model_class), "not a class"
    instance = object.__new__(model_class)
    annotations = model_class.__annotations__
    if annotations:
        for name, v in annotations.items():
            if name not in data:
                continue
            value = data.get(name)
            if inspect.isclass(v) and isinstance(value, (list, dict)):
                value = bind(v, value)
            setattr(instance, name, value)
    else:
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
    return instance


def lookup(data, path: str, findall=False):
    """
    根据路径表达式查找数据
    :param data:
    :param path:
    :param findall: 总是返回list
    :return:
    """
    result = Json(data).all(path)
    if findall:
        return result
    if len(result) == 0:
        return None
    elif len(result) == 1:
        return result[0]
    return result
