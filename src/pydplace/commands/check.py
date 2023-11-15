"""

"""
import subprocess

from termcolor import colored
from cldfbench.cli_util import add_dataset_spec, get_dataset

from pydplace import DatasetWithoutSocieties, DatasetWithSocieties


def register(parser):
    add_dataset_spec(parser)


def run(args):
    ds = get_dataset(args)
    passed = True
    assert ds.id.startswith('dplace-dataset-')
    if subprocess.check_call(['cldf', 'validate', str(ds.cldf_dir)]) != 0:
        passed = False  # pragma: no cover

    cldf = ds.cldf_reader()
    if not cldf.properties.get('dc:title', '').startswith(
            'D-PLACE dataset derived from'):
        print(colored(
            'Invalid dataset title in CLDF: {}'.format(
                cldf.properties.get('dc:title')),
            'red'))
        passed = False

    if issubclass(ds.__class__, DatasetWithoutSocieties):
        if not ds.__society_sets__:
            print(colored(
                'Dataset without societies must reference at lease one society set',
                'red'))
            passed = False
        if not cldf.properties.get('dc:references'):
            print(colored(
                'Referenced society sets not yet in CLDF. Re-run makecldf',
                'red'))
            passed = False
    else:
        assert issubclass(ds.__class__, DatasetWithSocieties)
        if not ds.dir.joinpath('map.png').exists():
            print(colored('map.png not found', 'red'))
            passed = False

    for fname in ['metadata.json', 'CONTRIBUTORS.md', '.zenodo.json']:
        if not ds.dir.joinpath(fname).exists():
            print(colored('{} not found'.format(fname), 'red'))
            passed = False

    print(colored('OK' if passed else 'FAIL', 'green' if passed else 'red', attrs={'bold'}))
    return 0
