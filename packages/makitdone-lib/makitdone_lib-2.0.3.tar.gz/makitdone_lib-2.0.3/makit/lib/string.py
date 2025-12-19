# coding:utf-8


import re
import uuid
from string import *


def int_values(s):
    """
    获取字符串中所有的整数
    :param s:
    :return:
    """
    _list = re.compile(r'\d+').findall(s)
    return [int(n) for n in _list]


def float_values(s):
    """
    获取字符串中所有的浮点数
    :param s:
    :return:
    """
    _list = re.compile(r'\d+(?:\.\d+)?').findall(s)
    return [float(n) for n in _list]


def camel(s):
    """
    将下划线字符串转为驼峰风格
    """
    s = ''.join([s.title() if s else '_' for s in s.split('_')])
    return s


def uncamel(s, sep='_'):
    """
    将驼峰风格字符串转换为下划线风格
    :param s:
    :param sep:
    :return:
    """
    s = re.sub('([a-z]+)(?=[A-Z])', r'\1' + sep, s)
    return s.lower()


def safe_join(s, *objects) -> str:
    """
    将多个字符串连接成一个字符串，但会忽略None和空字符串
    Concatenate any number of strings. It will ignore None.
    :param s:
    :param objects:
    :return:
    """

    def iterate():
        for item in objects:
            if item is None or str(item) == '':
                continue
            yield item

    return s.join(iterate())


def split_at(s, sep=None, *positions):
    """
    Split the string at specified positions.
    :param s:
    :param sep: The delimiter according which to split the string.
    :param positions: split positions
    :return:
    """
    parts = s.split(sep)
    result, length = [], len(parts)
    positions = sorted(set([min(length, max(0, i if i >= 0 else length + i)) for i in positions] + [0, length]))
    prev = positions[0]
    for pos in positions:
        if pos <= prev:
            continue
        result.append(sep.join(parts[prev:pos]))
        prev = pos
    return result


def short_id():
    """
    生成短ID
    :return:
    """
    s = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
    buffer = []
    chars = digits + ascii_letters
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(s[start:end], 16)
        buffer.append(chars[val % 62])
    return "".join(buffer)


def is_email(s: str):
    pattern = re.compile(r'^\w+([-.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')
    return pattern.match(s) is not None


def is_phone_number():
    pass


def find_phone_number():
    pass
