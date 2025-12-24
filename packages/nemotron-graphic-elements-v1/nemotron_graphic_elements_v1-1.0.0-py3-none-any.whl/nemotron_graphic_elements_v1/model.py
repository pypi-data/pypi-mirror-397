# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import torch
import importlib
import numpy as np
import numpy.typing as npt
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Union
from .yolox.boxes import postprocess


def define_model(
    config_name: str = "graphic_element_v1",
    verbose: bool = True,
    weights_cache_dir: str = None,
    force_download: bool = False,
    hf_token: str = None,
) -> nn.Module:
    """
    Defines and initializes the model based on the configuration.

    Args:
        config_name (str): Configuration name. Defaults to "graphic_element_v1".
        verbose (bool): Whether to print verbose output. Defaults to True.
        weights_cache_dir (str): Directory to cache downloaded weights.
            Defaults to ~/.cache/nemotron_graphic_elements_v1
        force_download (bool): If True, re-download weights even if cached.
        hf_token (str): Hugging Face token for accessing gated models (if needed).

    Returns:
        torch.nn.Module: The initialized YOLOX model.
    """
    # Import the config class
    from .graphic_element_v1 import Exp
    
    config = Exp(
        weights_cache_dir=weights_cache_dir,
        force_download=force_download,
        hf_token=hf_token,
    )
    model = config.get_model()

    # Load weights
    if verbose:
        print(" -> Loading weights from", config.ckpt)

    ckpt = torch.load(config.ckpt, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model"], strict=True)

    model = YoloXWrapper(model, config)
    return model.eval().to(config.device)


def resize_pad(img: torch.Tensor, size: tuple) -> torch.Tensor:
    """
    Resizes and pads an image to a given size.
    The goal is to preserve the aspect ratio of the image.

    Args:
        img (torch.Tensor[C x H x W]): The image to resize and pad.
        size (tuple[2]): The size to resize and pad the image to.

    Returns:
        torch.Tensor: The resized and padded image.
    """
    img = img.float()
    _, h, w = img.shape
    scale = min(size[0] / h, size[1] / w)
    nh = int(h * scale)
    nw = int(w * scale)
    img = F.interpolate(
        img.unsqueeze(0), size=(nh, nw), mode="bilinear", align_corners=False
    ).squeeze(0)
    img = torch.clamp(img, 0, 255)
    pad_b = size[0] - nh
    pad_r = size[1] - nw
    img = F.pad(img, (0, pad_r, 0, pad_b), value=114.0)
    return img


class YoloXWrapper(nn.Module):
    """
    Wrapper for YoloX models.
    """
    def __init__(self, model: nn.Module, config) -> None:
        """
        Constructor

        Args:
            model (torch model): Yolo model.
            config (Config): Config object containing model parameters.
        """
        super().__init__()
        self.model = model
        self.config = config

        # Copy config parameters
        self.device = config.device
        self.img_size = config.size
        self.min_bbox_size = config.min_bbox_size
        self.normalize_boxes = config.normalize_boxes
        self.conf_thresh = config.conf_thresh
        self.iou_thresh = config.iou_thresh
        self.class_agnostic = config.class_agnostic
        self.threshold = config.threshold
        self.labels = config.labels
        self.num_classes = config.num_classes

    def reformat_input(
        self,
        x: torch.Tensor,
        orig_sizes: Union[torch.Tensor, List, Tuple, npt.NDArray]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Reformats the input data and original sizes to the correct format.

        Args:
            x (torch.Tensor[BS x C x H x W]): Input image batch.
            orig_sizes (torch.Tensor or list or np.ndarray): Original image sizes.
        Returns:
            torch tensor [BS x C x H x W]: Input image batch.
            torch tensor [BS x 2]: Original image sizes (before resizing and padding).
        """
        # Convert image size to tensor
        if isinstance(orig_sizes, (list, tuple)):
            orig_sizes = np.array(orig_sizes)
        if orig_sizes.shape[-1] == 3:  # remove channel
            orig_sizes = orig_sizes[..., :2]
        if isinstance(orig_sizes, np.ndarray):
            orig_sizes = torch.from_numpy(orig_sizes).to(self.device)

        # Add batch dimension if not present
        if len(x.size()) == 3:
            x = x.unsqueeze(0)
        if len(orig_sizes.size()) == 1:
            orig_sizes = orig_sizes.unsqueeze(0)

        return x, orig_sizes

    def preprocess(self, image: Union[torch.Tensor, npt.NDArray]) -> torch.Tensor:
        """
        YoloX preprocessing function:
        - Resizes to the longest edge to img_size while preserving the aspect ratio
        - Pads the shortest edge to img_size

        Args:
            image (torch tensor or np array [H x W x 3]): Input images in uint8 format.

        Returns:
            torch tensor [3 x H x W]: Processed image.
        """
        if not isinstance(image, torch.Tensor):
            image = torch.from_numpy(image)
        image = image.to(self.device)
        image = image.permute(2, 0, 1)  # [H, W, 3] -> [3, H, W]
        image = resize_pad(image, self.img_size)
        return image.float()

    def forward(
        self,
        x: torch.Tensor,
        orig_sizes: Union[torch.Tensor, List, Tuple, npt.NDArray]
    ) -> List[Dict[str, torch.Tensor]]:
        """
        Forward pass of the model.
        Applies NMS and reformats the predictions.

        Args:
            x (torch.Tensor[BS x C x H x W]): Input image batch.
            orig_sizes (torch.Tensor or list or np.ndarray): Original image sizes.

        Returns:
            list[dict]: List of prediction dictionaries. Each dictionary contains:
                - labels (torch.Tensor[N]): Class labels
                - boxes (torch.Tensor[N x 4]): Bounding boxes
                - scores (torch.Tensor[N]): Confidence scores.
        """
        x, orig_sizes = self.reformat_input(x, orig_sizes)

        # Scale to 0-255 if in range 0-1
        if x.max() <= 1:
            x *= 255

        pred_boxes = self.model(x.to(self.device))

        # NMS
        pred_boxes = postprocess(
            pred_boxes,
            self.config.num_classes,
            self.conf_thresh,
            self.iou_thresh,
            class_agnostic=self.class_agnostic,
        )

        # Reformat output
        preds = []
        for i, (p, size) in enumerate(zip(pred_boxes, orig_sizes)):
            if p is None:  # No detections
                preds.append({
                    "labels": torch.empty(0),
                    "boxes": torch.empty((0, 4)),
                    "scores": torch.empty(0),
                })
                continue

            p = p.view(-1, p.size(-1))
            ratio = min(self.img_size[0] / size[0], self.img_size[1] / size[1])
            boxes = p[:, :4] / ratio

            # Clip
            boxes[:, [0, 2]] = torch.clamp(boxes[:, [0, 2]], 0, size[1])
            boxes[:, [1, 3]] = torch.clamp(boxes[:, [1, 3]], 0, size[0])

            # Remove too small
            kept = (
                (boxes[:, 2] - boxes[:, 0] > self.min_bbox_size) &
                (boxes[:, 3] - boxes[:, 1] > self.min_bbox_size)
            )
            boxes = boxes[kept]
            p = p[kept]

            # Normalize to 0-1
            if self.normalize_boxes:
                boxes[:, [0, 2]] /= size[1]
                boxes[:, [1, 3]] /= size[0]

            scores = p[:, 4] * p[:, 5]
            labels = p[:, 6]

            preds.append({"labels": labels, "boxes": boxes, "scores": scores})

        return preds
