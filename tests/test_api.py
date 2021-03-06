import pytest
import attr

from pydplace.api import *


def test_reader(tmpdir):
    from pydplace.api import reader

    tmpdir.join('test').write_text('a,b\n1,2,3', encoding='utf8')

    with pytest.raises(ValueError):
        list(reader(str(tmpdir.join('test')), dicts=True))


def test_datasets(repos):
    assert len(repos.datasets) == 1
    assert len(repos.phylogenies) == 2
    assert len(repos.societies) == 339
    assert len(repos.variables) == 40

    ds = repos.dataset('Binford')
    with pytest.raises(KeyError):
        ds.society('xyz')
    assert '{0}'.format(ds) == 'Binford Hunter-Gatherer (Binford)'
    assert len(ds.society_relations) == 339
    ds.societies[0].Comment = '__test__'
    ds.write()
    # Make sure the altered attribute is persisted:
    assert '__test__' in ds._path('societies').read_text(encoding='utf-8')

    for d in ds.data:
        assert len(d.references) == 7
        assert '{0}'.format(d.references[0]) == 'avadhani1975'
        break

    phy = repos.phylogenies[0]
    assert 'ket:' in phy.newick
    assert len(phy.taxa) == 40
    assert not phy.is_glottolog

    assert len(list(
        repos.iter_data(datasets=['Binford'], societies=['B350'], variables=['B001']))) == 1

    repos.write()
    assert len(Repos(repos.repos).societies) == 339

    assert isinstance(repos.read_json('geo', 'societies_tdwg.json'), dict)


@pytest.fixture
def society_attrs():
    res = {k.name: '' for k in attr.fields(Society)}
    res.update(
        id='A1', xd_id='xd1', origLat='0', origLong='0', Lat='0', Long='0', glottocode='abcd1234')
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
def test_Society_invalid(society_attrs, update):
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


def test_RelatedSociety():
    with pytest.raises(ValueError):
        RelatedSociety.from_string('x')
    assert RelatedSociety.from_string('Dataset: name [id]').id == 'id'


def test_Taxon():
    t = Taxon.from_dict(dict(taxon='t', glottocode='g', xd_ids='a,b', soc_ids='', x='y'))
    assert t.properties['x'] == 'y'


def test_HRAF():
    assert 'xyz' in HRAF.fromstring('Name (xyz)').url
