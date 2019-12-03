import os

import pytest

try:
    from shapely.geometry import shape
except ImportError:  # pragma: no cover
    shape = None

from pydplace import geo

@pytest.mark.skipif('TRAVIS' in os.environ or shape is None, reason="pygdal not installed")
def test_match():
    with pytest.raises(AssertionError):
        geo.match(0, 0, [])


def test_match_contains(mocker):
    mocker.patch('pydplace.geo.shape', mocker.Mock())
    mocker.patch('pydplace.geo.Point', mocker.Mock())
    assert geo.match(0, 0, [mocker.MagicMock()])[1] == 0


def test_match_contains_not(mocker):
    mocker.patch(
        'pydplace.geo.shape', mocker.Mock(return_value=mocker.Mock(contains=lambda p: False)))
    mocker.patch(
        'pydplace.geo.Point', mocker.Mock(return_value=mocker.Mock(distance=lambda p: 100)))
    assert geo.match(0, 0, [mocker.MagicMock()])[1] == 100
