# makitdone-lib

### 介绍
python 基本库的扩展

### 安装教程

```bash
pip install makitdone-lib
```

### 使用说明

#### 1. command 命令行工具

```python
from makit.lib import AppCommand

c = AppCommand()

@c.command(default=True)
def serve(env='prod', host='127.0.0.1', port=8000):
    """
    运行服务
    
    :param env: 环境，默认prod
    :param host: 默认127.0.0.1
    :param port: 默认8000
    """
    ...

c.run()

```

装饰器可以直接将函数封装为子命令，如果default为True，会作为默认命令

#### 2. os.path的扩展ospath

除了继承os.path原有的所有用法，还额外对部分函数进行了功能扩展

```python
import os
from makit.lib import ospath

print(ospath.exists('C:', 'windows'))  # 将路径拼接之后再判断是否存在
print(ospath.join('C:', 'windows'))  # 拼接路径
print(ospath.join(os.getcwd(), '../temp')) # 支持..向上拼接

```

更多示例可以在源代码中查看 samples/ospath_sample.py

#### 3. inspect扩展

继承原生inspect的所有用法，另外增加了函数的安全调用

```python
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
    pass

# 遍历所有参数
for arg in method.allargs:
    print(arg)

```
更多信息查看源代码： samples/inspect_sample.py

#### 4. json扩展

可以替代原生的json，与原dumps不同，这里的json.dumps默认支持安全模式，会解除循环引用的问题

另外支持 json.predumps，可以将任意对象序列化为 dict 或 list，而不是直接转化为json字符串

具体查看示例源码：samples/json_sample.py