# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import torch
import torch.nn as nn
from typing import List, Tuple, Optional

from .weights import get_weights_path


class Exp:
    """
    Configuration class for the graphic element model.

    This class contains all configuration parameters for the YOLOX-based
    graphic element detection model, including architecture settings, inference
    parameters, and class-specific thresholds.
    """

    def __init__(
        self,
        weights_cache_dir: Optional[str] = None,
        force_download: bool = False,
        hf_token: Optional[str] = None,
    ) -> None:
        """
        Initialize the configuration with default parameters.

        Args:
            weights_cache_dir: Directory to cache downloaded weights.
                Defaults to ~/.cache/nemotron_graphic_elements_v1
            force_download: If True, re-download weights even if cached.
            hf_token: Hugging Face token for accessing gated models (if needed).
        """
        self.name: str = "graphic-element-v1"
        # Get weights path (downloads from HuggingFace if needed)
        self.ckpt: str = get_weights_path(
            cache_dir=weights_cache_dir,
            force_download=force_download,
            token=hf_token,
        )
        self.device: str = "cuda:0" if torch.cuda.is_available() else "cpu"

        # YOLOX architecture parameters
        self.act: str = "silu"
        self.depth: float = 1.00
        self.width: float = 1.00
        self.labels: List[str] = [
            "chart_title",
            "x_title",
            "y_title",
            "xlabel",
            "ylabel",
            "other",
            "legend_label",
            "legend_title",
            "mark_label",
            "value_label",
        ]
        self.num_classes: int = len(self.labels)

        # Inference parameters
        self.size: Tuple[int, int] = (1024, 1024)
        self.min_bbox_size: int = 0
        self.normalize_boxes: bool = True

        # NMS & thresholding. These can be updated
        self.conf_thresh: float = 0.01
        self.iou_thresh: float = 0.25
        self.class_agnostic: bool = True  # False

        self.threshold: float = 0.1

    def get_model(self) -> nn.Module:
        """
        Get the YOLOX model.

        Builds and returns a YOLOX model with the configured architecture.
        Also updates batch normalization parameters for optimal inference.

        Returns:
            nn.Module: The YOLOX model with configured parameters.
        """
        from .yolox import YOLOX, YOLOPAFPN, YOLOXHead

        # Build model
        if getattr(self, "model", None) is None:
            in_channels = [256, 512, 1024]
            backbone = YOLOPAFPN(
                self.depth, self.width, in_channels=in_channels, act=self.act
            )
            head = YOLOXHead(
                self.num_classes, self.width, in_channels=in_channels, act=self.act
            )
            self.model = YOLOX(backbone, head)

        # Update batch-norm parameters
        def init_yolo(M: nn.Module) -> None:
            for m in M.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.eps = 1e-3
                    m.momentum = 0.03

        self.model.apply(init_yolo)

        return self.model
