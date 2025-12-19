# coding:utf-8
import os

from makit.lib import ospath

# 原生拼接路径
print(ospath.join(os.getcwd(), 'temp'))
# 向上拼接路径
print(ospath.join(os.getcwd(), r'..\temp'))
