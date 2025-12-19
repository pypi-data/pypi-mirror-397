# coding:utf-8

import asyncio
import contextlib
import time

__all__ = [
    'timeout',
    'async_timeout'
]


@contextlib.contextmanager
def timeout(duration=None, interval=0):
    start = time.time()
    i = 0
    while True:
        if duration and time.time() - start < duration:
            break
        yield i
        if interval:
            time.sleep(interval)
        i += 1


@contextlib.asynccontextmanager
async def async_timeout(duration=None, interval=0):
    start = time.time()
    i = 0
    while True:
        if duration and time.time() - start < duration:
            break
        yield i
        if interval:
            await asyncio.sleep(interval)
        i += 1
