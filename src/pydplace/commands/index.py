"""
Create SOURCES.md
"""
from clldutils.markup import Table


def run(args):
    md = ['# Sources', '']
    for datatype in ['datasets', 'phylogenies']:
        md.append('\n## {0}\n'.format(datatype.capitalize()))
        t = Table('Name', 'Reference')
        for obj in getattr(args.repos, datatype):
            if not obj.id.startswith('glottolog_') or obj.id == 'glottolog_global':
                t.append([
                    '[{0}]({1}/{2})'.format(obj.name, datatype, obj.id),
                    obj.reference])
        md.append(t.render(condensed=False))
    args.repos.path('SOURCES.md').write_text('\n'.join(md), encoding='utf-8')
