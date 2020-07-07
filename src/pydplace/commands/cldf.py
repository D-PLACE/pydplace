"""

"""
import collections

from clldutils.clilib import PathType
from cldfcatalog import Catalog
from pycldf import StructureDataset, Sources


def register(parser):
    parser.add_argument(
        'glottolog',
        metavar='GLOTTOLOG',
        help="clone of glottolog/glottolog",
        type=PathType(type='dir'),
    )
    parser.add_argument(
        '--glottolog-version',
        default=None,
        help="tag to checkout glottolog/glottolog to",
    )
    parser.add_argument('--dev', action='store_true', default=False)
    parser.add_argument(
        '--cldf_repos',
        help="clone of d-place/dplace-cldf",
        default='../dplace-cldf',
        type=PathType(type='dir'))


def run(args):
    from csvw.metadata import Column
    #with Catalog(args.glottolog, args.glottolog_version) as glottolog:
    #    (args.repos, glottolog.dir, args.cldf_repos)
    cldf = StructureDataset.in_dir(args.cldf_repos / 'cldf')
    cldf.add_component(
        'LanguageTable',
        'xd_id',
        'ORIG_name_and_ID_in_this_dataset',
        {
            "name": "alt_names_by_society",
            "separator": ";"
        },
        'Dataset_ID',
        'main_focal_year',
        'HRAF_Name'
        'HRAF_ID',
        'HRAF_Link',
        'origLat',
        'origLong',
        'Comment',
        'Glottocode_Comment',
    )
    cldf.add_component(
        'ParameterTable',
        'Dataset_ID',
        {
            "name": "Category",
            "separator": ","
        },
        {
            "name": "Type",
            "datatype": {"base": "string", "format": "|".join(['Continuous', 'Categorical', 'Ordinal'])},
        },
        "Units",
        "Source",
        "Changes",
        "Notes",
    )
    cldf.add_component('CodeTable')
    cldf.add_columns(
        'ValueTable',
        'Sub_Case',
        'Year',
        'Source_Coded_Data',
        'Admin_Comment',
        'Dataset_ID',
    )
    cldf['ValueTable', 'value'].null = ['NA']
    cldf.add_table(
        'datasets.csv',
        {'name': 'ID', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id'},
        {'name': 'Name', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#name'},
        {'name': 'Description', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#description'},
        {'name': 'Type', 'datatype': {'base': 'string', 'format': 'environmental|cultural'}},
        {'name': 'Year', 'propertyUrl': 'http://purl.org/dc/terms/date'},
        {'name': 'Author', 'propertyUrl': 'http://purl.org/dc/elements/1.1/creator'},
        {'name': 'Reference', 'propertyUrl': 'http://purl.org/dc/terms/bibliographicCitation'},
        'URL',
    )
    t = cldf.add_table(
        'society_relations.csv',
        {'name': 'ID', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id'},
        'Society_ID',
        'Related_Society_ID',
        'Related_Society_External_ID',
        'Related_Society_Name',
        'Related_Society_Dataset',
    )
    cldf.add_foreign_key('society_relations.csv', 'Society_ID', 'LanguageTable', 'ID')
    cldf.add_foreign_key('society_relations.csv', 'Related_Society_ID', 'LanguageTable', 'ID')
    cldf.add_foreign_key('ParameterTable', 'Dataset_ID', 'datasets.csv', 'ID')
    cldf.add_foreign_key('LanguageTable', 'Dataset_ID', 'datasets.csv', 'ID')
    cldf.add_foreign_key('ValueTable', 'Dataset_ID', 'datasets.csv', 'ID')

    # FIXME: add foreignkeys to datasets.csv!

    relscount = 0
    cldf.sources = Sources.from_file(args.repos.path('sources.bib'))
    categorical_variables = set()
    data = collections.defaultdict(list)
    dsids = [ds.id for ds in args.repos.datasets]
    for ds in args.repos.datasets:
        data['datasets.csv'].append({
            'ID': ds.id,
            'Name': ds.name,
            'Description': ds.description,
            'Type': ds.type,
            'Year': ds.year,
            'Author': ds.author,
            'Reference': ds.reference,
            'URL': ds.url,
        })
        for soc in ds.societies:
            data['LanguageTable'].append({
                'ID': soc.id,
                'Dataset_ID': ds.id,
                'Name': soc.pref_name_for_society,
                'Glottocode': soc.glottocode,
                'Latitude': soc.Lat,
                'Longitude': soc.Long,
                'Comment': soc.Comment,
                'Glottocode_Comment': soc.glottocode_comment,
                'xd_id': soc.xd_id,
                'ORIG_name_and_ID_in_this_dataset': soc.ORIG_name_and_ID_in_this_dataset,
                'alt_names_by_society': soc.alt_names_by_society,
                'main_focal_year': soc.main_focal_year,
                'HRAF_ID': soc.HRAF_name_ID.id if soc.HRAF_name_ID else None,
                'HRAF_Name': soc.HRAF_name_ID.name if soc.HRAF_name_ID else None,
                'HRAF_Link': soc.HRAF_link,
                'origLat': soc.origLat,
                'origLong': soc.origLong,
            })
        for soc in ds.society_relations:
            for rel in soc.related:
                relscount += 1
                data['society_relations.csv'].append({
                    'ID': str(relscount),
                    'Society_ID': soc.id,
                    'Related_Society_ID': rel.id if rel.dataset in dsids else None,
                    'Related_Society_External_ID': rel.id if rel.dataset not in dsids else None,
                    'Related_Society_Name': rel.name,
                    'Related_Society_Dataset': rel.dataset,
                })
        for param in ds.variables:
            data['ParameterTable'].append({
                'ID': param.id.replace('.', '_'),
                'Dataset_ID': ds.id,
                'Name': param.title,
                'Description': param.definition,
                "Category": param.category,
                "Type": param.type,
                "Units": param.units,
                "Source": param.source,
                "Changes": param.changes,
                "Notes": param.notes,
            })
            for code in param.codes:
                if code.code == 'NA':
                    continue
                categorical_variables.add(code.var_id)
                data['CodeTable'].append({
                    'ID': '{}-{}'.format(code.var_id, code.code).replace('.', '_'),
                    'Parameter_ID': code.var_id.replace('.', '_'),
                    'Name': code.name,
                    'Description': code.description,
                })
        for i, d in enumerate(ds.data, start=1):
            data['ValueTable'].append({
                'ID': '{}-{}'.format(ds.id, i),
                'Language_ID': d.soc_id,
                'Parameter_ID': d.var_id.replace('.', '_'),
                'Dataset_ID': ds.id,
                'Code_ID': None
                if (d.var_id not in categorical_variables) or d.code == 'NA'
                else '{}-{}'.format(d.var_id, d.code).replace('.', '_'),
                'Value': d.code,
                'Comment': d.comment,
                'Sub_Case': d.sub_case,
                'Year': d.year,
                'Source': [ref.format_cldf() for ref in d.references],
                'Source_Coded_Data': d.source_coded_data,
                'Admin_Comment': d.admin_comment,
            })
    cldf.write(**data)
    if not args.dev:
        cldf.validate(log=args.log)