# coding:utf-8
import asyncio
import inspect
import io
import re
import sys
import traceback
import typing as t
from functools import cached_property
from inspect import *

from docstring_parser import parse

from makit.lib import py
from makit.lib.inspect._common import obj_name, get_class


class Argument:
    def __init__(self, name, default=None, arg_type=None, kwonly=False, required=False):
        self.name = name
        self.default = default
        self.__required = required
        if not arg_type and not self.__required:
            arg_type = type(default)
        self.type = arg_type
        self.kwonly = kwonly
        self.description = None

    @property
    def required(self):
        return self.__required

    def __repr__(self):
        if self.required:
            return f'<Argument {self.name}>'
        else:
            return f'<Argument {self.name}={self.default}>'


class Method:
    def __init__(self, routine):
        self.routine = routine
        self._args: t.List[Argument] = []
        self._kwargs: t.Dict[str, Argument] = {}
        self.allow_args = False
        self.allow_kwargs = False
        self.__description = None
        self.__detail = None
        self._cls = None
        self.module = getmodule(routine)
        self.__parsed = False
        self._doc_parser = None

    @cached_property
    def name(self):
        return obj_name(self.routine)

    @cached_property
    def description(self):
        if not self.__parsed:
            self.__parse()
        return self.__description

    @cached_property
    def detail(self):
        if not self.__parsed:
            self.__parse()
        return self.__detail

    @cached_property
    def cls(self):
        if not self._cls:
            self._cls = get_class(self.routine, module=self.module)
        return self._cls

    @cached_property
    def is_classmethod(self):
        if self.cls:
            o = object.__new__(self.cls)
            f = getattr(o, self.routine.__name__)
            f_str = str(f)
            return re.match(r'<bound method [a-zA-Z_0-9]+\.[a-zA-Z0-9_]+ of <class', f_str) is not None
        return False

    @cached_property
    def is_module_function(self):
        return re.match(r'<function [a-zA-Z_][a-zA-Z0-9_]* at', str(self.routine)) is not None

    @cached_property
    def is_staticmethod(self):
        if self.cls:
            pattern = re.compile(r'<function [a-zA-Z_0-9]+\.[a-zA-Z_][a-zA-Z0-9_]* at')
            f_str = str(self.routine)
            match = pattern.match(f_str)
            if match is None:
                return False
            o = object.__new__(self.cls)
            f = getattr(o, self.routine.__name__)
            f_str = str(f)
            match = pattern.match(f_str)
            return match is not None
        return False

    @cached_property
    def is_instance_method(self):
        if self.cls:
            f_str = str(self.routine)
            return re.match(r'<bound method .+ of <.+ object at 0x[a-zA-Z0-9]+>>', f_str) is not None
        return False

    @cached_property
    def args(self):
        if not self.__parsed:
            self.__parse()
        return self._args

    @cached_property
    def kwargs(self):
        if not self.__parsed:
            self.__parse()
        return self._kwargs

    @property
    def allargs(self):
        for arg in self.args:
            yield arg
        for _, arg in self.kwargs.items():
            yield arg

    def is_coroutine(self):
        return inspect.iscoroutinefunction(self.routine)

    def __parse(self):
        self.__parse_args()
        self.__parse_doc()

    def __parse_args(self):
        self.__parsed = True
        full_args = inspect.getfullargspec(self.routine)
        self.allow_args = full_args.varargs is not None
        self.allow_kwargs = full_args.varkw is not None
        if full_args.defaults:
            required_args = full_args.args[:-len(full_args.defaults)]
            optional_kwargs = zip(reversed(full_args.args), reversed(full_args.defaults))
        else:
            required_args, optional_kwargs = full_args.args, {}
        for name in required_args:
            self._args.append(Argument(name, required=True, arg_type=full_args.annotations.get(name)))
        for name, value in optional_kwargs:
            self._kwargs[name] = Argument(name, default=value, required=False, arg_type=full_args.annotations.get(name))
        for name in full_args.kwonlyargs:
            default = full_args.kwonlydefaults.get(name)
            arg_type = full_args.annotations.get(name)
            self._kwargs[name] = Argument(name, default=default, arg_type=arg_type, kwonly=True)
        return self

    def __parse_doc(self):
        info = parse(self.routine.__doc__)
        self.__description = info.short_description
        self.__detail = info.description
        for param in info.params:
            for arg in self._args:
                if arg.name == param.arg_name:
                    arg.description = param.description
                    break
            for _, arg in self._kwargs.items():
                if arg.name == param.arg_name:
                    arg.description = param.description
                    break
        return self

    def __call__(self, *args, **kwargs):
        args = list(args)
        if self.routine.__name__ == '__init__':
            instance = object.__new__(self.cls)
            args.insert(0, instance)
        actual_args, actual_kwargs = [], {}
        for name, arg in self.kwargs.items():
            value = kwargs.pop(name, None)
            actual_kwargs[name] = value
        for arg in self.args:
            if arg.name in kwargs:
                actual_args.append(kwargs.pop(arg.name))
            else:
                if args:
                    value = args.pop(0)
                    actual_args.append(value)
        if self.allow_args:
            actual_args.extend(args)
        if self.allow_kwargs:
            actual_kwargs.update(kwargs)
        return self.routine(*actual_args, **actual_kwargs)


def run(f, *args, **kwargs):
    """
    调用函数，可正确处理参数，不会因为参数给多或者顺序错乱而导致错误
    :param f:
    :param args:
    :param kwargs:
    :return:
    """
    if not isinstance(f, Method):
        f = Method(f)
    return f(*args, **kwargs)


async def async_run(f, *args, **kwargs):
    if not isinstance(f, Method):
        f = Method(f)
    result = f(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result


class CallInfo:
    def __init__(self, frame):
        self.__frame = frame
        self._filename = None
        self._lineno = None
        self._caller = None

    @property
    def filename(self):
        return self.__frame.f_code.co_filename

    @property
    def lineno(self):
        return self.__frame.f_lineno

    @property
    def func_name(self):
        return self.__frame.f_code.co_name

    @property
    def caller(self):
        frame_str = str(self.__frame)
        caller_name = re.findall(r'code (.+)>', frame_str)[0]
        f_locals = self.__frame.f_locals
        if 'self' in f_locals:
            instance = f_locals.get('self')
            return getattr(instance, caller_name)
        elif 'cls' in f_locals:
            cls = f_locals.get('cls')
            return getattr(cls, caller_name)

    @property
    def module(self):
        return py.import_file(self.filename, raise_error=False)

    def get_stack(self):
        sio = io.StringIO()
        sio.write('Stack (most recent call last):\n')
        traceback.print_stack(self.__frame, file=sio)
        stack_info = sio.getvalue()
        if stack_info[-1] == '\n':
            stack_info = stack_info[:-1]
        sio.close()
        return stack_info

    def flat(self):
        return self.filename, self.module, self.func_name, self.lineno, self.get_stack()


def parse_caller(invoked_file):
    """
    用于解析函数调用者信息
    :param invoked_file: 被调用函数所在的py文件路径
    :return:
    """
    f = getattr(sys, '_getframe')(0)
    found, changed = None, False
    while f:
        code_file = f.f_code.co_filename
        if code_file == invoked_file and found is None:
            found = True
        if found and code_file != invoked_file:
            changed = True
        if found and changed:
            break
        f = f.f_back
    if not f:
        return None
    return CallInfo(f)
