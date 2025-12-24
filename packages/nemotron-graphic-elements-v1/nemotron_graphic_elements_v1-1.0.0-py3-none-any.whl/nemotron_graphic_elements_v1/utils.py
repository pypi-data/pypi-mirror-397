# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pandas as pd
import numpy.typing as npt
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import Dict, List, Tuple, Optional, Union


COLORS = [
    "#003EFF",
    "#FF8F00",
    "#079700",
    "#A123FF",
    "#87CEEB",
    "#FF5733",
    "#C70039",
    "#900C3F",
    "#581845",
    "#11998E",
]


def reformat_for_plotting(
    boxes: npt.NDArray[np.float64],
    labels: npt.NDArray[np.int_],
    scores: npt.NDArray[np.float64],
    shape: Tuple[int, int, int],
    num_classes: int,
) -> Tuple[List[npt.NDArray[np.int_]], List[npt.NDArray[np.float64]]]:
    """
    Reformat YOLOX predictions for plotting.
    - Unnormalizes boxes to original image size.
    - Reformats boxes to [xmin, ymin, width, height].
    - Converts to list of boxes and scores per class.

    Args:
        boxes (np.ndarray [N, 4]): Array of bounding boxes in format [xmin, ymin, xmax, ymax].
        labels (np.ndarray [N]): Array of labels.
        scores (np.ndarray [N]): Array of confidence scores.
        shape (tuple [2]): Shape of the image (height, width).
        num_classes (int): Number of classes.

    Returns:
        list[np.ndarray[N]]: List of box bounding boxes per class.
        list[np.ndarray[N]]: List of confidence scores per class.
    """
    boxes_plot = boxes.copy()
    boxes_plot[:, [0, 2]] *= shape[1]
    boxes_plot[:, [1, 3]] *= shape[0]
    boxes_plot = boxes_plot.astype(int)
    boxes_plot[:, 2] -= boxes_plot[:, 0]
    boxes_plot[:, 3] -= boxes_plot[:, 1]
    boxes_plot = [boxes_plot[labels == c] for c in range(num_classes)]
    confs = [scores[labels == c] for c in range(num_classes)]
    return boxes_plot, confs


def plot_sample(
    img: npt.NDArray[np.uint8],
    boxes_list: List[npt.NDArray[np.int_]],
    confs_list: List[npt.NDArray[np.float64]],
    labels: List[str],
    show_text: bool = True,
) -> None:
    """
    Plots an image with bounding boxes.
    Coordinates are expected in format [x_min, y_min, width, height].

    Args:
        img (numpy.ndarray): The input image to be plotted.
        boxes_list (list[np.ndarray]): List of box bounding boxes per class.
        confs_list (list[np.ndarray]): List of confidence scores per class.
        labels (list): List of class labels.
        show_text (bool, optional): Whether to show the text. Defaults to True.
    """
    plt.imshow(img, cmap="gray")
    plt.axis(False)

    for boxes, confs, col, l in zip(boxes_list, confs_list, COLORS, labels):
        for box_idx, box in enumerate(boxes):
            # Better display around boundaries
            h, w, _ = img.shape
            box = np.copy(box)
            box[:2] = np.clip(box[:2], 2, max(h, w))
            box[2] = min(box[2], w - 2 - box[0])
            box[3] = min(box[3], h - 2 - box[1])

            rect = Rectangle(
                (box[0], box[1]),
                box[2],
                box[3],
                linewidth=2,
                facecolor="none",
                edgecolor=col,
            )
            plt.gca().add_patch(rect)

            # Add class and index label with proper alignment
            if show_text:
                plt.text(
                    box[0], box[1],
                    f"{l}_{box_idx}   conf={confs[box_idx]:.3f}",
                    color='white',
                    fontsize=8,
                    bbox=dict(facecolor=col, alpha=1, edgecolor=col, pad=0, linewidth=2),
                    verticalalignment='bottom',
                    horizontalalignment='left'
                )


def reorder_boxes(
    boxes: npt.NDArray[np.float64],
    labels: npt.NDArray[np.int_],
    classes: Optional[List[str]] = None,
    scores: Optional[npt.NDArray[np.float64]] = None,
) -> Union[
    Tuple[npt.NDArray[np.float64], npt.NDArray[np.int_]],
    Tuple[npt.NDArray[np.float64], npt.NDArray[np.int_], npt.NDArray[np.float64]],
]:
    """
    Reorder boxes, labels and scores by box coordinates.
    Ordering depends on the class.

    Args:
        boxes (np.ndarray [N, 4]): Array of bounding boxes in format [xmin, ymin, xmax, ymax].
        labels (np.ndarray [N]): Array of labels.
        classes (list, optional): List of class labels. Defaults to None.
        scores (np.ndarray [N], optional): Array of confidence scores. Defaults to None.

    Returns:
        np.ndarray [N, 4]: Ordered boxes in format [xmin, ymin, xmax, ymax].
        np.ndarray [N]: Ordered labels.
        np.ndarray [N]: Ordered scores if scores is not None.
    """
    n_classes = labels.max() if classes is None else len(classes)
    classes = labels.unique() if classes is None else classes

    ordered_boxes, ordered_labels, ordered_scores = [], [], []
    for c in range(n_classes):
        boxes_class = boxes[labels == c]
        if len(boxes_class):
            # Reorder
            sort = ["y0", "x0"]
            ascending = [True, True]
            if classes[c] == "ylabel":
                ascending = [False, True]
            elif classes[c] == "y_title":
                sort = ["x0", "y0"]
                ascending = [True, False]

            df_coords = pd.DataFrame({
                "y0": np.round(boxes_class[:, 1] - boxes_class[:, 1].min(), 2),
                "x0": np.round(boxes_class[:, 0] - boxes_class[:, 0].min(), 2),
            })

            idxs = df_coords.sort_values(sort, ascending=ascending).index

            ordered_boxes.append(boxes_class[idxs])
            ordered_labels.append(labels[labels == c][idxs])

            if scores is not None:
                ordered_scores.append(scores[labels == c][idxs])

    ordered_boxes = np.concatenate(ordered_boxes)
    ordered_labels = np.concatenate(ordered_labels)
    if scores is not None:
        ordered_scores = np.concatenate(ordered_scores)
        return ordered_boxes, ordered_labels, ordered_scores
    return ordered_boxes, ordered_labels


def postprocess_preds_graphic_element(
    preds: Dict[str, npt.NDArray],
    threshold: float = 0.1,
    class_labels: Optional[List[str]] = None,
    reorder: bool = True,
) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.int_], npt.NDArray[np.float64]]:
    """
    Post process predictions for the page element task.
    - Applies thresholding
    - Reorders boxes using the reading order

    Args:
        preds (dict): Predictions. Keys are "scores", "boxes", "labels".
        threshold (float, optional): Threshold for the confidence scores. Defaults to 0.1.
        class_labels (list, optional): List of class labels. Defaults to None.
        reorder (bool, optional): Whether to apply reordering. Defaults to True.

    Returns:
        numpy.ndarray [N x 4]: Array of bounding boxes.
        numpy.ndarray [N]: Array of labels.
        numpy.ndarray [N]: Array of scores.
    """
    boxes = preds["boxes"].cpu().numpy()
    labels = preds["labels"].cpu().numpy()
    scores = preds["scores"].cpu().numpy()

    # Threshold
    boxes = boxes[scores > threshold]
    labels = labels[scores > threshold]
    scores = scores[scores > threshold]

    if len(boxes) > 0 and reorder:
        boxes, labels, scores = reorder_boxes(boxes, labels, class_labels, scores)

    return boxes, labels, scores
