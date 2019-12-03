"""
Update data derived from Glottolog
"""
import datetime
import contextlib

from clldutils.clilib import PathType
from cldfcatalog import Catalog

from pydplace import glottolog


def register(parser):
    parser.add_argument('glottolog', help='clone of glottolog/glottolog', type=PathType(type='dir'))
    parser.add_argument('--glottolog-version', default=None)


def run(args):
    with contextlib.ExitStack() as stack:
        if args.glottolog_version:  # pragma: no cover
            stack.enter_context(Catalog(args.glottolog, tag=args.glottolog_version))
        glottolog.update(
            args.repos,
            args.glottolog,
            str(datetime.date.today().year),
            "Glottolog {0}".format(args.glottolog_version))
