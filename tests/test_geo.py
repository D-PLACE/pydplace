import pytest

from pydplace import geo


def test_match():
    with pytest.raises(AssertionError):
        geo.match(0, 0, [])
