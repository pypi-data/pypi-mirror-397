"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

row_transform_h = h.Callable[[float], float]
coord_trans_h = tuple[h.Sequence[int], row_transform_h | None]
