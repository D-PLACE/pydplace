"""
Recreate glottolog data files from the current version published at http://glottolog.org
"""
import re
import itertools

from csvw.dsv import UnicodeWriter, reader
from ete3 import Tree
from pyglottolog.api import Glottolog
try:
    # Compatibility with pyglottolog < 2.x
    from pyglottolog.languoids import Level
except ImportError:
    Level = None

from pydplace.util import comma_join, remove_subdirs

__all__ = ['update']

NEXUS_TEMPLATE = """#NEXUS
Begin trees;
    tree {} = {}
end;
"""


def reference(title, year):
    return "Hammarström, Harald & Forkel, Robert & Haspelmath, Martin. {0}. " \
           "{1}. Jena: Max Planck Institute for the Science of Human History. " \
           "https://glottolog.org/".format(title, year)


def write_tree(tree, fname, taxa_in_dplace, societies_by_glottocode):
    if not fname.exists():
        fname.mkdir()
    tree.prune([str(n) for n in taxa_in_dplace])

    with fname.joinpath('summary.trees').open('w', encoding="utf-8") as handle:
        handle.write(NEXUS_TEMPLATE.format(
            tree.name if tree.name else 'UNTITLED',
            tree.write(format=1)
        ))

    with UnicodeWriter(fname.joinpath('taxa.csv')) as writer:
        writer.writerow(['taxon', 'glottocode', 'xd_ids', 'soc_ids'])
        for gc in sorted(taxa_in_dplace):
            socs = societies_by_glottocode[gc]
            writer.writerow([
                gc,
                gc,
                comma_join(sorted(set(s.xd_id for s in socs))),
                comma_join(sorted(s.id for s in socs))])
    return tree


def trees(societies_by_glottocode, langs, outdir, year, title):
    label_pattern = re.compile("'[^\[]+\[([a-z0-9]{4}[0-9]{4})[^']*'")

    def rename(n):
        n.name = label_pattern.match(n.name).groups()[0]
        n.length = 1

    glottocodes = set(societies_by_glottocode.keys())
    glottocodes_in_global_tree = set()
    index = {}
    outdir = outdir / 'phylogenies'
    remove_subdirs(outdir, 'glottolog_*')
    languoids = {}
    families = []
    for lang in langs:
        if not lang.lineage:  # a top-level node
            if not lang.category.startswith('Pseudo '):
                families.append(lang)
        languoids[lang.id] = lang

    glob = Tree()
    glob.name = 'glottolog_global'

    for family in sorted(families, key=lambda f: f.name):
        node = family.newick_node(nodes=languoids)
        node.visit(rename)
        taxa_in_tree = set(n.name for n in node.walk())
        taxa_in_dplace = glottocodes.intersection(taxa_in_tree)
        if not taxa_in_dplace:
            continue  # pragma: no cover

        tree = Tree("({0});".format(node.newick), format=3)
        tree.name = 'glottolog_{0}'.format(family.id)
        if family.level.name == 'family':
            tree = write_tree(tree, outdir / tree.name, taxa_in_dplace, societies_by_glottocode)
            glottocodes_in_global_tree = glottocodes_in_global_tree.union(
                set(n.name for n in tree.traverse()))
            index[tree.name] = dict(
                id=tree.name,
                name='{0} ({1})'.format(family.name, title),
                author='{0} ({1})'.format(title, family.name),
                year=year,
                scaling='',
                reference=reference(title, year),
                url='https://glottolog.org/resource/languoid/id/{}'.format(family.id))
        else:
            glottocodes_in_global_tree = glottocodes_in_global_tree.union(taxa_in_tree)
        glob.add_child(tree)

    # global
    write_tree(
        glob,
        outdir / glob.name,
        glottocodes_in_global_tree.intersection(glottocodes),
        societies_by_glottocode)
    index[glob.name] = dict(
        id=glob.name,
        name='Global Classification ({0})'.format(title),
        author=title,
        year=year,
        scaling='',
        reference=reference(title, year),
        url='https://glottolog.org/')

    index_path = outdir / 'index.csv'
    phylos = list(reader(index_path, dicts=True))
    with UnicodeWriter(index_path) as writer:
        header = list(phylos[0].keys())
        writer.writerow(header)
        for phylo in sorted(phylos, key=lambda p: tuple(p.values())):
            if phylo['id'] in index:
                writer.writerow([index[phylo['id']].get(k, '') for k in header])
                del index[phylo['id']]
            else:
                writer.writerow(list(phylo.values()))

        for id_, spec in sorted(index.items()):
            writer.writerow([spec.get(k, '') for k in header])


def languoids(api, langs, outdir):
    _Level = Level or api.languoid_levels
    with UnicodeWriter(outdir / 'csv' / 'glottolog.csv') as writer:
        writer.writerow([
            'id', 'name', 'family_id', 'family_name', 'iso_code', 'language_id', 'macroarea',
            'lineage', 'level'])
        for lang in sorted(langs, key=lambda l: l.id):
            if lang.level == _Level.language:
                lid = lang.id
            elif lang.level == _Level.dialect:
                for _, lid, level in reversed(lang.lineage):
                    if level == _Level.language:
                        break
                else:  # pragma: no cover
                    raise ValueError
            else:
                lid = None
            writer.writerow([
                lang.id,
                lang.name,
                lang.lineage[0][1] if lang.lineage else '',
                lang.lineage[0][0] if lang.lineage else '',
                lang.iso or '',
                lid,
                getattr(lang.macroareas[0], 'value', lang.macroareas[0].name)
                if lang.macroareas else '',
                '/'.join(gc for _, gc, _ in lang.lineage),
                lang.level.name,
            ])


def update(repos, gl_repos, year, title):
    societies_by_glottocode = {
        gc: list(socs) for gc, socs in itertools.groupby(
            sorted(repos.societies.values(), key=lambda s: s.glottocode),
            lambda s: s.glottocode)}
    api = Glottolog(gl_repos)
    langs = list(api.languoids())
    languoids(api, langs, repos.repos)
    trees(societies_by_glottocode, langs, repos.repos, year, title)
