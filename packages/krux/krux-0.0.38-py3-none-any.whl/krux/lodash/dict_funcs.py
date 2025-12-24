# -*- coding:utf-8 -*-

import six
import re
from fnmatch import fnmatch

__all__ = ['pick', 'pick2', 'omit', 'defaults', 'deep_update']


def pick(d, keys, attr=False, glob=False, regex=False):
    if attr:
        d = {k: getattr(d, k) for k in dir(d)}

    result = {}
    orig_keys = d.keys()

    for k in keys:
        if regex:
            for orig_key in orig_keys:
                if re.fullmatch(k, orig_key):
                    result[orig_key] = d[orig_key]
        elif glob:
            for orig_key in orig_keys:
                if fnmatch(orig_key, k):
                    result[orig_key] = d[orig_key]
        else:
            if k in d:
                result[k] = d[k]

    return result


def pick2(d, keys, glob=False, regex=False):
    # pick/omit together
    result, rest = {}, d.copy()
    for key in keys:
        if regex:
            for orig_key in list(rest.keys()):
                if re.fullmatch(key, orig_key):
                    result[orig_key] = rest.pop(orig_key)
        elif glob:
            for orig_key in list(rest.keys()):
                if fnmatch(orig_key, key):
                    result[orig_key] = rest.pop(orig_key)
        else:
            if key in d:
                result[key] = rest.pop(key)

    return result, rest


def omit(d, keys, glob=False, regex=False):
    result = d.copy()
    for k in keys:
        if regex:
            for orig_key in list(result.keys()):
                if re.fullmatch(k, orig_key):
                    result.pop(orig_key, None)
        elif glob:
            for orig_key in list(result.keys()):
                if fnmatch(orig_key, k):
                    result.pop(orig_key, None)
        else:
            result.pop(k, None)

    return result


def defaults(d1, d2, inplace=True):
    result = d1 if inplace else d1.copy()
    for k, v in six.iteritems(d2):
        result.setdefault(k, v)
    return result


def deep_update(a, b):
    """deep version of dict.update()"""
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deep_update(a[key], b[key])
            elif a[key] == b[key]:
                pass
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a
