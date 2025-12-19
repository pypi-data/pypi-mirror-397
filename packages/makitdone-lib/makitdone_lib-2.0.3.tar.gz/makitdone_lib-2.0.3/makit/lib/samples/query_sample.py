# coding:utf-8
from makit.lib.query import ListQuery


class User:
    def __init__(self, name, skills):
        self.name = name
        self.skills = skills

    def __repr__(self):
        return f'<User {self.name}, skills: {self.skills}>'


users = [
    User('张三', skills=['Python', 'Go', 'AI', 'Java']),
    User(name='李四', skills=['Python', 'C#']),
    User(name='王五', skills=['Python', 'C#', 'Go']),
    User(name='赵六', skills=['Vue'])
]

result = ListQuery(users).where(skills__contains='C#').last()
print(result)
result = ListQuery(users).where(skills__contains='C#').first()
print(result)
result = ListQuery(users).where(skills__contains='C#').all()
print(result)
result = ListQuery(users).where(skills__contains='C#').count()
print(result)
result = ListQuery(users).where(skills__has='C#').count()
print(result)
result = ListQuery(users).where(skills__has=['C#', 'Go']).all()
print(result)
result = ListQuery(users).where(skills__hasany=['C#', 'Go']).all()
print(result)
result = ListQuery(users).where(skills__not_hasany=['C#', 'Go']).all()
print(result)
