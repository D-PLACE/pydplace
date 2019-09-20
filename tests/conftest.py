import shutil
from pathlib import Path

import pytest


@pytest.fixture
def repos(tmpdir):
    from pydplace.api import Repos

    shutil.copytree(str(Path(__file__).parent / 'repos'), str(tmpdir.join('repos')))
    return Repos(str(tmpdir.join('repos')))
