# Copyright 2020 pydicom3 authors. See LICENSE file for details.
"""Pydicom command line interface program for codify"""

import argparse

import pydicom3.util.codify


default_exclude_size = 100


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    codify_parser = subparsers.add_parser(
        "codify",
        description=(
            "Read a DICOM file and produce the pydicom3 (Python) "
            "code which can create that file"
        ),
        epilog=(
            "Binary data (e.g. pixels) larger than --exclude-size "
            f"(default {default_exclude_size} bytes) is not included. "
            "A dummy line with a syntax error is produced. "
            "Private data elements are not included by default."
        ),
    )

    # Codify existed before as a stand-alone before, re-use it here
    pydicom3.util.codify.set_parser_arguments(codify_parser, default_exclude_size)
    codify_parser.set_defaults(func=pydicom3.util.codify.do_codify)
