# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from itertools import groupby, chain

import attr
from clldutils.dsv import reader
from clldutils.path import read_text
from clldutils.misc import UnicodeMixin
from clldutils.apilib import API
from clldutils.attrlib import valid_re, valid_range
from clldutils import jsonlib
from nexus import NexusReader
from pyglottolog.references import BibFile

from pydplace.util import comma_split, semicolon_split

__all__ = ['Variable', 'Reference', 'Data', 'Society', 'Dataset',
           'Taxon', 'Phylogeny', 'Repos']


@attr.s
class Variable(object):
    id = attr.ib()
    category = attr.ib(converter=lambda s: [c.capitalize() for c in comma_split(s)])
    title = attr.ib()
    definition = attr.ib()
    type = attr.ib(
        validator=attr.validators.in_(['Continuous', 'Categorical', 'Ordinal']))
    source = attr.ib()
    changes = attr.ib()
    notes = attr.ib()
    codes = attr.ib(default=attr.Factory(list))
    units = attr.ib(default='')


@attr.s
class Reference(UnicodeMixin):
    key = attr.ib()
    pages = attr.ib()

    def __unicode__(self):
        res = self.key
        if self.pages:
            res += ':{0}'.format(self.pages)
        return res

    @classmethod
    def from_string(cls, s):
        if ':' in s:
            k, _, p = s.partition(':')
        elif '[' in s:
            k, _, p = s[:-1].partition('[')
        else:
            k, p = s, ''
        return cls(k.strip(), p.strip())


@attr.s
class Data(object):
    soc_id = attr.ib()
    sub_case = attr.ib()
    year = attr.ib()
    var_id = attr.ib()
    code = attr.ib()
    comment = attr.ib()
    references = attr.ib(
        converter=lambda s: [Reference.from_string(ss) for ss in semicolon_split(s)])
    source_coded_data = attr.ib()
    admin_comment = attr.ib()


@attr.s
class ObjectWithSource(UnicodeMixin):
    id = attr.ib()
    name = attr.ib()
    year = attr.ib()
    author = attr.ib()
    reference = attr.ib()
    base_dir = attr.ib()
    url = attr.ib()

    @property
    def dir(self):
        return self.base_dir.joinpath(self.id)

    def __unicode__(self):
        return '{0.name} ({0.id})'.format(self)


@attr.s
class RelatedSociety(object):
    dataset = attr.ib(converter=lambda s: s.strip())
    name = attr.ib(converter=lambda s: s.strip())
    id = attr.ib(converter=lambda s: s.strip())

    @classmethod
    def from_string(cls, s):
        match = re.match('([A-Za-z]+):\s*([^\[]+)\[([^\]]+)\]$', s)
        if not match:
            raise ValueError(s)
        return cls(*match.groups())


@attr.s
class RelatedSocieties(object):
    id = attr.ib()
    related = attr.ib(converter=lambda s: [
        RelatedSociety.from_string(ss) for ss in semicolon_split(s)])


@attr.s
class Society(UnicodeMixin):
    id = attr.ib(validator=valid_re('[A-Za-z][A-Za-z0-9]+'))
    xd_id = attr.ib(validator=valid_re('xd[0-9]+'))
    pref_name_for_society = attr.ib()
    glottocode = attr.ib()
    ORIG_name_and_ID_in_this_dataset = attr.ib()
    alt_names_by_society = attr.ib()
    main_focal_year = attr.ib()
    HRAF_name_ID = attr.ib()
    HRAF_link = attr.ib()
    origLat = attr.ib(converter=float)
    origLong = attr.ib(converter=float)
    Lat = attr.ib(converter=float, validator=valid_range(-90, 90))
    Long = attr.ib(converter=float, validator=valid_range(-180, 180))
    Comment = attr.ib()
    glottocode_comment = attr.ib()

    def __unicode__(self):
        return '{0.pref_name_for_society} ({0.id})'.format(self)


@attr.s
class Dataset(ObjectWithSource):
    type = attr.ib(validator=attr.validators.in_(['cultural', 'environmental']))
    description = attr.ib()

    def _items(self, what, **kw):
        fname = self.dir.joinpath('{0}.csv'.format(what))
        return list(reader(fname, **kw)) if fname.exists() else []

    @property
    def data(self):
        return [Data(**d) for d in self._items('data', dicts=True)]

    @property
    def societies(self):
        return [Society(**d) for d in self._items('societies', dicts=True)]

    @property
    def society_relations(self):
        return [
            RelatedSocieties(**d) for d in self._items('societies_mapping', dicts=True)]

    @property
    def variables(self):
        codes = {vid: list(c) for vid, c in groupby(
            sorted(self._items('codes', namedtuples=True), key=lambda c: c.var_id),
            lambda c: c.var_id)}
        return [
            Variable(codes=codes.get(v['id'], []), **v)
            for v in self._items('variables', dicts=True)]


@attr.s
class Taxon(object):
    taxon = attr.ib()
    glottocode = attr.ib()
    xd_ids = attr.ib(converter=comma_split)
    soc_ids = attr.ib(converter=comma_split)


@attr.s
class Phylogeny(ObjectWithSource):
    scaling = attr.ib()

    @property
    def nexus(self):
        return NexusReader(self.trees.as_posix())

    @property
    def newick(self):
        nexus = self.nexus
        nexus.trees.detranslate()
        newick = re.sub(r'\[.*?\]', '', nexus.trees.trees[0])
        try:
            return newick[newick.index('=') + 1:]
        except ValueError:  # pragma: no cover
            return newick

    @property
    def is_glottolog(self):
        return self.id.startswith('glottolog_')

    @property
    def trees(self):
        return self.dir.joinpath('summary.trees')

    @property
    def taxa(self):
        return [Taxon(**d) for d in reader(self.dir.joinpath('taxa.csv'), dicts=True)]


class Repos(API):
    @property
    def datasets(self):
        res = [
            Dataset(base_dir=self.path('datasets'), **r) for r in
            reader(self.path('datasets', 'index.csv'), dicts=True)]
        for ds in res:
            if not ds.description:
                readme = ds.base_dir / ds.id / 'README.md'
                if readme.exists():
                    ds.description = read_text(readme)
        return res

    @property
    def phylogenies(self):
        return [
            Phylogeny(base_dir=self.path('phylogenies'), **r) for r in
            reader(self.path('phylogenies', 'index.csv'), dicts=True)]

    @property
    def societies(self):
        return {
            s.id: s for s in chain.from_iterable(d.societies for d in self.datasets)
        }

    @property
    def variables(self):
        return {
            v.id: v for v in chain.from_iterable(d.variables for d in self.datasets)
        }

    @property
    def sources(self):
        return BibFile(self.path('datasets', 'sources.bib'))

    def read_csv(self, *comps, **kw):
        return list(reader(self.path(*comps), **kw))

    def read_json(self, *comps):
        return jsonlib.load(self.path(*comps))
    
    def iter_data(self, datasets=None, variables=None, societies=None):
        for ds in self.datasets:
            if (datasets is None) or (datasets and ds.id in datasets):
                for record in ds.data:
                    if variables and record.var_id not in variables:
                        continue
                    if societies and record.soc_id not in societies:
                        continue
                    yield record
