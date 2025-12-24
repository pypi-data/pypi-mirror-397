"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as s
from pathlib import Path as path_t

import daccuracy.interface.storage.input as inpt
import daccuracy.task.measures as msrs
import numpy as nmpy
import skimage.io as skio
from daccuracy.interface.console.two_d_labeled_slices_to_3d import ProcessedArguments

array_t = nmpy.ndarray


def LabeledImage(folder: path_t, relabel: str | None, /) -> array_t:
    """"""
    output = None

    for document in sorted(folder.iterdir()):
        if not document.is_file():
            continue

        next_image = inpt.ImageAtPath(document, relabel, None, None, None, None)
        if next_image is None:
            continue
        if next_image.ndim != 2:
            print(f"{next_image.ndim}: Invalid image dimension. Expected=2. Ignoring.")
            continue

        if output is None:
            output = [next_image]
        else:
            previous_image = output[-1]

            n_previous_objects = nmpy.amax(previous_image).item()
            n_next_objects = nmpy.amax(next_image).item()
            next_2_previous_associations = msrs.ObjectAssociations(
                n_next_objects, next_image, n_previous_objects, previous_image
            )
            unassociated = set(range(1, n_next_objects + 1)).difference(
                next_2_previous_associations.keys()
            )
            for new_label, next_label in enumerate(
                unassociated, start=n_previous_objects + 1
            ):
                next_2_previous_associations[next_label] = new_label

            new_image = nmpy.zeros_like(next_image)
            for next_label, previous_label in next_2_previous_associations.items():
                new_image[next_image == next_label] = previous_label
            output.append(new_image)

    return nmpy.dstack(output)


def Main() -> None:
    """"""
    input_path, output_path, relabel = ProcessedArguments(s.argv[1:])

    labeled = LabeledImage(input_path, relabel)

    if output_path.exists():  # Re-test, just in case
        print(f"{output_path}: Existing file or folder; Exiting", file=s.stderr)
        s.exit(-1)

    skio.imsave(output_path, labeled)


if __name__ == "__main__":
    #
    Main()
