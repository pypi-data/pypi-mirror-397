# coding:utf-8
import json
import re
from json import JSONDecoder

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)


class JsonDecoder(JSONDecoder):
    """"""

    def __init__(self, model=None, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.kwargs = kwargs

    def decode(self, s: str, _w=WHITESPACE):
        data = json.loads(s, **self.kwargs)
        if self.model is None:
            return data
        instance = object.__new__(self.model)
        annotations = self.model.__annotations__
        if annotations:
            for name, v in annotations.items():
                setattr(instance, name, data.get(name))
        else:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
        return instance
