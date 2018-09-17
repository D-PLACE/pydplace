"""
Main command line interface of the pydplace package.

Like programs such as git, this cli splits its functionality into sub-commands
(see e.g. https://docs.python.org/2/library/argparse.html#sub-commands).
The rationale behind this is that while a lot of different tasks may be
triggered using this cli, most of them require common configuration.

The basic invocation looks like

    dplace [OPTIONS] <command> [args]

"""
from __future__ import unicode_literals, division, print_function
import sys

from clldutils.clilib import ArgumentParserWithLogging

import pydplace
from pydplace.api import Repos
import pydplace.commands
assert pydplace.commands


def main():  # pragma: no cover
    parser = ArgumentParserWithLogging(pydplace.__name__)
    parser.add_argument(
        '--repos',
        type=Repos,
        default=Repos('dplace-data'),
        help='Location of clone of D_PLACE/dplace-data (defaults to ./dplace-data)')
    sys.exit(parser.main())
