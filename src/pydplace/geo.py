"""
Assign socities to TDWG's World Geographical Scheme for Recording Plant Distributions (WGSRPD)
level 2 (regional or subcontinental) units.

See https://www.tdwg.org/standards/wgsrpd/
"""
import pathlib

import fiona
from shapely.geometry import shape, Point

GEOJSON = pathlib.Path(__file__).parent / 'wgsrpd_level2.geojson'


class Regions:
    def __init__(self):
        self.regions = [
            (dict(f.properties.items()), shape(f['geometry']))
            for f in fiona.collection(str(GEOJSON))]

    def match(self, lon, lat):
        point = Point(lon, lat)
        mindist, nearest = None, None
        for feature, polygon in self.regions:
            if polygon.contains(point):
                return feature['LEVEL2_NAM'], 0

            dist = point.distance(polygon)
            if mindist is None or mindist > dist:
                mindist, nearest = dist, feature

        assert mindist is not None
        return nearest['LEVEL2_NAM'], mindist
