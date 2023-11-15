import shutil
import pathlib

import pytest


@pytest.fixture
def tests_dir():
    return pathlib.Path(__file__).parent


@pytest.fixture
def dataset_with_societies(tmp_path, tests_dir):
    shutil.copytree(tests_dir / 'dataset_with_societies', tmp_path / 'dataset_with_societies')
    return tmp_path / 'dataset_with_societies' / 'cldfbench_test.py'


@pytest.fixture
def dataset_without_societies(tmp_path, tests_dir):
    shutil.copytree(tests_dir / 'dataset_without_societies', tmp_path / 'dataset_without_societies')
    return tmp_path / 'dataset_without_societies' / 'cldfbench_test2.py'
