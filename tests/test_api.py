# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
import attr

from pydplace.api import *


def test_datasets(repos):
    assert len(repos.datasets) == 1
    assert len(repos.phylogenies) == 2
    assert len(repos.societies) == 339
    assert len(repos.variables) == 40

    ds = repos.datasets[0]
    assert '{0}'.format(ds) == 'Binford Hunter-Gatherer (Binford)'
    assert len(ds.society_relations) == 339

    for d in ds.data:
        assert len(d.references) == 7
        assert '{0}'.format(d.references[0]) == 'avadhani1975'
        break

    phy = repos.phylogenies[0]
    assert 'ket:' in phy.newick
    assert len(phy.taxa) == 40

    assert not list(repos.iter_data())
    assert len(list(
        repos.iter_data(datasets=['Binford'], societies=['B350'], variables=['B001']))) == 1


@pytest.fixture
def society_attrs():
    res = {k.name: '' for k in attr.fields(Society)}
    res.update(id='A1', xd_id='xd1', origLat='0', origLong='0', Lat='0', Long='0')
    return res


@pytest.mark.parametrize(
    'update',
    [
        dict(id='1'),
        dict(id=''),
        dict(xd_id='x4'),
        dict(Lat=-100),
    ]
)
def test_Societey_invalid(society_attrs, update):
    society_attrs.update(update)
    with pytest.raises(ValueError):
        Society(**society_attrs)


def test_Society(society_attrs):
    soc = Society(**society_attrs)
    assert '{0}'.format(soc) == ' (A1)'


def test_Reference():
    ref = Reference('meier2001', '10-15')
    assert '{0}'.format(ref) == 'meier2001:10-15'
    assert ref == Reference.from_string('meier2001[10-15]')
