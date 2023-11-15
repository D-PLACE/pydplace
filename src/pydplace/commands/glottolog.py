"""
Update data derived from Glottolog
"""
import datetime
import contextlib

from cldfcatalog import Catalog

from pydplace import glottolog


def run(args):  # pragma: no cover
    with contextlib.ExitStack() as stack:
        if args.glottolog_version:  # pragma: no cover
            stack.enter_context(Catalog(args.glottolog, tag=args.glottolog_version))
        glottolog.update(
            args.repos,
            args.glottolog,
            str(datetime.date.today().year),
            "Glottolog {0}".format(args.glottolog_version))
