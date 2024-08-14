# pydplace

A Python library to curate [D-PLACE](https://d-place.org) data.

[![Build Status](https://github.com/D-PLACE/pydplace/workflows/tests/badge.svg)](https://github.com/D-PLACE/pydplace/actions?query=workflow%3Atests)
[![PyPI](https://img.shields.io/pypi/v/pydplace.svg)](https://pypi.org/project/pydplace)


To install `pydplace` run

```
pip install pydplace
```

## Usage

### Bootstrapping a `pydplace`-curated dataset

`pydplace` provides a `cldfbench` dataset template to create the skeleton of files and directories for a
D-PLACE dataset, to be run with [cldfbench new](https://github.com/cldf/cldfbench/#creating-a-skeleton-for-a-new-dataset-directory).

Running

```shell
cldfbench new --template dplace_dataset 
```

will create a dataset skeleton looking as follows
```shell
$ tree testtree/
```


### Implementing CLDF creation

Implementing CLDF creation means - as for any other `cldfbench`-curated dataset - filling in the
`cmd_makecldf` method of the `Dataset` subclass in `cldfbench_<id>.py`.


### Running CLDF creation

With `cmd_makecldf` implemented, CLDF creation can be triggered running
```shell
cldfbench makecldf cldfbench_<id>.py
```

The resulting CLDF dataset can be validated running
```shell
pytest
```


### Release workflow

```shell
cldfbench makecldf --glottolog-version v4.8 --with-cldfreadme cldfbench_<id>.py
pytest
cldfbench zenodo --communities dplace cldfbench_<id>.py
cldfbench cldfviz.map cldf --pacific-centered --format png --width 20 --output map.png --with-ocean --no-legend
cldfbench readme cldfbench_<id>.py
dplace check cldfbench_<id>.py
git commit -a -m"release v3.0"
git push origin
dplace release cldfbench_<id>.py v3.0
```

Then create a release on GitHub, thereby pushing the repos to Zenodo.


### Using the datasets

```shell
$ csvgrep -c Var_ID -m AnnualMeanTemperature cldf/data.csv | csvstat -c Value
  4. "Value"

	Type of data:          Number
	Contains null values:  False
	Unique values:         1649
	Smallest value:        -19,45
	Largest value:         29,153
	Sum:                   32.700,717
	Mean:                  16,449
	Median:                19,721
	StDev:                 9,684
	Most common values:    14,392 (9x)
	                       21,66 (6x)
	                       6,96 (6x)
	                       23,335 (5x)
	                       21,619 (5x)

Row count: 1988
```