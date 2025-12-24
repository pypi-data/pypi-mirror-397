"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from daccuracy.hint.csv_ import row_transform_h

# --- INPUT


def SymmetrizedRow(idx: float, img_height: float, /) -> float:
    """"""
    return img_height - idx - 1.0


def ColLabelToIdx(label: str, /) -> int:
    """"""
    reference = ord("A")
    if (length := label.__len__()) > 1:
        ords = map(lambda _ltt: ord(_ltt) - reference + 1, reversed(label))
        powers = (26**_idx for _idx in range(length))
        output = sum(_ord * _pwr for _ord, _pwr in zip(ords, powers)) - 1
    else:
        output = ord(label) - reference

    return output


def CSVLineToCoords(
    # line instead of row to avoid confusion with row index of center
    line: h.Sequence[str],
    coordinate_idc: h.Sequence[int] | None,
    row_transform: row_transform_h,
    /,
) -> tuple[int, ...] | None:
    """"""
    if coordinate_idc is None:
        coordinate_idc = tuple(range(line.__len__()))

    try:
        row = float(line[coordinate_idc[0]])
    except ValueError:
        # CSV header line
        return None

    row = row_transform(row)
    remaining = [float(line[_idx]) for _idx in coordinate_idc[1:]]

    return tuple(int(round(_elm)) for _elm in [row] + remaining)


# --- OUTPUT


def HeaderRow(measure_header: h.Sequence[str], /) -> h.Sequence[str]:
    """"""
    measure_header = tuple(_elm.capitalize() for _elm in measure_header)

    return "Ground truth", "Detection", *measure_header
