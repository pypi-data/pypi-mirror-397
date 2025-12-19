# coding:utf-8

import argparse
import asyncio
import typing as t

from makit.lib import inspect
from makit.lib.inspect import Method


class AppCommand:

    def __init__(self, prog_name=None):
        self.default_command = None
        self.parser = parser = argparse.ArgumentParser(prog=prog_name)
        self.subparsers = parser.add_subparsers(dest='command')
        self.handlers: t.Dict[str, Method] = dict()

    def run(self):
        """
        开始执行
        :return:
        """
        try:
            args = self.parser.parse_args()
            kwargs = args.__dict__
            command = kwargs.pop('command', None) or self.default_command
            handler = self.handlers.get(command)
            if handler:
                if handler.is_coroutine():
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(inspect.async_run(handler, **kwargs))
                else:
                    inspect.run(handler, **kwargs)
        except Exception as e:
            print(e)

    def command(self, default=False):
        """
        命令装饰器
        :param default: 是否默认命令
        :return:
        """

        def deco(f):
            method = inspect.Method(f)
            if default:
                self.default_command = method.name
            parser = self.subparsers.add_parser(method.name, help=method.description)
            for arg in method.args:
                self.__add_parser_argument(parser, arg, default)
            for name, arg in method.kwargs.items():
                self.__add_parser_argument(parser, arg, default)

            self.handlers.setdefault(method.name, method)
            return f

        return deco

    def __add_parser_argument(self, parser, arg, default):
        if default:
            self.parser.add_argument(
                arg.name if arg.required else '--' + arg.name,
                type=arg.type,
                help=arg.description,
                default=arg.default,
            )
        parser.add_argument(
            arg.name if arg.required else '--' + arg.name,
            type=arg.type,
            help=arg.description,
            default=arg.default,
        )
