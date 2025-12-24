"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import daccuracy.task.image as imge
import numpy as nmpy
from matplotlib import pyplot as pypl
from matplotlib.patches import Patch as patch_t

array_t = nmpy.ndarray


def PrepareMixedGTDetectionImage(
    ground_truth: array_t,
    detection: array_t,
    /,
    *,
    mode: h.Literal["object", "pixel"] = "object",
    dn_2_gt_associations: dict[int, int] = None,
) -> None:
    """"""
    image, n_correct, n_missed, n_invented = imge.MixedGTDetectionImage(
        ground_truth, detection, mode=mode, dn_2_gt_associations=dn_2_gt_associations
    )
    if mode == "object":
        n_correct = f": {n_correct}"
        n_missed = f": {n_missed} (total)"
        n_invented = f": {n_invented}"
    elif mode == "pixel":
        n_correct = n_missed = n_invented = ""
    else:
        raise ValueError(f"{mode}: Invalid mode")

    patches = [
        patch_t(edgecolor=(0, 0, 0), facecolor=_clr, label=_lbl)
        for _clr, _lbl in zip(
            ((0, 0, 1), (1, 1, 0), (1, 1, 1), (1, 0, 0)),
            (
                f"Correct{n_correct}",
                f"Missed{n_missed}",
                "Missed (due to fusion)",
                f"Invented{n_invented}",
            ),
        )
    ]
    axes = pypl.imshow(image)  # Do not use matshow: color image
    axes.figure.suptitle(f'Mode = "{mode}"')
    pypl.legend(handles=patches, bbox_to_anchor=(1.01, 1.0), loc=2, borderaxespad=0.0)


def ShowPreparedImages() -> None:
    """"""
    pypl.show()
