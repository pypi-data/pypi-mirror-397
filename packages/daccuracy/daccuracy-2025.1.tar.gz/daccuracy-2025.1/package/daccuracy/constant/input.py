"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from collections import defaultdict as default_dict_t

MUST_CHECK_LABELING = default_dict_t(lambda: True)
MUST_CHECK_LABELING |= {".csv": False}

ERROR_MESSAGE = default_dict_t(lambda: "image or unreadable by imageio")
ERROR_MESSAGE |= {
    ".npy": "Numpy file or unreadable",
    ".npz": "Numpy file or unreadable",
    ".csv": "CSV file or unreadable",
}
