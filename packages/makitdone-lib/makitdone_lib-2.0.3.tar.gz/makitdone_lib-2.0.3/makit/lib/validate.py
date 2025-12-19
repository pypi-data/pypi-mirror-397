# coding:utf-8

import re


def check(o, *args, **kwargs):
    r = True
    for k, v in kwargs.items():
        pattern = re.compile(r'(?P<attr>[a-zA-Z][a-zA-Z0-9]*_?[a-zA-Z0-9]+)(__(?P<not>not_)?(?P<method>\w+))?')
        d = pattern.match(k).groupdict()
        attr = d.get('attr')
        _not = d.get('not') is not None
        method = d.get('method')
        if isinstance(o, dict):
            value = o.get(attr)
        else:
            value = getattr(o, attr, None)
        if not method:
            result = value == v
        elif method == 'in':
            result = value in v
        else:
            if method.startswith('i') and isinstance(value, str):
                value = value.lower()
                v = v.lower()
                method = method[1:]
            if method in ['contains', 'has']:
                if isinstance(v, list):
                    result = all([item in value for item in v])
                else:
                    result = v in value
            elif method in ['containsany', 'hasany']:
                if isinstance(v, list):
                    result = any([item in value for item in v])
                else:
                    result = v in value
            elif method in ['startswith', 'prefix']:
                result = value.startswith(v)
            elif method in ['endswith', 'suffix']:
                result = value.endswith(v)
            elif method == 'matches':
                result = re.match(re.compile(v), value) is not None
            elif method in ['none', 'isnull', 'isnone', 'null']:
                result = value is None and v
            elif method == 'lt':
                result = value < v
            elif method == 'gt':
                result = value > v
            elif method == 'le':
                result = value <= v
            elif method == 'ge':
                result = value >= v
            else:
                raise RuntimeError(f'Do not support method: {method}')
        if _not:
            result = not result
        r = r and result
    return r
