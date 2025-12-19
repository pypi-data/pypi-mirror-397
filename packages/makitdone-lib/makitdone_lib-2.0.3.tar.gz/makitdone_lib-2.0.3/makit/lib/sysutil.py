# coding:utf-8

import fnmatch
import os
import platform
import signal
import subprocess

import psutil


def is_windows():
    return platform.system().lower() == 'windows'


def is_linux():
    return platform.system().lower() == 'linux'


def process_running(pid=None, name=None):
    if name:
        output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {name}"')
        return name in str(output)
    elif pid:
        output = subprocess.check_output(f'tasklist /FI "PID eq {pid}"')
        return str(pid) in str(output)


def kill_process(target: int | str, **kwargs):
    if isinstance(target, int):
        sig = kwargs.get('signal', signal.SIGKILL)
        os.kill(target, sig)
        return
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if fnmatch.fnmatch(name, target):
            proc.kill()
            break
    else:
        print(f"No process found matches name '{target}'.")
