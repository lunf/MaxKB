# coding=utf-8
"""
    @project: qabot
    @Author:The Tiger
    @file: lock.py
    @date:2023/9/11 11:45
    @desc:
"""
from datetime import timedelta

from django.core.cache import caches

memory_cache = caches['default']


def try_lock(key: str, timeout=None):
    """
    Get the lock.
    :param key:    Get the lock. key
    :param timeout Overtime time
    :return: Get to the lock.
    """
    return memory_cache.add(key, 'lock', timeout=timedelta(hours=1).total_seconds() if timeout is not None else timeout)


def un_lock(key: str):
    """
    Unlocked
    :param key: Unlocked key
    :return: Unlocking success.
    """
    return memory_cache.delete(key)


def lock(lock_key):
    """
    Lock a function.
    :param lock_key: the lock.key The characters.|functions  The function returns the value to a string.
    :return: The decorator function. Current decorator mainly limits one.keyOnly one line to call. the samekeyYou can only stop waiting for the last task to be completed. differentlykeyNo need to wait.
    """

    def inner(func):
        def run(*args, **kwargs):
            key = lock_key(*args, **kwargs) if callable(lock_key) else lock_key
            try:
                if try_lock(key=key):
                    return func(*args, **kwargs)
            finally:
                un_lock(key=key)

        return run

    return inner
