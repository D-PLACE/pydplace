# coding: utf8
from __future__ import unicode_literals, print_function, division

try:
    from shapely.geometry import shape, Point
except ImportError:  # pragma: no cover
    shape, Point = None, None


def match(lon, lat, features):
    if not shape:
        return None, None  # pragma no cover
    point = Point(lon, lat)
    mindist, nearest = None, None
    for feature in features:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature, 0

        dist = point.distance(polygon)
        if mindist is None or mindist > dist:
            mindist, nearest = dist, feature

    assert mindist is not None
    return nearest, mindist
