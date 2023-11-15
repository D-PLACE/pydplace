"""
Augment sources.bib with lgcode for use as Glottolog reference provider.
"""
import collections


def run(args):  # pragma: no cover
    refs = collections.defaultdict(set)

    socs = {}
    for id_, soc in args.repos.societies.items():
        socs[id_] = soc

    for d in args.repos.iter_data():
        for ref in d.references:
            soc = socs[d.soc_id]
            refs[ref.key].add((soc.pref_name_for_society, soc.glottocode))

    def add_lgcode(e):
        if e.key in refs:
            e.fields['lgcode'] = ', '.join('{0} [{1}]'.format(*soc) for soc in sorted(refs[e.key]))

    args.repos.sources.visit(add_lgcode)
