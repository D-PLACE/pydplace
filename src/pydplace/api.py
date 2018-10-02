# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from itertools import groupby, chain

import attr
from clldutils.dsv import reader, UnicodeWriter
from clldutils.path import read_text
from clldutils.misc import UnicodeMixin, lazyproperty
from clldutils.apilib import API
from clldutils.attrlib import valid_re, valid_range
from clldutils import jsonlib
from nexus import NexusReader
from pyglottolog.references import BibFile

from pydplace.util import comma_split, semicolon_split, comma_join, semicolon_join, format_float

__all__ = ['Variable', 'Reference', 'Data', 'Society', 'Dataset',
           'Taxon', 'Phylogeny', 'Repos']

ID_PATTERN = re.compile('[A-Za-z]+([0-9]+)?')


@attr.s
class Object(object):
    @classmethod
    def fields(cls):
        return [f.name for f in attr.fields(cls)]

    def astuple(self):
        return attr.astuple(self)


@attr.s
class Variable(Object):
    id = attr.ib(validator=valid_re(ID_PATTERN))
    category = attr.ib(converter=comma_split)
    title = attr.ib()
    definition = attr.ib()
    type = attr.ib(validator=attr.validators.in_(['Continuous', 'Categorical', 'Ordinal']))
    units = attr.ib()
    source = attr.ib()
    changes = attr.ib()
    notes = attr.ib()
    codes = attr.ib(default=attr.Factory(list))

    @classmethod
    def fields(cls):
        return [f.name for f in attr.fields(cls)][:-1]

    def astuple(self):
        return (
            self.id,
            comma_join(self.category),
            self.title,
            self.definition,
            self.type,
            self.units,
            self.source,
            self.changes,
            self.notes,
        )


@attr.s
class Code(Object):
    var_id = attr.ib(validator=valid_re(ID_PATTERN))
    code = attr.ib()
    description = attr.ib(converter=lambda s: s.strip())
    name = attr.ib()


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
class Data(Object):
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

    def astuple(self):
        return (
            self.soc_id,
            self.sub_case,
            self.year,
            self.var_id,
            self.code,
            self.comment,
            semicolon_join('{0}'.format(ref) for ref in self.references),
            self.source_coded_data,
            self.admin_comment,
        )


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
class RelatedSociety(UnicodeMixin):
    dataset = attr.ib(converter=lambda s: s.strip())
    name = attr.ib(converter=lambda s: s.strip())
    id = attr.ib(converter=lambda s: s.strip())

    def __unicode__(self):
        return '{0.dataset}: {0.name} [{0.id}]'.format(self)

    @classmethod
    def from_string(cls, s):
        match = re.match('([A-Za-z]+):\s*([^\[]+)\[([^\]]+)\]$', s)
        if not match:
            raise ValueError(s)
        return cls(*match.groups())


@attr.s
class RelatedSocieties(Object):
    id = attr.ib()
    related = attr.ib(converter=lambda s: [
        RelatedSociety.from_string(ss) for ss in semicolon_split(s)])

    def astuple(self):
        return (self.id, semicolon_join('{0}'.format(rs) for rs in self.related))


@attr.s
class HRAF(UnicodeMixin):
    name = attr.ib()
    id = attr.ib()

    @classmethod
    def fromstring(cls, s):
        if s:
            name, _, id_ = s.strip().partition('(')
            assert id_.endswith(')')
            return cls(name.strip(), id_[:-1])

    def __unicode__(self):
        return '{0.name} ({0.id})'.format(self)

    @property
    def url(self):
        return 'http://ehrafworldcultures\.yale\.edu/collection\?owc={0}'.format(self.id)


@attr.s
class Society(UnicodeMixin, Object):
    id = attr.ib(validator=valid_re('[A-Za-z][A-Za-z0-9]+'))
    xd_id = attr.ib(validator=valid_re('xd[0-9]+'))
    pref_name_for_society = attr.ib()
    glottocode = attr.ib(validator=valid_re('[a-z0-9]{4}[0-9]{4}$', nullable=True))
    ORIG_name_and_ID_in_this_dataset = attr.ib()
    alt_names_by_society = attr.ib(converter=comma_split)
    main_focal_year = attr.ib()
    HRAF_name_ID = attr.ib(converter=HRAF.fromstring)
    HRAF_link = attr.ib(
        converter=lambda s: s.strip() or None,
        validator=valid_re(
            r'http://ehrafworldcultures\.yale\.edu/collection\?owc=[A-Z0-9]+|in process',
            nullable=True))
    origLat = attr.ib(converter=float)
    origLong = attr.ib(converter=float)
    Lat = attr.ib(converter=float, validator=valid_range(-90, 90))
    Long = attr.ib(converter=float, validator=valid_range(-180, 180))
    Comment = attr.ib()
    glottocode_comment = attr.ib()

    def __unicode__(self):
        return '{0.pref_name_for_society} ({0.id})'.format(self)

    def astuple(self):
        return (
            self.id,
            self.xd_id,
            self.pref_name_for_society,
            self.glottocode,
            self.ORIG_name_and_ID_in_this_dataset,
            comma_join(self.alt_names_by_society),
            self.main_focal_year,
            '{0}'.format(self.HRAF_name_ID or ''),
            self.HRAF_link,
            format_float(self.origLat),
            format_float(self.origLong),
            format_float(self.Lat),
            format_float(self.Long),
            self.Comment,
            self.glottocode_comment,
        )


@attr.s
class Dataset(ObjectWithSource):
    type = attr.ib(validator=attr.validators.in_(['cultural', 'environmental']))
    description = attr.ib()

    def _path(self, what):
        return self.dir.joinpath('{0}.csv'.format(what))

    def _read_items(self, what, **kw):
        fname = self._path(what)
        return list(reader(fname, **kw)) if fname.exists() else []

    def _write_items(self, what, attr=None, items=None):
        items = items if items is not None else getattr(self, attr or what)
        if items:
            with UnicodeWriter(self._path(what)) as writer:
                writer.writerow(items[0].__class__.fields())
                for item in items:
                    writer.writerow(item.astuple())

    @lazyproperty
    def data(self):
        return [Data(**d) for d in self._read_items('data', dicts=True)]

    @lazyproperty
    def societies(self):
        return [Society(**d) for d in self._read_items('societies', dicts=True)]

    @lazyproperty
    def _society_dict(self):
        return {soc.id: soc for soc in self.societies}

    def society(self, id_):
        return self._society_dict[id_]

    @lazyproperty
    def society_relations(self):
        return [
            RelatedSocieties(**d) for d in self._read_items('societies_mapping', dicts=True)]

    @lazyproperty
    def variables(self):
        codes = {vid: list(c) for vid, c in groupby(
            sorted(self._read_items('codes', dicts=True), key=lambda c: c['var_id']),
            lambda c: c['var_id'])}
        res = []
        for v in self._read_items('variables', dicts=True):
            v.setdefault('units', '')
            res.append(Variable(codes=[Code(**c) for c in codes.get(v['id'], [])], **v))
        return res

    def write(self):
        self._write_items('societies')
        self._write_items('data')
        self._write_items('variables')
        self._write_items('codes', items=list(chain(*[var.codes for var in self.variables])))
        self._write_items('societies_mapping', attr='society_relations')


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
    @lazyproperty
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

    @lazyproperty
    def _dataset_dict(self):
        return {ds.id: ds for ds in self.datasets}

    def dataset(self, id_):
        return self._dataset_dict[id_]

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

    def write(self):
        for ds in self.datasets:
            ds.write()

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
