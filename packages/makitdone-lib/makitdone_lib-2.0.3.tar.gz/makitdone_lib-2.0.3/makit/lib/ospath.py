# coding:utf-8

import fnmatch
import glob
import os
import re
import shutil
import typing as t
from datetime import datetime
from functools import cached_property
from os.path import *


def name(filename):
    """
    获取文件名，不带后缀
    :param filename: 文件路径
    :return:
    """
    return basename(filename).rsplit('.', maxsplit=1)[0]


def extname(filename):
    """
    获取文件扩展名
    :param filename:
    :return:
    """
    name = os.path.basename(filename)
    try:
        dot_index = name.rindex('.')
    except ValueError:
        dot_index = None
    return name[dot_index:] if dot_index else None


def exists(p, *paths):
    """
    拼接路径并判断是否存在
    :param p:
    :param paths:
    :return:
    """
    p = join(p, *paths)
    return os.path.exists(p)


def join(p, *paths):
    """
    拼接路径

    - .. 父级
    - ... 向上查找，直到指定名称节点
    :param p:
    :param paths:
    :return:
    """
    prev = None
    for path in paths:
        parts = re.split(r'[/\\]', path)
        if len(parts) > 1:
            p = join(p, *parts)
        else:
            if path == '..':
                p = os.path.dirname(p)
            elif path == '...':
                prev = path
                continue
            elif prev == '...':
                for item in reverse_search(p, path):
                    p = item
                    break
            else:
                p = os.path.join(p, path)

    return Path(p.replace('\\', '/'))


def drive(path):
    """
    获取系统盘符
    :param path:
    :return:
    """
    return os.path.splitdrive(path)[0]


def rename(filename: str, new: str):
    """
    Rename a file or a directory.

    :param filename:
    :param new: new name
    :return:
    """
    shutil.move(filename, join(filename, '..', new))


def delete(path):
    """
    删除路径
    :param path:
    :return:
    """
    if not os.path.exists(path):
        return False
    if os.path.isfile(path):
        os.remove(path)
    else:
        os.removedirs(path)
    return True


def listdir(p, pattern=None):
    """
    枚举文件夹下的所有文件或子文件夹
    :param p: 路径，如果是文件，则取其所在文件夹
    :param pattern:
    :return: (filename, fullpath)
    """
    p = os.path.abspath(p)
    if os.path.isfile(p):
        p = os.path.dirname(p)
    for filename in os.listdir(p):
        if pattern and not fnmatch.fnmatch(filename, pattern):
            continue
        yield filename, os.path.join(p, filename)


def reverse_search(path, pattern):
    if not pattern:
        raise Exception('Pattern for searching is required!')
    if os.path.isfile(path):
        path = os.path.dirname(path)
    basename = os.path.basename(path)
    if fnmatch.fnmatch(basename, pattern):
        yield path
    else:
        for f in reverse_search(os.path.dirname(path), pattern):
            yield f


def search(pattern, path=None, recursive=True):
    """
    根据通配符查找文件
    :param pattern: 通配符
    :param path: 查找路径
    :param recursive: 是否递归查找
    :return:
    """
    if path is not None:
        if recursive:
            pattern = join(path, '**', pattern)
        else:
            pattern = join(path, pattern)
    return glob.glob(pattern, recursive=recursive)


def copy(src, dest):
    # 支持通配符
    if os.path.isfile(src):
        shutil.copy(src, dest)
    else:
        if os.path.isdir(dest) and os.path.exists(dest):
            dest = os.path
        shutil.copytree(src, dest)


#
# def move(src, dest, overwrite=False, backfile=True):
#     """
#     移动文件
#     :param src: 源文件
#     :param dest: 目标目录
#     :param overwrite: 是否覆写
#     :param backfile: 如果目标位置有同名文件，是否备份
#     :return:
#     """
#     _dest = Path(dest)
#     if _dest.isfile and _dest.basename != src.basename:
#         dest = os.path.dirname(dest)
#     try:
#         shutil.move(src, dest)
#         return True
#     except shutil.Error as e:
#         if 'already exists' in str(e) and overwrite:
#             shutil.copy()
#             os.remove(os.path.join(dest, self.basename))
#             return move(src, dest)
#         return False
class Path(str):

    @cached_property
    def basename(self) -> str:
        return os.path.basename(self)

    @cached_property
    def name(self):
        """
        名称，不带后缀
        :return:
        """
        if self.isfile:
            return self.basename.rsplit('.', maxsplit=1)[0]
        else:
            return self.basename

    @cached_property
    def extname(self):
        basename = self.basename
        try:
            dot_index = basename.rindex('.')
        except ValueError:
            dot_index = None
        return basename[dot_index:] if dot_index else None

    @cached_property
    def isfile(self):
        return os.path.isfile(self)

    @cached_property
    def isdir(self):
        return os.path.isdir(self)

    @cached_property
    def ismount(self):
        """是否盘符"""
        return os.path.ismount(self)

    @cached_property
    def isabs(self):
        return os.path.isabs(self)

    @property
    def size(self):
        return os.path.getsize(self)

    @cached_property
    def create_time(self):
        return datetime.fromtimestamp(os.path.getctime(self))

    @cached_property
    def ctime(self):
        return datetime.fromtimestamp(os.path.getctime(self))

    @property
    def mod_time(self):
        return datetime.fromtimestamp(os.path.getmtime(self))

    @property
    def mtime(self):
        return datetime.fromtimestamp(os.path.getmtime(self))

    @property
    def last_access_time(self):
        return datetime.fromtimestamp(os.path.getatime(self))

    @property
    def atime(self):
        return datetime.fromtimestamp(os.path.getatime(self))

    @cached_property
    def parent(self):
        return Path(os.path.dirname(self)) if not self.ismount else None

    @property
    def exists(self):
        return os.path.exists(self)

    @property
    def nodes(self):
        """将路径拆分成节点列表"""
        return re.split(r'[\\/]', self)

    def info(self, related: str = None):
        info = dict(
            name=self.basename,
            path=self,
            size=self.size,
            create_time=self.create_time,
            mod_time=self.mod_time,
            last_access_time=self.last_access_time
        )
        if self.isfile:
            info['size'] = self.size
            info['type'] = 'file'
        else:
            info['type'] = 'dir'
        if related:
            related = related.strip(os.sep)
            info['relative_path'] = self.replace(related, '')
        return info

    def list(self, pattern=None, ign_case=True):
        assert self.isdir, "not a directory"
        for _name in os.listdir(self):
            match = fnmatch.fnmatch
            if not ign_case:
                match = fnmatch.fnmatchcase
            if pattern is None or (pattern and match(_name, pattern)):
                yield Path(os.path.join(self, _name))

    def search(self, pattern, recursive=True):
        if not pattern:
            raise PathError('Pattern for searching is required!')
        for item in self.list():
            if fnmatch.fnmatch(item.basename, pattern):
                yield item
            if item.isdir and recursive:
                for f in item.search(pattern):
                    yield f

    def files(self, pattern=None):
        """
        列出所有子文件
        :param pattern:
        :return:
        """
        for item in self.list(pattern):
            if item.isfile:
                yield item

    def dirs(self, pattern=None):
        """
        列出目录中的所有文件夹
        :param pattern:
        :return:
        """
        for item in self.list(pattern):
            if item.isdir:
                yield item

    def walk_files(self, pattern=None, ):
        for root, dirs, files in os.walk(self):
            for file in files:
                if pattern is None or (pattern and fnmatch.fnmatch(file, pattern)):
                    yield file, self.__class__(root) / file

    def walk(self, pattern=None):
        for root, dirs, files in os.walk(self):
            for d in dirs:
                if pattern is None or (pattern and fnmatch.fnmatch(d, pattern)):
                    yield Path(root) / d
            for file in files:
                if pattern is None or (pattern and fnmatch.fnmatch(file, pattern)):
                    yield Path(root) / file

    def reserve_search(self, pattern):
        """
        方向查找文件或文件夹
        :param pattern: 通配符
        :return:
        """
        if not pattern:
            raise PathError('Pattern for searching is required!')
        if self.isfile:
            for f in self.parent.reserve_search(pattern):
                yield f
        else:
            for f in self.list(pattern):
                yield f
            if self.parent:
                for f in self.parent.reserve_search(pattern):
                    yield f

    def open(self):
        assert self.isfile, "not a file"
        return open(self)

    def makedirs(self, mode=0o777, exist_ok=False):
        p = self.parent if self.isfile else self
        os.makedirs(p, mode=mode, exist_ok=exist_ok)
        return self

    mkdirs = makedirs  # 别名

    def copy(self, dest):
        if self.isfile:
            shutil.copy(self, dest)
        else:
            shutil.copytree(self, dest)

    def move(self, dest, overwrite=False):
        """

        :param dest:
        :param overwrite:
        :return:
        """
        _dest = Path(dest)
        if _dest.isfile and _dest.basename != self.basename:
            dest = os.path.dirname(dest)
        try:
            shutil.move(self, dest)
            return True
        except shutil.Error as e:
            if 'already exists' in str(e) and overwrite:
                os.remove(os.path.join(dest, self.basename))
                return self.move(dest)
            return False

    def delete(self):
        """
        删除路径指向的文件或文件夹
        :return:
        """
        if not self.exists:
            return
        if self.isfile:
            os.remove(self)
        else:
            os.removedirs(self)

    def rename(self, new):
        """
        Rename a file or a directory.
        :param new: new name
        :return:
        """
        shutil.move(self, os.path.join(self.parent, new))

    def abspath(self):
        return os.path.abspath(self)

    def join(self, *paths):
        return join(self, *paths)

    def expend(self, *paths):
        result = self
        for path in paths:
            result = result / path if result else Path(path)
        return result

    def __truediv__(self, other: t.Union['Path', str]):
        if other:
            return Path(os.path.join(self, other))
        return self

    @staticmethod
    def user_path(*paths):
        return Path(os.path.expanduser('~')).join(*paths)


class PathError(Exception):
    """
    """
