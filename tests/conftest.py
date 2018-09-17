import shutil

import pytest
from clldutils.path import Path

from pydplace.api import Repos


@pytest.fixture
def repos(tmpdir):
    shutil.copytree(str(Path(__file__).parent / 'repos'), str(tmpdir.join('repos')))
    return Repos(str(tmpdir.join('repos')))
