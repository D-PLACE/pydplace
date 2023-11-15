import logging

import pytest

from cldfbench.__main__ import main as cldfbenchmain
from pydplace.__main__ import main


def test_help(capsys):
    main([])
    out, _ = capsys.readouterr()
    assert 'usage' in out


def test_check(capsys, dataset_with_societies, dataset_without_societies):
    from clldutils.clilib import ParserError

    with pytest.raises(SystemExit):
        main(['check', '-h'])
    out, _ = capsys.readouterr()
    assert 'check' in out

    with pytest.raises(ParserError):
        main(['check', __file__], log=logging.getLogger(__name__))

    main(['check', str(dataset_with_societies)])
    out, _ = capsys.readouterr()
    assert 'Invalid dataset title' in out
    assert 'map.png not found' in out
    assert '.zenodo.json' in out

    main(['check', str(dataset_without_societies)])
    out, _ = capsys.readouterr()
    assert 'must reference' in out
    assert 'Re-run' in out


def test_readme(dataset_with_societies, dataset_without_societies):
    cldfbenchmain(['readme', str(dataset_with_societies)])
    assert dataset_with_societies.parent.joinpath('README.md').exists()

    cldfbenchmain(['readme', str(dataset_without_societies)])
    assert dataset_with_societies.parent.joinpath('README.md').exists()


def test_makecldf(capsys, dataset_with_societies, dataset_without_societies, tests_dir):
    cldfbenchmain([
        'makecldf', str(dataset_with_societies), '--glottolog', str(tests_dir / 'gl_repos')])
    main(['check', str(dataset_with_societies)])
    out, _ = capsys.readouterr()
    assert 'Invalid dataset title' not in out

    cldfbenchmain([
        'makecldf', str(dataset_without_societies), '--glottolog', str(tests_dir / 'gl_repos')])


def test_glottologbib():
    pass
    #main(['--repos', str(repos.repos), 'glottologbib'])
