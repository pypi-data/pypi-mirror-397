"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import glob
import sys as s
import typing as h
from collections import defaultdict as default_dict_t
from csv import reader as csv_reader_t
from pathlib import Path as path_t

import daccuracy.interface.storage.csv_ as csio
import daccuracy.task.image as imge
import numpy as nmpy
import skimage.io as skio
import skimage.morphology as mrph
import skimage.segmentation as sgmt
from daccuracy.constant.input import ERROR_MESSAGE, MUST_CHECK_LABELING
from daccuracy.hint.csv_ import row_transform_h
from daccuracy.hint.input import img_shape_h
from daccuracy.task.image import LabeledImageIsValid

array_t = nmpy.ndarray

# See at the end of module.
_LOADING_FUNCTION = default_dict_t(lambda: _ImageAtImagePath)


def GroundTruthPathForDetection(
    detection_name: str,  # Without extension
    ground_truth_path: path_t,
    ground_truth_folder: path_t,
    mode: str,
    /,
) -> path_t | None:
    """"""
    if mode == "one-to-one":
        output = None
        pattern = ground_truth_folder / (detection_name + ".*")
        for path in glob.iglob(str(pattern)):
            output = path_t(path)
            break

        return output

    # mode = 'one-to-many'
    return ground_truth_path


def ImageAtPath(
    path: path_t,
    relabel: str | None,
    shifts: h.Sequence[int] | None,
    shape: img_shape_h | None,
    coordinate_idc: h.Sequence[int] | None,
    row_transform: row_transform_h | None,
    /,
) -> array_t | None:
    """"""
    extension = path.suffix.lower()
    LoadingFunction = _LOADING_FUNCTION[extension]
    try:
        output = LoadingFunction(path, shape, coordinate_idc, row_transform)
        if shifts is not None:
            output = imge.ShiftedVersion(output, shifts)
        if relabel == "seq":
            output, *_ = sgmt.relabel_sequential(output)
        elif relabel == "full":
            output = mrph.label(output > 0)

        if MUST_CHECK_LABELING[extension]:
            is_valid, issues = LabeledImageIsValid(output, path)
            if not is_valid:
                print(f"{path}: Incorrectly labeled image:\n{issues}", file=s.stderr)
                output = None
    except BaseException as exc:
        print(f"{path}: Not a valid {ERROR_MESSAGE[extension]}\n({exc})", file=s.stderr)
        output = None

    return output


def _ImageAtImagePath(
    path: path_t,
    _: img_shape_h | None,
    __: h.Sequence[int] | None,
    ___: row_transform_h | None,
    /,
) -> array_t:
    """"""
    output = skio.imread(path)

    if (max_value := nmpy.amax(output)) == nmpy.iinfo(output.dtype).max:
        print(
            f"{path}: Image in {output.dtype.name} format attaining its maximum value {max_value}.\n"
            f"There is a risk that the number of objects exceeded the image format capacity.\n"
            f"Switching to NPY or NPZ Numpy formats might be necessary."
        )

    return output


def _ImageAtNumpyPath(
    path: path_t,
    _: img_shape_h | None,
    __: h.Sequence[int] | None,
    ___: row_transform_h | None,
    /,
) -> array_t:
    """"""
    output = nmpy.load(str(path))

    if hasattr(output, "keys"):
        first_key = tuple(output.keys())[0]
        output = output[first_key]

    if nmpy.issubdtype(output.dtype, nmpy.floating):
        # Try to convert to an integer dtype. If this fails, then leave output as is. Image invalidity will be noticed
        # later by "LabeledImageIsValid". For non-integer dtypes other than floating, conversion is not even attempted,
        # and invalidity will therefore also be noticed later on.
        as_integer = output.astype(nmpy.uint64)
        back_to_float = as_integer.astype(output.dtype)
        if nmpy.array_equal(back_to_float, output):
            output = as_integer

    return output


def _ImageFromCSV(
    path: path_t,
    shape: img_shape_h | None,
    coordinate_idc: h.Sequence[int] | None,
    row_transform: row_transform_h | None,
    /,
) -> array_t:
    """"""
    # Note: using nmpy.uint64 provides the highest limit on the maximum number of objects. However, care must be taken
    # when using the elements of an array of this dtype as indices after some arithmetic. Indeed, an uint64 number then
    # becomes a float64. (Other automatic type conversions arise for other unsigned dtypes.) To avoid this, extracted
    # elements must be converted to Python type int (with.item()) before applying arithmetic operations.
    output = nmpy.zeros(shape, dtype=nmpy.uint64)

    # Leave this here since the symmetrization transform must be defined for each image (shape[0])
    if row_transform is None:
        row_transform = lambda f_idx: csio.SymmetrizedRow(f_idx, float(shape[0]))

    with open(path) as csv_accessor:
        csv_reader = csv_reader_t(csv_accessor)
        # Do not enumerate csv_reader below since some rows might be dropped
        label = 1
        for line in csv_reader:
            coordinates = csio.CSVLineToCoords(line, coordinate_idc, row_transform)
            if coordinates is not None:
                if coordinates.__len__() != output.ndim:
                    print(
                        f"{coordinates.__len__()} != {output.ndim}: Mismatch between (i) CSV coordinates "
                        f"and (ii) detection dimension for {path}"
                    )
                    output = None
                    break
                if any(_elm < 0 for _elm in coordinates) or nmpy.any(
                    nmpy.greater_equal(coordinates, output.shape)
                ):
                    expected = (f"0<= . <= {_sze - 1}" for _sze in output.shape)
                    expected = ", ".join(expected)
                    print(
                        f"{coordinates}: CSV coordinates out of bound for detection {path}; Expected={expected}"
                    )
                    output = None
                    break
                if output[coordinates] > 0:
                    print(
                        f"{path}: Multiple GTs at same position (due to rounding or duplicates)"
                    )
                    output = None
                    break
                output[coordinates] = label
                label += 1

    return output


_LOADING_FUNCTION |= {
    ".npy": _ImageAtNumpyPath,
    ".npz": _ImageAtNumpyPath,
    ".csv": _ImageFromCSV,
}
