from pydplace import __main__
from pydplace import commands


def test_extract(tmpdir, repos, mocker):
    res = tmpdir.join('res.csv')
    commands.extract(mocker.Mock(repos=repos, args=[str(res)]))
    assert len(res.read_text('utf8').split('\n')) == 13959
