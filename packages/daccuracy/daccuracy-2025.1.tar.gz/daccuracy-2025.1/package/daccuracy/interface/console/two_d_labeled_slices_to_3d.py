"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as s
import typing as h
from argparse import ArgumentParser as argument_parser_t
from argparse import RawDescriptionHelpFormatter
from pathlib import Path as path_t

from daccuracy.constant.two_d_labeled_slices_to_3d import DESCRIPTION

import __main__ as main_package


def ProcessedArguments(
    arguments: h.Sequence[str], /
) -> tuple[path_t, path_t, str | None]:
    """"""
    parser = _ArgumentParser()
    arguments = parser.parse_args(arguments)

    input_path = path_t(arguments.input_path)
    output_path = path_t(arguments.output_path)
    relabel = arguments.relabel

    if not input_path.is_dir():
        print(f"{input_path}: Not a folder", file=s.stderr)
        s.exit(-1)
    if output_path.exists():
        print(f"{output_path}: Existing file or folder; Exiting", file=s.stderr)
        s.exit(-1)

    return input_path, output_path, relabel


def _ArgumentParser() -> argument_parser_t:
    """"""
    output = argument_parser_t(
        prog=path_t(main_package.__file__).stem,
        description=DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )

    output.add_argument(
        "--2d",
        type=str,
        required=True,
        dest="input_path",
        metavar="Input_folder",
        help="Folder containing a set of labeled 2-dimensional images.",
    )
    output.add_argument(
        "--relabel",
        type=str,
        choices=("seq", "full"),
        default=None,
        dest="relabel",
        help="If present, this option instructs to relabel the 2-dimensional images with sequential labels (seq),"
        "or to fully relabel the non-zero regions of the 2-dimensional images with maximum connectivity (full).",
    )
    output.add_argument(
        "--3d",
        type=str,
        required=True,
        dest="output_path",
        metavar="Output_file",
        help="File to store the coherently labeled 3-dimensional image.",
    )

    return output
