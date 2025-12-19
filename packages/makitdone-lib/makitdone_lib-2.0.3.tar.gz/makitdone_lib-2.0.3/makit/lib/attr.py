# coding:utf-8
import asyncio
import re

from makit.lib import inspect


class Attr:
    """
    描述器基类
    """

    def __init__(
            self,
            default=None,
            validators=None,
            nullable=True,
            readonly=False
    ):
        self.name = None
        self._default = default
        self.validators = validators or []
        self.nullable = nullable
        self.readonly = readonly
        self._changed_callbacks = []

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, '__' + self.name, None)

    def __set__(self, instance, value):
        if self.readonly:
            raise Exception('attribute readonly!')
        old_value = getattr(instance, '__' + self.name, None)
        value = self.convert_value(instance, value)
        self.validate(instance, value)
        changed = old_value == value
        setattr(instance, '__' + self.name, value)
        if changed:
            for callback in self._changed_callbacks:
                if inspect.iscoroutinefunction(callback):
                    loop = getattr(instance, 'loop', asyncio.new_event_loop())
                    loop.run_until_complete(callback(instance, old_value, value))
                else:
                    callback(instance, old_value, value)

    def convert_value(self, instance, value):
        return value

    def on_changed(self):

        def deco(f):
            self._changed_callbacks.append(f)

            return f

        return deco

    def validate(self, instance, value):
        errors = getattr(instance, 'errors')  # 如果实例没有errors，则校验抛异常
        if self.nullable and value is None:
            return True
        if not self.nullable and value is None:
            if self.name:
                message = f'"{self.name}" should not be None!'
            else:
                message = 'Invalid value: None'
            if errors:
                instance.errors.append(message)
            else:
                raise Exception(message)
        for v in self.validators:
            if hasattr(v, 'validate'):
                v = v.validate
            if callable(v):
                try:
                    result = inspect.run(v, value, instance=instance)
                    if not result:
                        return False
                except Exception as e:
                    if errors:
                        instance.errors.append(f'"{self.name}" {e}' if self.name else str(e))
                    else:
                        raise e
        return len(errors) == 0


class String(Attr):
    def __init__(self, prefix=None, suffix=None, pattern=None, **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix
        self.suffix = suffix
        self.pattern = pattern
        if self.prefix:
            self.validators.append(lambda v: should_startswith(v, self.prefix))
        if self.suffix:
            self.validators.append(lambda v: should_endswith(v, self.suffix))
        if self.pattern:
            self.validators.append(lambda v: should_match(v, self.pattern))


class Number(Attr):

    def __init__(self, default=None, min=None, max=None, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_value = min
        self.max_value = max
        if min is not None:
            self.validators.append(lambda v: v >= self.min_value)
        if max is not None:
            self.validators.append(lambda v: v <= self.max_value)


class Int(Attr):
    def convert_value(self, instance, value):
        if isinstance(value, str):
            if re.match(r'^\d+$', value):
                return int(value)
        return value


class Float(Attr):
    def convert_value(self, instance, value):
        if isinstance(value, str):
            if re.match(r'^\d+(\.\d+)?$', value):
                return float(value)
        return value


class Boolean(Attr):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def convert_value(self, instance, value):
        if isinstance(value, str):
            value = value.lower()
            if value in ('true', '1'):
                return True
            elif value in ('false', '0'):
                return False
        elif isinstance(value, bool):
            return value
        raise InvalidAttrValueError(instance.__class__, self, value)


class Validator:
    def validate(self, value, instance=None):
        raise NotImplementedError


def should_startswith(value: str, prefixes):
    if not value.startswith(prefixes):
        raise Exception(f'should startswith: {prefixes}')


def should_endswith(value: str, suffix):
    if not value.endswith(suffix):
        raise Exception(f'should endswith: {suffix}')


def should_match(value: str, pattern):
    if re.match(pattern, value) is None:
        raise Exception(f'should match: {pattern}')


def not_none(value):
    return value is not None


# endregion


class InvalidAttrValueError(Exception):
    def __init__(self, model, attr, value):
        self.model = model
        self.attr = attr
        self.value = value
        super().__init__(f'invalid attr value for model "{model.__name__}.{attr.name}": {value}')


class InvalidValidatorError(Exception):
    def __init__(self, model, attr, validator):
        self.model = model
        self.attr = attr
        self.validator = validator
