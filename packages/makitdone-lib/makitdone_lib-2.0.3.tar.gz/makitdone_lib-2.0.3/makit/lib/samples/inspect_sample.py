# coding:utf-8

from makit.lib import inspect


def serve(env, host='127.0.0.1', port=8000):
    print(f'Serving on {host}:{port}, env：{env}')


# 即使提供了多余的参数，也能正常执行
inspect.run(serve, env='dev', config=dict())

# 函数参数信息和文档信息
method = inspect.Method(serve)

# 遍历必需参数
for arg in method.args:
    print(arg.name)
    print(arg.required)
    print(arg.default)
    print(arg.description)

# 遍历可选参数
for name, arg in method.kwargs.items():
    print(arg.name)
    print(arg.required)
    print(arg.default)
    print(arg.description)

# 遍历所有参数
for arg in method.allargs:
    print(arg)
