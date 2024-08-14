import re
import pathlib

from pycldf.sources import Sources
from cldfbench import Dataset as BaseDataset, CLDFSpec
from clldutils import jsonlib
from clldutils.markup import add_markdown_text

from .util import comma_split, semicolon_split, split
from .geo import Regions

XD_IDS = pathlib.Path(__file__).parent / 'cross_dataset_ids.json'


def hraf_id(name_and_id):
    match = re.search(r'\((?P<id>[A-Z]+[0-9]+)(/[A-Z0-9]+)?\)', name_and_id)
    if match:
        return match.group('id')


def valid_id(s):
    return s.replace('.', '_')


def add_data(raw_dir, writer):
    continuous = set()
    for row in raw_dir.read_csv('variables.csv', dicts=True):
        writer.objects['ParameterTable'].append(dict(
            ID=valid_id(row['id']),
            Name=row['title'],
            Description=row['definition'],
            category=comma_split(row['category']),
            type=row['type'],
            unit=row['units'],
            source_comment=row['source'],
            changes=row['changes'],
            comment=row['notes'],
            ColumnSpec=dict(datatype='decimal') if row['type'] == 'Continuous' else None,
        ))
        if row['type'] == 'Continuous':
            continuous.add(row['id'])

    codes = {}
    if raw_dir.joinpath('codes.csv').exists():
        for row in raw_dir.read_csv('codes.csv', dicts=True):
            if row['var_id'] not in continuous:
                writer.objects['CodeTable'].append(dict(
                    ID='{}-{}'.format(valid_id(row['var_id']), row['code'].replace('.', '')),
                    Var_ID=valid_id(row['var_id']),
                    Name=row['name'],
                    Description=row['description'],
                    ord=int(row['code'].replace('.', '')) if row['code'] != 'NA' else 99,
                ))
                codes[(row['var_id'], row['code'])] = (
                    row)['name'] if row['name'].lower() != 'missing data' else None

    refs = set()
    sources = Sources.from_file(raw_dir / 'sources.bib')

    for i, row in enumerate(raw_dir.read_csv('data.csv', dicts=True)):
        ref = []
        for src in semicolon_split(row['references']):
            src, _, pages = src.partition(':')
            if src not in refs:
                writer.cldf.add_sources(sources[src])
                refs.add(src)
            r = src
            if pages:
                r += '[{}]'.format(pages)
            ref.append(r)
        val = codes.get((row['var_id'], row['code']), row['code'])
        if val in {'NA', '?'}:
            val = None
        writer.objects['ValueTable'].append(dict(
            ID=str(i + 1),
            Var_ID=valid_id(row['var_id']),
            Code_ID='{}-{}'.format(valid_id(row['var_id']), row['code'].replace('.', ''))
            if (row['var_id'], row['code']) in codes else None,
            Soc_ID=row['soc_id'],
            Value=val,
            Comment=row['comment'],
            Source=ref,
            sub_case=row['sub_case'],
            source_coded_data=row['source_coded_data'],
            admin_comment=row['admin_comment'],
            year=None if row['year'] == 'NA' else row['year'],
        ))


def data_schema(cldf, with_codes=True):
    cldf.add_columns(
        'ValueTable',
        {
            'name': 'sub_case',
            'dc:description':
                'More specific description of the population the data refer to in terms of '
                'society or area.',
        },
        {
            'name': 'year',
            'datatype': {'base': 'string', 'format': '-?[0-9]{1,4}(-[0-9]{4})?'},
            'dc:description': 'Focal year, i.e. the time period to which the data refer.',
        },
        {
            'name': 'source_coded_data',
            'dc:description':
                'The source of the coded data, which was aggregated in this dataset.',
        },
        {
            'name': 'admin_comment',
        },
    )
    cldf['ValueTable'].common_props['dc:description'] = \
        ("Values are coded datapoints, i.e. measurements of a variable for a society."
         "\n\n**Note:** Missing data is signaled by an empty Value column.")
    cldf['ValueTable', 'Value'].null = [""]
    cldf['ValueTable', 'Value'].common_props['dc:description'] = \
        ("Values for categorical and ordinal variables reference the corresponding code via "
         "the Code_ID column. Values for continuous variables have the measured number in the "
         "Value column and an empty Code_ID.")
    cldf.rename_column('ValueTable', 'languageReference', 'Soc_ID')
    cldf.rename_column('ValueTable', 'parameterReference', 'Var_ID')
    cldf.add_columns(
        'ParameterTable',
        {
            'name': 'category',
            'dc:description': "",
            'separator': ', '},
        {
            'name': 'type',
            'datatype': {'base': 'string', 'format': 'Continuous|Categorical|Ordinal'},
            'dc:description':
                "Variables may be categorical (and then must be accompanied by a list of "
                "possible ‘codes’, i.e. rows in Codetable. "
                "Variables can also be continuous (e.g. Population size) or ordinal. "
                "Ordinal variables are accompanied by a list of codes (like categorical "
                "variables). The order of codes is encoded as `ord` column in CodeTable.",
        },
        {
            'name': 'unit',
            'dc:description': 'The unit of measurement',
        },
        {
            'name': 'source_comment',
            'dc:description': 'A note about the source of this variable.',
        },
        {
            'name': 'changes',
            'dc:description':
                'Notes about how a variable may have been derived from the source.',
        },
        {
            "name": "comment",
            "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment",
        },
    )
    cldf['ParameterTable'].common_props['dc:description'] = \
        "Variables are cultural features or practices, or environmental descriptors."
    cldf['ParameterTable', 'ID'].datatype.format = '[A-Za-z.0-9_]+([0-9]+)?'
    if with_codes:
        cldf.add_component(
            'CodeTable',
            {
                'name': 'ord',
                'datatype': 'integer',
            },
            # var_id, code, description, name
        )
        cldf.rename_column('CodeTable', 'parameterReference', 'Var_ID')


class WithPrefix:
    @classmethod
    def with_prefix(cls, s):
        id_ = getattr(cls, 'id', None)
        assert id_
        return '{}{}'.format(id_.split('-')[-1].upper(), s)


class DatasetWithSocieties(BaseDataset, WithPrefix):
    def __init__(self):
        BaseDataset.__init__(self)
        # We enrich data with the cross-dataset ID and a WGSRPD region.
        self.xd_ids = {}
        for xd_id, ext in jsonlib.load(XD_IDS).items():
            for lid in ext:
                self.xd_ids[lid] = xd_id
        self.regions = Regions()

    def cldf_specs(self):
        return CLDFSpec(
            data_fnames={
                'LanguageTable': 'societies.csv',
                'ParameterTable': 'variables.csv',
                'ValueTable': 'data.csv',
            },
            dir=self.cldf_dir,
            module="StructureDataset")

    def schema(self, cldf):
        cldf.remove_columns('LanguageTable', 'Macroarea', 'ISO639P3code')
        cldf.add_columns(
            'LanguageTable',
            {
                'name': 'Name_and_ID_in_source',
                'dc:description':
                    'Society names identified as pejorative have been replaced with a preferred, '
                    'English-language ethnonym. The name (and ID) as given in the source dataset '
                    'is kept in this field.',
            },
            {
                'name': "xd_id",
                'dc:description':
                    '“cross-data-set” identifier, used to link societies present in different '
                    'datasets, if they share a focal location. Note: If this field is empty, other '
                    'fields such as Name, Glottocode, focal year and location may be used to '
                    'identify societies across datasets if appropriate.',
            },
            {
                'name': 'alt_names_by_society',
                'separator': '; ',
                'dc:description':
                    "A list of ‘alternate’ names for the society; includes, where available, one "
                    "or more autonyms in the society’s own language, as well as other commonly "
                    "encountered ethnonyms.",
            },
            {
                'name': 'main_focal_year',
                'datatype': 'integer',
                'dc:description':
                    'Focal year specifying the time period to which the data refer, given as '
                    'number of years BCE - if negative - or CE.',
            },
            {
                'name': 'HRAF_name_ID',
                'dc:description':
                    'Name(s) and ID(s) of the corresponding society in HRAF '
                    '(the Human Relations Area Files)',
            },
            {
                'name': 'HRAF_ID',
                'valueUrl': 'https://ehrafworldcultures.yale.edu/cultures/{HRAF_ID}/description',
                'dc:description': 'ID of the corresponding society in HRAF',
            },
            {
                'name': 'origLat',
                'datatype': {'base': 'decimal', 'minimum': -90, 'maximum': 90},
                'dc:description': 'Uncorrected latitude as given in the source.',
            },
            {
                'name': 'origLong',
                # Original longitudes sometimes are simply extended in the pacific.
                'datatype': {'base': 'decimal', 'minimum': -270, 'maximum': 180},
                'dc:description': 'Uncorrected longitude as given in the source.',
            },
            {
                "name": "comment",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment",
            },
            {
                'name': 'glottocode_comment',
                'dc:description': 'Comment on the Glottocode assignment.',
            },
            {
                'name': 'region',
                'dc:description':
                    'World Geographical Scheme for Recording Plant Distributions level2 region',
            },
        )
        cldf['LanguageTable'].common_props['dc:description'] = \
            ("We use the term “society” to refer to cultural groups. In most cases, a society can "
             "be understood to represent a group of people at a focal location with a shared "
             "language that differs from that of their neighbors. However, in some cases multiple "
             "societies share a language.")

    def add_society(self, writer, **props):
        """
        Enrich and add the data of a society for the CLDF dataset.

        :param props:
        """
        props.update(
            region=self.regions.match(props['Longitude'], props['Latitude'])[0],
            xd_id=self.xd_ids.get(props['ID']),
        )
        writer.objects['LanguageTable'].append(props)

    def local_makecldf(self, args):
        """
        Datasets can hook up any custom processing to happen at the end of the CLDF conversion.
        """
        pass

    def cmd_makecldf(self, args):
        data_schema(args.writer.cldf)
        self.schema(args.writer.cldf)

        add_data(self.raw_dir, args.writer)

        for row in self.raw_dir.read_csv('societies.csv', dicts=True):
            self.add_society(
                args.writer,
                ID=row['id'],
                Name=row['pref_name_for_society'],
                Glottocode=row['glottocode'],
                Latitude=row['Lat'],
                Longitude=row['Long'],
                Name_and_ID_in_source=row['ORIG_name_and_ID_in_this_dataset'],
                alt_names_by_society=split(row['alt_names_by_society']),
                main_focal_year=None if row['main_focal_year'] == 'NA' else row['main_focal_year'],
                HRAF_name_ID=row['HRAF_name_ID'],
                HRAF_ID=hraf_id(row['HRAF_name_ID']),
                origLat=row['origLat'],
                origLong=row['origLong'],
                comment=row['Comment'],
                glottocode_comment=row['glottocode_comment'],
            )
        self.local_makecldf(args)

    def cmd_readme(self, args):
        print('gh repo edit --description "{}" --add-topic "ethnology"'.format(self.metadata.title))
        if self.metadata.url:  # pragma: no cover
            print('gh repo edit --homepage "{}"'.format(self.metadata.url))
        return add_markdown_text(
            super().cmd_readme(args), "\n\n![](map.png)\n\n", section='Description')


class DatasetWithoutSocieties(BaseDataset, WithPrefix):
    __society_sets__ = []

    def cldf_specs(self):
        return CLDFSpec(
            data_fnames={
                'ParameterTable': 'variables.csv',
                'ValueTable': 'data.csv',
            },
            dir=self.cldf_dir,
            module="StructureDataset")

    def cmd_makecldf(self, args):
        data_schema(args.writer.cldf, with_codes=self.raw_dir.joinpath('codes.csv').exists())
        add_data(self.raw_dir, args.writer)
        args.writer.cldf.properties['dc:references'] = self.__society_sets__

    def cmd_readme(self, args):
        print('gh repo edit --description "{}" --add-topic "ethnology"'.format(self.metadata.title))
        if self.metadata.url:  # pragma: no cover
            print('gh repo edit --homepage "{}"'.format(self.metadata.url))
        return super().cmd_readme(args)
