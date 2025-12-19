# coding:utf-8
import inspect
import json
import typing as t
from datetime import datetime, date, time
from uuid import UUID

from makit.lib import inspect
from makit.lib.json._base import cannot_encode


def _is_reference(obj):
    if inspect.is_basictype(obj):
        return False
    return not cannot_encode(obj)


def predumps(o, safe=True, datetime_format=None, date_format=None, time_format=None, omitempty=True,
             ign_protected=True):
    def __predumps(obj, safe_break, makers=None) -> t.Any:
        if makers is None:
            makers = []
        obj_id = id(obj)
        if safe_break > 0 and obj_id in makers and _is_reference(obj):
            safe_break = safe_break - 1
            if safe_break < 0 or makers.count(obj_id) > safe_break >= 0:  # 如果采用安全模式，遇到循环引用则处理为None
                return None
        makers.append(obj_id)
        if obj is None:
            return obj
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, datetime):
            if datetime_format:
                return obj.strftime(datetime_format)
            return str(obj)
        elif isinstance(obj, date):
            if date_format:
                return obj.strftime(date_format)
            return str(obj)
        elif isinstance(obj, time):
            if time_format:
                return obj.strftime(time_format)
            return str(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, list):
            return [__predumps(item, safe_break, list(makers)) for item in obj]
        elif isinstance(obj, dict):
            return {
                k: __predumps(v, safe_break, list(makers))
                for k, v in obj.items()
                if v is not None or (v is None and not omitempty)
            }
        elif hasattr(obj, 'encode') and inspect.isroutine(obj.encode):
            return obj.encode()
        elif hasattr(obj, '__encode__') and inspect.isroutine(obj.__encode__):
            return obj.__encode__()
        elif cannot_encode(obj):
            raise EncodeError(f'Cannot encode obj for type: {obj.__class__.__name__}')
        else:
            obj_class = obj.__class__
            annotations = obj_class.__annotations__
            if annotations:
                data = dict()
                for key, _ in annotations.items():
                    v = getattr(obj, key)
                    v = __predumps(v, safe_break, list(makers))
                    if v is None and omitempty:
                        continue
                    data[key] = v
                return data
            else:
                data = dict()
                for name in dir(obj):
                    value = getattr(obj, name, None)
                    if callable(value) or name.startswith('__') or (name.startswith('_') and ign_protected):
                        continue
                    value = __predumps(value, safe_break, list(makers))
                    if not value and omitempty:
                        continue
                    data[name] = value
                return data

    return __predumps(o, 1 if safe else 0)


def dumps(
        obj,
        ensure_ascii=True,
        debug=False,
        safe=True,
        omitempty=True,  # 如果值可以判断为False，则予以忽略
        ign_protected=True,
        datetime_format=None,
        date_format=None,
        time_format=None,
        **kwargs
):
    """
    将对象序列化为json格式的字符串
    :param obj: 被序列化对象
    :param ensure_ascii: 是否确保ascii编码
    :param debug: 是否调试，如果为True, ensure_ascii会被强设为False
    :param safe: 是否采用安全模式，安全模式下会处理循环引用问题
    :param omitempty: 是否忽略空值，None,空字符串，0，False等可以被判定为False的值在这里均视为空值
    :param ign_protected:
    :param datetime_format:
    :param date_format:
    :param time_format:
    :param kwargs:
    :return:
    """
    data = predumps(
        obj,
        safe=safe,
        omitempty=omitempty,
        datetime_format=datetime_format,
        date_format=date_format,
        time_format=time_format,
        ign_protected=ign_protected,
    )
    if debug:
        ensure_ascii = False
    return json.dumps(data, ensure_ascii=ensure_ascii, **kwargs)


class EncodeError(Exception):
    """"""
