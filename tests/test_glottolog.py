from pathlib import Path

from pydplace.glottolog import *


def test_update(repos):
    update(repos, Path(__file__).parent / 'gl_repos', '2018', 'the glottolog')
