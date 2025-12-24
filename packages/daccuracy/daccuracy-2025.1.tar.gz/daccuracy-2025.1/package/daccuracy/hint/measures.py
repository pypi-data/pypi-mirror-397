"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from daccuracy.type.measures import pointwise_measures_t, region_measures_t

full_pointwise_measures_h = tuple[int, int, pointwise_measures_t]
full_pw_region_measures_h = tuple[int, int, pointwise_measures_t, region_measures_t]
full_measures_h = full_pointwise_measures_h | full_pw_region_measures_h
measure_fct_h = h.Callable[..., tuple[str, ...] | full_measures_h]

cost_h = h.Literal["IoU", "IoRef", "IoCrr"]
