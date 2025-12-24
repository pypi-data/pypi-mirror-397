# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import numpy.typing as npt
from typing import Tuple, List


def bb_iou_array(
    boxes: npt.NDArray[np.float64], new_box: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """
    Calculates the Intersection over Union (IoU) between a box and an array of boxes.

    Args:
        boxes (numpy.ndarray): Array of bounding boxes with shape (N, 4).
        new_box (numpy.ndarray): A single bounding box [x_min, y_min, x_max, y_max].

    Returns:
        numpy.ndarray: Array of IoU values between the new_box and each box in the array.
    """
    # bb interesection over union
    xA = np.maximum(boxes[:, 0], new_box[0])
    yA = np.maximum(boxes[:, 1], new_box[1])
    xB = np.minimum(boxes[:, 2], new_box[2])
    yB = np.minimum(boxes[:, 3], new_box[3])

    interArea = np.maximum(xB - xA, 0) * np.maximum(yB - yA, 0)

    # compute the area of both the prediction and ground-truth rectangles
    boxAArea = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    boxBArea = (new_box[2] - new_box[0]) * (new_box[3] - new_box[1])

    iou = interArea / (boxAArea + boxBArea - interArea)

    return iou


def expand_boxes(
    boxes: npt.NDArray[np.float64],
    r_x: Tuple[float, float] = (1, 1),
    r_y: Tuple[float, float] = (1, 1),
    size_agnostic: bool = True,
) -> npt.NDArray[np.float64]:
    """
    Expands bounding boxes by a specified ratio.
    Expected box format is normalized [x_min, y_min, x_max, y_max].

    Args:
        boxes (numpy.ndarray): Array of bounding boxes with shape (N, 4).
        r_x (tuple, optional): Left, right expansion ratios. Defaults to (1, 1) (no expansion).
        r_y (tuple, optional): Up, down expansion ratios. Defaults to (1, 1) (no expansion).
        size_agnostic (bool, optional): Expand independently of the box shape. Defaults to True.

    Returns:
        numpy.ndarray: Adjusted bounding boxes clipped to the [0, 1] range.
    """
    old_boxes = boxes.copy()

    if not size_agnostic:
        h = boxes[:, 3] - boxes[:, 1]
        w = boxes[:, 2] - boxes[:, 0]
    else:
        h, w = 1, 1

    boxes[:, 0] -= w * (r_x[0] - 1)  # left
    boxes[:, 2] += w * (r_x[1] - 1)  # right
    boxes[:, 1] -= h * (r_y[0] - 1)  # up
    boxes[:, 3] += h * (r_y[1] - 1)  # down

    boxes = np.clip(boxes, 0, 1)

    # Enforce non-overlapping boxes
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            iou = bb_iou_array(boxes[i][None], boxes[j])[0]
            old_iou = bb_iou_array(old_boxes[i][None], old_boxes[j])[0]
            # print(iou, old_iou)
            if iou > 0.05 and old_iou < 0.1:
                if boxes[i, 1] < boxes[j, 1]:  # i above j
                    boxes[j, 1] = min(old_boxes[j, 1], boxes[i, 3])
                    if old_iou > 0:
                        boxes[i, 3] = max(old_boxes[i, 3], boxes[j, 1])
                else:
                    boxes[i, 1] = min(old_boxes[i, 1], boxes[j, 3])
                    if old_iou > 0:
                        boxes[j, 3] = max(old_boxes[j, 3], boxes[i, 1])

    return boxes


def retrieve_title(
    boxes: npt.NDArray[np.float64],
    labels: npt.NDArray[np.int_],
    classes: List[str],
) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.int_], npt.NDArray[np.float64]]:
    """
    Retrieves missed captions by using the biggest `other` box.

    If no chart_title is detected, this function finds the largest box
    labeled as 'other' (with width > 0.3) and relabels it as 'chart_title'.

    Args:
        boxes (numpy.ndarray): Array of bounding boxes with shape (N, 4).
        labels (numpy.ndarray): Array of labels with shape (N,).
        classes (list): List of class labels.

    Returns:
        numpy.ndarray [N]: Array of labels.
    """
    if classes.index("chart_title") not in labels:
        widths = boxes[:, 2] - boxes[:, 0]
        scores = widths * (labels == classes.index("other")) * (widths > 0.3)
        replaced = np.argmax(scores) if max(scores) > 0 else None
        if replaced is not None:
            labels[replaced] = classes.index("chart_title")
    return labels
