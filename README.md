# pydplace

A Python library to access [D-PLACE](https://d-place.org) data. 

[![Build Status](https://travis-ci.org/D-PLACE/pydplace.svg?branch=master)](https://travis-ci.org/D-PLACE/pydplace)
[![codecov](https://codecov.io/gh/D-PLACE/pydplace/branch/master/graph/badge.svg)](https://codecov.io/gh/D-PLACE/pydplace)
[![PyPI](https://img.shields.io/pypi/v/pydplace.svg)](https://pypi.org/project/pydplace)


To install `pydplace` you need a python installation on your system, running python 2.7 or >3.4. Run

```
pip install pydplace
```

to install the requirements, `pydplace` and the command line interface `dplace`.

`pydplace` is built to access data in a local clone or export of D-PLACE's data repository https://github.com/D-PLACE/dplace-data


## CLI

Command line functionality is implemented via sub-commands of `dplace`. The list of
available sub-commands can be inspected running
```
$ dplace --help
usage: deplace [-h] [--verbosity VERBOSITY] [--log-level LOG_LEVEL]
                 [--repos REPOS]
                 command ...
...

Use 'dplace help <cmd>' to get help about individual commands.
```

## Python API

D-PLACE data can also be accessed programmatically. All functionality is mediated through an instance of `pydplace.api.Repos`, e.g.

```python
>>> from pydplace.api import Repos
>>> api = Repos('.')

