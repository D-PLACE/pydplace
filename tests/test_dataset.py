import shutil
import pathlib
import argparse

import pytest

from pydplace.dataset import DatasetWithSocieties, DatasetWithoutSocieties


@pytest.fixture
def ds_with_dir(tmp_path):
    shutil.copytree(pathlib.Path(__file__).parent / 'dataset_with_societies', tmp_path / 'ds_with')
    return tmp_path / 'ds_with'


def test_DatasetWithSocieties(ds_with_dir):
    class DS(DatasetWithSocieties):
        id = 'dplace-dataset-test'
        dir = ds_with_dir

    ds = DS()
    ds._cmd_makecldf(argparse.Namespace())

    assert ds.with_prefix('x') == 'TESTx'
