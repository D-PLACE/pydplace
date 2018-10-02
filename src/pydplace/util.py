# coding: utf8
from __future__ import unicode_literals, print_function, division
from functools import partial
import types
import shutil

from clldutils.text import split_text
from clldutils.path import Path

__all__ = ['comma_split', 'semicolon_split', 'remove_subdirs', 'comma_join']


comma_split = partial(split_text, separators=',', strip=True, brackets={})
semicolon_split = partial(split_text, separators=';', strip=True, brackets={})


def _join(sep, *args):
    if len(args) == 1 and isinstance(args[0], (list, tuple, set, types.GeneratorType)):
        args = args[0]
    return sep.join(args)


comma_join = partial(_join, ', ')
semicolon_join = partial(_join, '; ')


def format_float(f):
    return format(float(f), '.6f').rstrip('0').rstrip('.')


def remove_subdirs(d, pattern='*'):
    for sd in Path(d).glob(pattern):
        if sd.is_dir():
            shutil.rmtree(str(sd))
