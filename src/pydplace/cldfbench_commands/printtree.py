"""

"""
import nexus

from cldfbench.cli_util import add_dataset_spec, get_dataset


def register(parser):
    add_dataset_spec(parser)


def run(args):
    ds = get_dataset(args)
    p = ds.cldf_dir / ds.cldf_reader().properties['dc:hasPart']['summary']['dc:relation']
    print(nexus.NexusReader(p).trees.trees[0].newick_tree.ascii_art())
