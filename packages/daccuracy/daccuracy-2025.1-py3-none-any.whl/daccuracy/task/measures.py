"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import daccuracy.task.image as imge
import numpy as nmpy
import scipy.optimize as spop
import skimage.segmentation as sisg
from daccuracy.constant.measures import MEASURE_COUNTS_HEADER
from daccuracy.hint.measures import (
    cost_h,
    full_measures_h,
    full_pointwise_measures_h,
    full_pw_region_measures_h,
    measure_fct_h,
)
from daccuracy.type.measures import pointwise_measures_t, region_measures_t

array_t = nmpy.ndarray


def AccuracyMeasures(
    ground_truth: array_t,
    detection: array_t,
    measure_fct: measure_fct_h,
    should_exclude_border: bool,
    tolerance: float,
    /,
) -> full_measures_h:
    """"""
    if should_exclude_border:
        sisg.clear_border(ground_truth, out=ground_truth)
        sisg.clear_border(detection, out=detection)
        ground_truth, *_ = sisg.relabel_sequential(ground_truth)
        detection, *_ = sisg.relabel_sequential(detection)

    return measure_fct(ground_truth, detection, tolerance=tolerance)


def MeasuresAsStrings(measures: full_measures_h, /) -> list[str]:
    """"""
    output = [elm.__str__() for elm in measures[:2]]  # Object counts

    for group in measures[2:]:
        output.extend(elm.__str__() for elm in group._asdict().values())

    return output


def PointwiseMeasures(
    ground_truth: array_t | None,
    detection: array_t | None,
    /,
    *,
    tolerance: float = 0.0,
) -> tuple[str, ...] | full_pointwise_measures_h:
    """"""
    if ground_truth is None:
        return *MEASURE_COUNTS_HEADER, *pointwise_measures_t._fields

    if tolerance >= 1.0:
        detection = imge.DetectionWithTolerance(detection, tolerance)

    n_gt_objects = nmpy.amax(ground_truth).item()
    n_dn_objects = nmpy.amax(detection).item()

    dn_2_gt_associations = ObjectAssociations(
        n_dn_objects, detection, n_gt_objects, ground_truth
    )
    correct = dn_2_gt_associations.__len__()
    missed = n_gt_objects - correct
    invented = n_dn_objects - correct

    output = (
        n_gt_objects,
        n_dn_objects,
        _StandardMeasuresFromCounts(correct, missed, invented, dn_2_gt_associations),
    )

    return output


def PWandRegionMeasures(
    ground_truth: array_t | None,
    detection: array_t | None,
    /,
    *,
    tolerance: float = 0.0,
) -> tuple[str, ...] | full_pw_region_measures_h:
    """"""
    if ground_truth is None:
        return (
            *MEASURE_COUNTS_HEADER,
            *pointwise_measures_t._fields,
            *region_measures_t._fields,
        )

    n_gt_objects, n_dn_objects, pointwise_measures = PointwiseMeasures(
        ground_truth, detection, tolerance=tolerance
    )

    overlap, jaccard, precision_p, recall_p, f1_score_p = [], [], [], [], []
    for dn_label, gt_label in pointwise_measures.dn_2_gt_associations.items():
        ground_truth_obj = ground_truth == gt_label
        detected_obj = detection == dn_label

        gt_area = nmpy.count_nonzero(ground_truth_obj)
        dn_area = nmpy.count_nonzero(detected_obj)
        union_area = nmpy.count_nonzero(nmpy.logical_or(ground_truth_obj, detected_obj))
        intersection_area = nmpy.count_nonzero(
            nmpy.logical_and(ground_truth_obj, detected_obj)
        )
        assert intersection_area > 0, "This should never happen; Contact Developer"
        one_precision = intersection_area / dn_area
        one_recall = intersection_area / gt_area

        overlap.append(100.0 * intersection_area / min(gt_area, dn_area))
        jaccard.append(intersection_area / union_area)
        precision_p.append(one_precision)
        recall_p.append(one_recall)
        f1_score_p.append(
            2.0 * one_precision * one_recall / (one_precision + one_recall)
        )

    measures = {}
    for name, values in zip(
        ("overlap", "jaccard", "precision_p", "recall_p", "f1_score_p"),
        (overlap, jaccard, precision_p, recall_p, f1_score_p),
    ):
        for reduction, as_numpy in zip(
            ("mean", "stddev", "min", "max"), ("mean", "std", "amin", "amax")
        ):
            ReductionFunction = getattr(nmpy, as_numpy)
            measures[f"{name}_{reduction}"] = ReductionFunction(values).item()

    region_measures = region_measures_t(**measures)

    return n_gt_objects, n_dn_objects, pointwise_measures, region_measures


def ObjectAssociations(
    n_ref_objects: int,
    ref_img: array_t,
    n_objects: int,
    image: array_t,
    /,
    *,
    cost: cost_h = "IoU",
    threshold: float = 1.0,
) -> dict[int, int]:
    """"""
    assert cost in h.get_args(cost_h), (cost, h.get_args(cost_h))

    # TODO: Add a parameter to select the threshold.
    # TODO: Add parameter to let the choice between IoU, IoRef, IoCrr.
    assignment_costs = nmpy.ones((n_ref_objects, n_objects), dtype=nmpy.float64)

    for ref_label in range(1, n_ref_objects + 1):
        ref_obj = ref_img == ref_label

        corresponding_labels = nmpy.unique(image[ref_obj])
        if corresponding_labels[0] == 0:
            corresponding_labels = corresponding_labels[1:]

        for crr_label in corresponding_labels:
            crr_label = crr_label.item()
            corresponding_obj = image == crr_label

            intersection_area = nmpy.count_nonzero(
                nmpy.logical_and(corresponding_obj, ref_obj)
            )
            if cost == "IoU":
                denominator = nmpy.logical_or(corresponding_obj, ref_obj)
            elif cost == "IoRef":
                denominator = ref_obj
            else:
                denominator = corresponding_obj
            denominator = nmpy.count_nonzero(denominator)

            assignment_costs[ref_label - 1, crr_label - 1] = (
                1.0 - intersection_area / denominator
            )

    row_ind, col_ind = spop.linear_sum_assignment(assignment_costs)
    valid_idc = assignment_costs[row_ind, col_ind] < threshold
    output = dict(zip(row_ind[valid_idc] + 1, col_ind[valid_idc] + 1))

    return {_.item(): __.item() for _, __ in output.items()}


def _StandardMeasuresFromCounts(
    correct: int, missed: int, invented: int, dn_2_gt_associations: dict[int, int], /
) -> pointwise_measures_t:
    """"""
    true_positive = correct
    false_positive = invented
    false_negative = missed

    if true_positive > 0:
        precision = true_positive / (true_positive + false_positive)
        recall = true_positive / (true_positive + false_negative)
    else:
        precision = 0.0
        recall = 0.0
    if (precision > 0.0) and (recall > 0.0):
        f1_score = 2.0 * precision * recall / (precision + recall)
    else:
        f1_score = 0.0

    true_positive_rate = recall
    froc_sample = (false_positive, true_positive_rate)

    output = pointwise_measures_t(
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        froc_sample=froc_sample,
        check_tp_fn_equal_gt=correct + missed,
        check_tp_fp_equal_dn=correct + invented,
        dn_2_gt_associations=dn_2_gt_associations,
    )

    return output
