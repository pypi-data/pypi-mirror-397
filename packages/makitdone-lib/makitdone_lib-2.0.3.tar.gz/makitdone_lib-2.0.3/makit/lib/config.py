# coding:utf-8

import inspect

from makit.lib.errors import NotSupportError
from makit.lib.ospath import Path


class Config:
    def __init__(self, obj):
        if inspect.ismodule(obj) or isinstance(obj, dict):
            self._obj = obj
        elif isinstance(obj, Config):
            self._obj = obj._obj
        else:
            raise InvalidConfigError('config object can only be a module or dict')
        self._default = None

    def get(self, item, default=None):
        value = self.__getitem__(item)
        if value is None:
            return default
        return value

    def extend(self, obj):
        """
        扩展配置，注意与use有所不同，
        :param obj:
        :return: 返回一个新配置
        """
        if not obj:
            return self
        cfg = Config(obj)
        cfg._default = self
        return cfg

    def use(self, obj):
        """
        应用配置
        :param obj:
        :return:
        """
        if obj:
            self._obj = obj
        return self

    def read_file(self, filename: str, extend=False):
        """
        从文件读取配置
        :param filename:
        :param extend: 是否扩展配置
        :return:
        """
        path = Path(filename)
        if not path.isfile:
            raise InvalidConfigError(f'not a file: {filename}')
        if path.extname in ['.yml', '.yaml']:
            import yaml
            with open(filename, 'r') as r:
                data = yaml.load(r, yaml.Loader)
                return self.use(data)
        elif path.extname in ['.ini', '.cfg']:
            import configparser
            parser = configparser.ConfigParser()
            data = parser.read(filename)
            if extend:
                return self.extend(data)
            return self.use(data)
        else:
            raise NotSupportError(f'unsupported file type: {path.extname}')

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, item):
        if inspect.ismodule(self._obj):
            value = getattr(self._obj, item, None)
        else:
            value = self._obj.get(item)
        if value is None and self._default:
            value = getattr(self._default, item)
        if isinstance(value, dict) or inspect.ismodule(value):
            return Config(value)
        return value

    def items(self):
        if isinstance(self._obj, dict):
            return self._obj.items()
        else:
            raise NotSupportError(f'not a dict: {self._obj}')


class InvalidConfigError(Exception):
    """"""
