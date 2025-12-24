"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import os.path as osph
import sys as s


def OutputStream(output_path: str, /) -> object:
    """"""
    if output_path == "-":
        return s.stdout

    if osph.exists(output_path):
        print(
            f"{output_path}: Overwriting not supported; "
            f"Delete first to use the same name.",
            file=s.stderr,
        )
        s.exit(-1)

    return open(output_path, "w")
