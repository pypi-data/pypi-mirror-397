"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as s
import typing as h
from pathlib import Path as path_t

import numpy as nmpy
import scipy.ndimage as spim
import skimage.morphology as mrph
from daccuracy.config.output import MIN_N_DILATIONS

array_t = nmpy.ndarray


def LabeledImageIsValid(image: array_t, path: path_t, /) -> tuple[bool, str | None]:
    """"""
    issues = []

    if nmpy.issubdtype(image.dtype, nmpy.inexact):
        issues.append(
            f"{path}: Invalid image type {image.dtype}; Expected=integer types"
        )

    if (minimum := nmpy.amin(image).item()) > 0:
        issues.append(f"{path}: No background in image (no label equal to zero)")
    if minimum == (maximum := nmpy.amax(image).item()):
        issues.append(
            f"{path}: Only one value present in image: {minimum}; Expected=at least 0 and 1"
        )

    missing = []
    repeated = []
    for label in range(1, maximum + 1):
        just_one = image == label
        if not nmpy.any(just_one):
            missing.append(str(label))
        else:
            # Profiling shows that this is the bottleneck.
            _, n_islands = mrph.label(just_one, return_num=True)
            if n_islands > 1:
                repeated.append(f"{label} repeated {n_islands} times")

    if missing.__len__() > 0:
        issues.append(f"{path}: Missing labels: " + ", ".join(missing))
    if repeated.__len__() > 0:
        issues.append("\n".join(repeated))
    if is_valid := (issues.__len__() == 0):
        issues = None
    else:
        issues = "\n".join(issues)

    return is_valid, issues


def WithFixedDimensions(
    ground_truth: array_t, detection: array_t, /
) -> tuple[array_t | None, array_t | None]:
    """"""
    if ground_truth.ndim == 3:
        ground_truth = _AsOneGrayChannelOrNone(ground_truth)
    else:
        detection = _AsOneGrayChannelOrNone(detection)

    return ground_truth, detection


def ShiftedVersion(image: array_t, shifts: h.Sequence[int], /) -> array_t:
    """"""
    if shifts.__len__() != image.ndim:
        print(
            f"{shifts}/{image.ndim}: Incompatible requested shifts and image dimension. Using image as-is.",
            file=s.stderr,
        )
        return image

    output = image

    everything = slice(None)
    for d_idx in range(image.ndim):
        if (shift := shifts[d_idx]) != 0:
            output = nmpy.roll(output, shift, axis=d_idx)
            if shift > 0:
                slice_ = slice(shift)
            else:
                slice_ = slice(shift, None)
            slices = (
                (d_idx * (everything,))
                + (slice_,)
                + ((image.ndim - d_idx - 1) * (everything,))
            )
            output[slices] = 0

    return output


def DetectionWithTolerance(detection: array_t, tolerance: float, /) -> array_t:
    """"""
    if tolerance < 1.0:
        return detection

    output = nmpy.zeros_like(detection)

    distance_map = spim.distance_transform_edt(detection != 1)
    output[distance_map <= tolerance] = 1

    for label in range(2, nmpy.amax(detection).item() + 1):
        current_map = spim.distance_transform_edt(detection != label)
        closer_bmap = current_map < distance_map
        output[nmpy.logical_and(closer_bmap, current_map <= tolerance)] = label
        distance_map[closer_bmap] = current_map[closer_bmap]

    return output


def MixedGTDetectionImage(
    ground_truth: array_t,
    detection: array_t,
    /,
    *,
    mode: h.Literal["object", "pixel"] = "object",
    dn_2_gt_associations: dict[int, int] = None,
) -> tuple[array_t, int, int, int]:
    """"""
    if mode == "object":
        if dn_2_gt_associations is None:
            raise ValueError(
                f"Detection-to-Ground-truth associations "
                f'must be passed for mode "{mode}".'
            )

        smallest_dn_area = nmpy.inf

        correct = nmpy.zeros_like(detection, dtype=nmpy.bool_)
        n_correct = 0
        for label in dn_2_gt_associations.keys():
            just_one = detection == label
            smallest_dn_area = min(smallest_dn_area, nmpy.count_nonzero(just_one))
            correct[just_one] = True
            n_correct += 1

        missed = nmpy.zeros_like(ground_truth, dtype=nmpy.bool_)
        n_missed = 0
        gt_detected = tuple(dn_2_gt_associations.values())
        for label in range(1, nmpy.amax(ground_truth).item() + 1):
            if label not in gt_detected:
                missed[ground_truth == label] = True
                n_missed += 1

        n_missed_integer = n_missed

        invented = nmpy.zeros_like(detection, dtype=nmpy.bool_)
        n_invented = 0
        dn_associated = tuple(dn_2_gt_associations.keys())
        for label in range(1, nmpy.amax(detection).item() + 1):
            if label not in dn_associated:
                just_one = detection == label
                smallest_dn_area = min(smallest_dn_area, nmpy.count_nonzero(just_one))
                invented[just_one] = True
                n_invented += 1

        if nmpy.count_nonzero(missed) == n_missed_integer:
            if nmpy.isinf(smallest_dn_area):
                n_iterations = MIN_N_DILATIONS
            else:
                radius = nmpy.sqrt(smallest_dn_area / nmpy.pi)
                n_iterations = max(MIN_N_DILATIONS, int(nmpy.ceil(radius)))
            distance_map = spim.distance_transform_edt(missed == False)
            missed[distance_map <= n_iterations] = True
    elif mode == "pixel":
        ground_truth = ground_truth > 0
        detection = detection > 0

        correct = nmpy.logical_and(ground_truth, detection)
        missed = nmpy.logical_and(ground_truth, nmpy.logical_not(detection))
        invented = nmpy.logical_and(nmpy.logical_not(ground_truth), detection)

        n_correct = correct.sum().item()
        n_missed = missed.sum().item()
        n_invented = invented.sum().item()
    else:
        raise ValueError(f"{mode}: Invalid mode")

    red = 255 * nmpy.logical_or(invented, missed)
    green = 255 * missed
    blue = 255 * correct
    image = nmpy.dstack((red, green, blue)).astype(nmpy.uint8)

    return image, n_correct, n_missed, n_invented


def _AsOneGrayChannelOrNone(image: array_t, /) -> array_t | None:
    """"""
    if (
        (3 <= image.shape[2] <= 4)
        and nmpy.array_equal(image[..., 0], image[..., 1])
        and nmpy.array_equal(image[..., 0], image[..., 2])
    ):
        if (image.shape[2] == 3) or nmpy.all(image[..., 3] == image[0, 0, 3]):
            return image[..., 0]

    return None
