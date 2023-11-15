import pathlib

from cldfbench.scaffold import Template

import pydplace


class DatasetTemplate(Template):
    package = 'pydplace'

    dirs = Template.dirs + [pathlib.Path(pydplace.__file__).parent / 'dataset_template']
