import shutil
import pathlib
import functools

from clldutils.text import split_text

__all__ = ['split', 'comma_split', 'semicolon_split', 'remove_subdirs']


comma_split = functools.partial(split_text, separators=',', strip=True, brackets={})
semicolon_split = functools.partial(split_text, separators=';', strip=True, brackets={})
split = functools.partial(split_text, separators=';,', strip=True, brackets={})


def remove_subdirs(d, pattern='*'):
    for sd in pathlib.Path(d).glob(pattern):
        if sd.is_dir():
            shutil.rmtree(str(sd))
