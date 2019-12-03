"""
Extracts subsets of data for further processing.

To filter societies:

> dplace %(prog)s --society Cj4,Cj5,Cj6 output.csv

To filter societies on a given tree:

> dplace %(prog)s --tree gray_et_al2009 output.csv

To filter societies only from a given dataset:

> dplace %(prog)s --dataset EA output.csv
"""
from csvw.dsv import UnicodeWriter


def register(parser):
    parser.add_argument('filename', help='filename', default=None)
    parser.add_argument('--society', help='restrict to these society ids (x,y,z)', default=None)
    parser.add_argument('--tree', help='restrict to this tree', default=None)
    parser.add_argument('--dataset', help='restrict to these datasets (x,y,z)', default=None)
    parser.add_argument('--variable', help='restrict to thes dataset (x,y,z)', default=None)


def run(args):
    datasets = args.dataset.split(",") if args.dataset else None
    variables = args.variable.split(",") if args.variable else None
    societies = args.society.split(",") if args.society else None

    if args.tree:
        for tree in args.repos.phylogenies:
            if args.tree == tree.id:
                break
        else:
            raise SystemExit("Failed to find Tree %s" % args.tree)
        societies = [s for sublist in [t.soc_ids for t in tree.taxa] for s in sublist]

    with UnicodeWriter(f=args.filename) as out:
        header = [
            'ID',
            'XD_ID',
            'Glottocode',
            'Name',
            'OriginalName',
            'FocalYear',
            'Latitude',
            'Longitude',
            'Variable',
            'Value'
        ]
        out.writerow(header)

        socs = args.repos.societies
        for record in args.repos.iter_data(
                datasets=datasets, variables=variables, societies=societies):
            s = socs.get(record.soc_id, None)
            row = [
                s.id,
                s.xd_id,
                s.glottocode,
                s.pref_name_for_society,
                s.ORIG_name_and_ID_in_this_dataset,
                s.main_focal_year,
                s.Lat,
                s.Long,
                record.var_id,
                record.code
            ]
            out.writerow(row)
