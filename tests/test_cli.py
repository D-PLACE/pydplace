import os
import logging
import pathlib

try:
    import fiona
except ImportError:  # pragma: no cover
    fiona = None

import pytest

from pydplace.__main__ import main


def test_help(capsys):
    main([])
    out, _ = capsys.readouterr()
    assert 'usage' in out


def test_check(capsys):
    from clldutils.clilib import ParserError

    with pytest.raises(SystemExit):
        main(['check', '-h'])
    out, _ = capsys.readouterr()
    assert 'check' in out

    with pytest.raises(ParserError):
        main(['check', __file__], log=logging.getLogger(__name__))


def test_glottologbib():
    pass
    #main(['--repos', str(repos.repos), 'glottologbib'])
