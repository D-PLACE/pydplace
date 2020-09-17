import os
import logging
import pathlib

try:
    import fiona
except ImportError:  # pragma: no cover
    fiona = None

import pytest

from pydplace.__main__ import main


@pytest.fixture
def glottolog_repos():
    return pathlib.Path(__file__).parent / 'gl_repos'


def test_help(capsys):
    main([])
    out, _ = capsys.readouterr()
    assert 'usage' in out


def test_ls(repos, capsys):
    main(['--repos', str(repos.repos), 'ls'])
    out, _ = capsys.readouterr()
    assert 'Binford' in out


def test_denormalise(repos):
    with pytest.raises(NotImplementedError):
        main(['--repos', str(repos.repos), 'denormalise'])


def test_check(repos):
    main(['--repos', str(repos.repos), 'check'])


def test_glottologbib(repos):
    main(['--repos', str(repos.repos), 'glottologbib'])


def test_cldf(repos, tmpdir, glottolog_repos):
    main([
        '--repos', str(repos.repos),
        'cldf',
        str(glottolog_repos),
        'test',
        '--cldf-repos', str(tmpdir)])


def test_index(repos):
    assert not repos.path('SOURCES.md').exists()
    main(['--repos', str(repos.repos), 'index'])
    assert repos.path('SOURCES.md').exists()


@pytest.mark.skipif('TRAVIS' in os.environ or (fiona is None), reason="pygdal not installed")
def test_tdwg(repos):
    main(['--repos', str(repos.repos), 'tdwg'], log=logging.getLogger(__name__))
    main(['--repos', str(repos.repos), 'tdwg'], log=logging.getLogger(__name__))


def test_glottolog(repos, glottolog_repos):
    main(['--repos', str(repos.repos), 'glottolog', str(glottolog_repos)])


def test_extract(tmpdir, repos, mocker):
    res = tmpdir.join('res.csv')
    main(['--repos', str(repos.repos), 'extract', str(res)], log=mocker.Mock())
    assert len(res.read_text('utf8').split('\n')) == 13959

    with pytest.raises(SystemExit):
        main(['--repos', str(repos.repos), 'extract', str(res), '--tree', 'xyz'])

    main(['--repos', str(repos.repos), 'extract', str(res), '--tree', 'sicoli_and_holton2014'])
