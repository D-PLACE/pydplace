import shutil

import pytest
from clldutils.path import Path


@pytest.fixture
def repos(tmpdir):
    from pydplace.api import Repos

    shutil.copytree(str(Path(__file__).parent / 'repos'), str(tmpdir.join('repos')))
    return Repos(str(tmpdir.join('repos')))
