import os

import pytest

try:
    from shapely.geometry import shape
except ImportError:
    shape = None

from pydplace import geo

@pytest.mark.skipif('TRAVIS' in os.environ or shape is None, reason="pygdal not installed")
def test_match():
    with pytest.raises(AssertionError):
        geo.match(0, 0, [])
