"""
List datasets
"""
from clldutils.clilib import Table, add_format


def register(parser):
    add_format(parser, default='simple')


def run(args):
    with Table(args, 'id', 'name', 'type', 'variables', 'societies') as t:
        for ds in args.repos.datasets:
            t.append([ds.id, ds.name, ds.type, len(ds.variables), len(ds.societies)])
