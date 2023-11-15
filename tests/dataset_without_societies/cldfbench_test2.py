import pathlib

from pydplace import DatasetWithoutSocieties


class Dataset(DatasetWithoutSocieties):
    id = 'dplace-dataset-test'
    dir = pathlib.Path(__file__).parent
