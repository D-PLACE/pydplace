from pydplace.util import *


def test_remove_subdirs(tmpdir):
    tmpdir.join('a').mkdir()
    tmpdir.join('a', 'b').mkdir()
    assert tmpdir.join('a', 'b').check()
    remove_subdirs(str(tmpdir))
    assert not tmpdir.join('a').check()
