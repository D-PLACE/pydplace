# coding: utf8
from __future__ import unicode_literals, print_function, division
from functools import partial
import types
import shutil

from clldutils.text import split_text

__all__ = ['comma_split', 'semicolon_split', 'remove_subdirs', 'comma_join']


comma_split = partial(split_text, separators=',', strip=True, brackets={})
semicolon_split = partial(split_text, separators=';', strip=True, brackets={})


def comma_join(*args):
    if len(args) == 1 and isinstance(args[0], (list, tuple, set, types.GeneratorType)):
        args = args[0]
    return ', '.join(args)


def remove_subdirs(d, pattern='*'):
    for sd in d.glob(pattern):
        if sd.is_dir():
            shutil.rmtree(str(sd))
