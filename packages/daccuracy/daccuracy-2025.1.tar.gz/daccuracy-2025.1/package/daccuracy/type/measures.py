"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h


class pointwise_measures_t(h.NamedTuple):
    true_positive: int
    false_positive: int
    false_negative: int
    precision: float
    recall: float
    f1_score: float
    froc_sample: tuple[int, float]
    check_tp_fn_equal_gt: int
    check_tp_fp_equal_dn: int
    dn_2_gt_associations: dict[int, int]


class region_measures_t(h.NamedTuple):
    overlap_mean: float
    overlap_stddev: float
    overlap_min: float
    overlap_max: float
    jaccard_mean: float
    jaccard_stddev: float
    jaccard_min: float
    jaccard_max: float
    precision_p_mean: float
    precision_p_stddev: float
    precision_p_min: float
    precision_p_max: float
    recall_p_mean: float
    recall_p_stddev: float
    recall_p_min: float
    recall_p_max: float
    f1_score_p_mean: float
    f1_score_p_stddev: float
    f1_score_p_min: float
    f1_score_p_max: float
