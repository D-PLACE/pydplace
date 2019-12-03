"""
Assign socities to TDWG regions
"""
import math

from clldutils.jsonlib import update_ordered

from pydplace import geo

try:
    import fiona
except ImportError:  # pragma: no cover
    fiona = None


def run(args):
    if fiona is None:
        raise SystemExit('fiona and shapely must be installed for this command')

    with fiona.collection(str(args.repos.path("geo", "level2-shape/level2.shp")), "r") as source:
        regions = [f for f in source]

    with update_ordered(args.repos.path("geo", "societies_tdwg.json"), indent=4) as soc_tdwg:
        for ds in args.repos.datasets:
            for soc in ds.societies:
                spec = soc_tdwg.get(
                    soc.id, dict(lat=soc.Lat, lon=soc.Long, name=None, code=None))
                if math.isclose(spec['lat'], soc.Lat) \
                        and math.isclose(spec['lon'], soc.Long) \
                        and spec['code']:
                    continue

                region, dist = geo.match(spec['lon'], spec['lat'], regions)
                spec['name'] = region['properties']['REGION_NAM']
                spec['code'] = str(region['properties']['TDWG_CODE'])

                if dist == 0:  # pragma: no cover
                    args.log.info('{0} contained in region {1}'.format(soc, spec['name']))
                else:
                    args.log.warning(
                        'assigning {0} to nearest region {1}, distance {2}'.format(
                            soc, region['properties']['REGION_NAM'], dist))

                soc_tdwg[soc.id] = spec
