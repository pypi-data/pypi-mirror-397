"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

MEASURE_COUNTS_HEADER = ("n ground truths", "n detections")

MEASURES_DESCRIPTIONS = """
** "Pointwise" Measures **
Measures accounting for presence or absence only (object shapes are not accounted for).
    * true_positive:
        Number of detected objects present in ground-truth.
    * false_positive:
        Number of detected objects not present in ground-truth.
    * false_negative:
        Number of ground-truth objects not present in detection.
    * precision (a.k.a. positive predictive value):
        Correctness among detected objects.
        = true_positive / (true_positive + false_positive)
    * recall (a.k.a. sensitivity, true positive rate, hit rate):
        Exhaustiveness of detected objects.
        = true_positive / (true_positive + false_negative)
    * f1_score:
        Harmonic mean of precision and sensitivity; best=1, worst=0.
        = 2.0 * precision * recall / (precision + recall)
    * froc_sample:
        (false_positive, recall).
        = One sample of the Free-response Receiver Operating Characteristic (FROC) curve

** Region Measures **
Measures accounting for presence/absence and shape.
They are meaningful only if the ground-truth is specified through an image, not a CSV file.
They are computed for each detected object, then averaged (standard deviation, minimum, and maximum are also computed).
Notations: gt=ground-truth, dn=detection.
    * overlap:
        perfect match=>100; total miss=>0.
        = 100.0 * intersection_area_between_gt_and_dn / min(gt_area, dn_area)
    * jaccard:
        perfect match=>1; total miss=>0.
        = intersection_area_between_gt_and_dn / union_area_of_gt_and_dn
    * precision_p (pixelwise-precision):
        perfect match=>1; total miss=>0.
        = intersection_area_between_gt_and_dn / dn_area
    * recall_p (pixelwise-recall):
        perfect match=>1; total miss=>0.
        = intersection_area_between_gt_and_dn / gt_area
    * f1_score_p (pixelwise-f1 score).

** Checking Values **
Values useful for checking the coherence between some measures.
    * check_tp_fn_equal_gt:
        Must be equal to the number of ground-truth objects.
        = true_positive + false_negative
    * check_tp_fp_equal_dn:
        Must be equal to the number of detected objects.
        = true_positive + false_positive
    * dn_2_gt_associations:
        Python dictionary of the ground-truth labels (dictionary values) associated with the detection labels (dictionary keys).

** Notes **
    * Accuracy:
        Cannot be computed since the number of true negatives has no meaning in the context of DAccuracy.
        = (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative)
    * Specificity (a.k.a. selectivity, true negative rate):
        Cannot be computed. See note on Accuracy.
        = true_negative / (true_negative + false_positive)
    * Receiver Operating Characteristic (ROC) curve:
        Curve of the true positive rate (recall) against the false positive rate (equal to: 1 − specificity).
        Since the specificity cannot be computed, so does the ROC curve samples.
    * Free-response ROC (FROC) curve:
        Alternative to the ROC curve obtained by replacing the false positive rate with the number of false positives when true negatives cannot be defined.

References:
    https://en.wikipedia.org/wiki/Sensitivity_and_specificity
    https://en.wikipedia.org/wiki/Receiver_operating_characteristic
"""
