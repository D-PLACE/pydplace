import os

import pytest

from shapely.geometry import shape

from pydplace import geo


def test_match():
    reg = geo.Regions()
    region, dist = reg.match(0, 0)
    assert region == 'West Tropical Africa'
    assert dist > 0
