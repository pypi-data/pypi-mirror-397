# coding:utf-8


from makit.lib import json


# 替代原生的json
# 与原dumps不同，这里的json.dumps默认支持安全模式，会解除循环引用的问题
# 另外支持 json.predumps

class User:
    def __init__(self, name: str, username: str):
        self.name = name
        self.username = username
        self.org = None


class Org:
    def __init__(self, name, manager=None):
        self.name = name
        self.manager = manager


user = User('张三', 'zhangsan')
user2 = User('李四', 'lisi')
user3 = User('王五', 'wangwu')
user4 = User('赵六', 'zhaoliu')
org = Org('开发部')
user.org = org
user2.org = org
user3.org = org
user4.org = org
org.manager = user

print(json.dumps([user, user3, user2, user4], debug=True, safe=True))
