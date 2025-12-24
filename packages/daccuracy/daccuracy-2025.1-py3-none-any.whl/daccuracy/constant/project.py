"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from daccuracy import __version__ as VERSION

PROJECT_NAME = "DAccuracy"
NAME_MEANING = "Detection and Segmentation Accuracy Measures"
SHORT_DESCRIPTION = "Computation of some Standard Performance Measures of Object Detection and Segmentation"

DESCRIPTION = f"""[As of version {VERSION}]

3 modes:
    - one-to-one: one ground-truth (csv, image, or Numpy array) vs. one detection (image or Numpy array);
    - one-to-many: one ground-truth vs. several detections (folder of detections);
    - many-to-many: several ground-truths (folder of ground-truths) vs. corresponding detections (folder of detections).

In many-to-many mode, each detection file must have a counterpart ground-truth file with the same name,
but not necessarily the same extension.
"""
