import pathlib

from pydplace import DatasetWithSocieties


class Dataset(DatasetWithSocieties):
    id = 'dplace-dataset-test'
    dir = pathlib.Path(__file__).parent
