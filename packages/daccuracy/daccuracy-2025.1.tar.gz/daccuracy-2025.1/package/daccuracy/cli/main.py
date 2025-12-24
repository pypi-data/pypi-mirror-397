"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as s

import daccuracy.interface.console.main as cnsl
from daccuracy.main import ComputeAndOutputMeasures


def Main():
    """"""
    options = cnsl.ProcessedArguments(s.argv[1:])
    ComputeAndOutputMeasures(options)
    if options["output_accessor"] is not s.stdout:
        options["output_accessor"].close()


if __name__ == "__main__":
    #
    Main()
