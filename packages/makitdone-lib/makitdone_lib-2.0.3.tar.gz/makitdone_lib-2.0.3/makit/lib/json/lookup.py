# coding:utf-8

"""

语法：
/store/book
/store/book(^version)   # book that has no version
/store/book(price>10)
/store/book(price>10).title
/store/book(title, price>10)
/store/book[0]
/store/book[0:2]
/store/book[0:10:2]..
"""
import re

from makit.lib.validate import check


class Json:
    def __init__(self, data):
        self.data = data

    def all(self, expr: str):
        result = []

        pattern_index = re.compile(f'^\[(\d+)]')
        pattern_slice = re.compile(f'^\[(?P<start>\d+):(?P<end>\d+)]')
        pattern_filter = re.compile('^\(([^()\[\]]+)\)')
        pattern_node = re.compile(r'^([a-zA-Z0-9_]+)')

        def parse(d, _expr: str):
            if not _expr:
                result.append(d)
                return
            if _expr.startswith('//'):
                return parse(d, _expr[2:])
            elif _expr.startswith('/'):
                return parse(d, _expr[1:])
            # 索引
            match = pattern_index.match(_expr)
            if match:
                index = int(match.group(1))
                return parse(d[index], _expr[match.end(1) + 1:])
            # 切片
            match = pattern_slice.match(_expr)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                return parse(d[start:end], _expr[match.end(2) + 1:])
            if isinstance(d, list):
                for item in d:
                    parse(item, _expr)
                return
            match = pattern_node.match(_expr)
            if match:
                node = match.group(1)
                return parse(d[node], _expr[len(node):])
            # 过滤
            match = pattern_filter.match(_expr)
            if match:
                filter_expr = match.group(1)
                parts = filter_expr.split(',')
                ok = True
                for part in parts:
                    part = part.strip()
                    _not = part[0] == '^'
                    ok = ok and self._validate(d, part[1:] if _not else part)
                    if _not:
                        ok = not ok
                if ok:
                    return parse(d, _expr[match.end(1) + 1:])
            else:
                raise Exception('invalid path')

        parse(self.data, expr)

        return result

    def first(self, expr: str):
        result = self.all(expr)
        if result:
            return result[0]
        return None

    @classmethod
    def _validate(cls, data: dict, expr: str):
        match = re.match(r'^(?P<prop>[a-zA-Z0-9_]+)\s*((?P<token>[><=]+)?\s*(?P<value>.+))?', expr)
        if match:
            kw = match.groupdict()
            prop = kw['prop']
            token = kw.get('token')
            expected_value: str = kw.get('value') or ''
            expected_value = expected_value.strip('"').strip("'")
            value = data.get(prop)
            if not token:
                return prop in data
            elif token == '=':
                kwargs = dict()
                kwargs[prop] = expected_value
                return check(data, **kwargs)
            else:
                return eval(f'{value}{token}{expected_value}')
        else:
            raise Exception(f'invalid expression: {expr}')

    def __getattr__(self, item):
        if isinstance(self.data, dict):
            value = self.data.get(item)
            return Json(value)
        else:
            return getattr(self.data, item)

    def __getitem__(self, item):
        if isinstance(self.data, dict):
            value = self.data.get(item)
        else:
            value = self.data[item]
        if isinstance(value, (dict, list)):
            return Json(value)
        return value

    def __setitem__(self, key, value):
        if isinstance(self.data, dict):
            self.data[key] = value
        else:
            self.data[key] = value
