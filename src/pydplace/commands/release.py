"""

"""
from cldfbench.cli_util import add_dataset_spec, get_dataset


def register(parser):
    add_dataset_spec(parser)
    parser.add_argument('tag')


def run(args):  # pragma: no cover
    tag = args.tag
    if not tag.startswith('v'):
        tag = 'v' + tag
    ds = get_dataset(args)
    cldf = ds.cldf_reader()
    if cldf.properties.get('dc:bibliographicCitation'):
        relnotes = """\
Cite the source as

> {}

and the D-PLACE dataset as

DOI""".format(cldf.properties['dc:bibliographicCitation'])
    else:
        relnotes = """\
Cite the D-PLACE dataset as

DOI"""

    ds.dir.joinpath('relnotes.txt').write_text(relnotes, encoding='utf8')
    print('gh release create {} --title "{}" --notes-file relnotes.txt'.format(
        tag, cldf.properties['dc:title']))
    print('git pull origin')
    print('')
    print("Now you should grab the Zenodo version DOI from\n"
          "https://zenodo.org/account/settings/github/repository/D-PLACE/{0}\n"
          "and add it to\n"
          "https://github.com/D-PLACE/{0}/releases/edit/{1}\n and the concept DOI to "
          "metdata.json".format(cldf.properties['rdf:ID'], tag))
