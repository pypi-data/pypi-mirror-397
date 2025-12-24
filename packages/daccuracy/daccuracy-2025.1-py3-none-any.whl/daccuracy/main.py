"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from pathlib import Path as path_t

from numpy import ndarray as array_t

import daccuracy.interface.storage.csv_ as csio
import daccuracy.interface.storage.input as inpt
import daccuracy.task.image as imge
import daccuracy.task.measures as msrs
from daccuracy.config.csv_ import COL_SEPARATOR
from daccuracy.hint.csv_ import coord_trans_h, row_transform_h
from daccuracy.hint.measures import measure_fct_h
from daccuracy.interface.window.pypl import (
    PrepareMixedGTDetectionImage,
    ShowPreparedImages,
)


def ComputeAndOutputMeasures(
    options: dict[str, h.Any], /
) -> tuple[array_t, int, int, int] | None:
    """"""
    output = None

    ground_truth_path: path_t = options["ground_truth_path"]
    relabel_gt: str | None = options["relabel_gt"]
    detection_path: path_t = options["detection_path"]
    relabel_dn: str | None = options["relabel_dn"]
    coord_trans: coord_trans_h | None = options["coord_trans"]
    dn_shifts: h.Sequence[int] | None = options["dn_shifts"]
    should_exclude_border: bool = options["should_exclude_border"]
    tolerance: float = options["tolerance"]
    output_format: str = options["output_format"]
    should_return_image: bool = options["should_return_image"]
    should_show_image: bool = options["should_show_image"]
    output_accessor = options["output_accessor"]

    if ground_truth_path.is_file():
        gt_dn_mode = "one-to-many"
    else:
        gt_dn_mode = "one-to-one"

    if gt_dn_mode == "one-to-many":
        ground_truth_folder = None
        coordinate_idc, row_transform, measure_fct = _TransformationAndMeasure(
            ground_truth_path, coord_trans
        )
        header = measure_fct(None, None)
    else:
        ground_truth_folder = ground_truth_path
        coordinate_idc = row_transform = measure_fct = None
        header = msrs.PWandRegionMeasures(None, None)
    header = csio.HeaderRow(header)

    if detection_path.is_file():
        detection_folder = detection_path.parent
        detection_name = detection_path.name
    else:
        detection_folder = detection_path
        detection_name = None

    if output_format == "csv":
        print(COL_SEPARATOR.join(header), file=output_accessor)
        name_field_len = 0
    else:
        name_field_len = max(_.__len__() for _ in header)

    figures_are_waiting = False
    for document in detection_folder.iterdir():
        if (not document.is_file()) or (
            (detection_name is not None) and (document.name != detection_name)
        ):
            continue

        detection = inpt.ImageAtPath(document, relabel_dn, dn_shifts, None, None, None)
        if detection is None:
            continue

        ground_truth_path = inpt.GroundTruthPathForDetection(
            document.stem, ground_truth_path, ground_truth_folder, gt_dn_mode
        )
        if ground_truth_path is None:
            continue

        if gt_dn_mode == "one-to-one":
            coordinate_idc, row_transform, measure_fct = _TransformationAndMeasure(
                ground_truth_path, coord_trans
            )
        ground_truth = inpt.ImageAtPath(
            ground_truth_path,
            relabel_gt,
            None,
            detection.shape,
            coordinate_idc,
            row_transform,
        )
        if ground_truth is None:
            continue

        if (gt_shape := ground_truth.shape) != (dn_shape := detection.shape):
            if fixable := (sorted((ground_truth.ndim, detection.ndim)) == [2, 3]):
                ground_truth, detection = imge.WithFixedDimensions(
                    ground_truth, detection
                )
            if (not fixable) or (ground_truth is None) or (detection is None):
                print(
                    f"{gt_shape} != {dn_shape}: "
                    f"Ground-truth and detection shapes mismatch "
                    f"for images {ground_truth_path} and {document}"
                )
                continue

        measures = msrs.AccuracyMeasures(
            ground_truth, detection, measure_fct, should_exclude_border, tolerance
        )
        measures_as_str = msrs.MeasuresAsStrings(measures)
        output_row = [ground_truth_path.name, document.name] + measures_as_str

        if output_format == "csv":
            print(COL_SEPARATOR.join(output_row), file=output_accessor)
        else:
            for name, value in zip(header, output_row):
                print(f"{name:>{name_field_len}} = {value}", file=output_accessor)
        if should_show_image and (ground_truth.ndim == 2):
            PrepareMixedGTDetectionImage(
                ground_truth,
                detection,
                dn_2_gt_associations=measures[2].dn_2_gt_associations,
            )
            if ground_truth_path.suffix.lower() != ".csv":
                PrepareMixedGTDetectionImage(ground_truth, detection, mode="pixel")
            figures_are_waiting = True
        elif should_return_image and (ground_truth.ndim == 2) and (output is None):
            output = imge.MixedGTDetectionImage(
                ground_truth,
                detection,
                dn_2_gt_associations=measures[2].dn_2_gt_associations,
            )

    if figures_are_waiting:
        ShowPreparedImages()

    return output


def _TransformationAndMeasure(
    ground_truth_path: path_t, coord_trans: coord_trans_h | None, /
) -> tuple[h.Sequence[int] | None, row_transform_h | None, measure_fct_h]:
    """"""
    coordinate_idc = row_transform = None

    if ground_truth_path.suffix.lower() == ".csv":
        if coord_trans is None:
            row_transform = lambda f_idx: f_idx
        else:
            coordinate_idc, row_transform = coord_trans
        measure_fct = msrs.PointwiseMeasures
    else:
        measure_fct = msrs.PWandRegionMeasures

    return coordinate_idc, row_transform, measure_fct
