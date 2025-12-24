# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Nemotron Graphic Elements v1

A specialized object detection system designed to identify and extract key elements 
from charts and graphs. Based on YOLOX architecture.

Model weights are automatically downloaded from Hugging Face Hub on first use.
"""

__version__ = "1.0.0"

from .model import define_model
from .utils import (
    plot_sample,
    postprocess_preds_graphic_element,
    reformat_for_plotting,
    reorder_boxes,
    COLORS,
)
from .graphic_element_v1 import Exp
from .weights import get_weights_path, clear_cache

__all__ = [
    "define_model",
    "Exp",
    "plot_sample",
    "postprocess_preds_graphic_element",
    "reformat_for_plotting",
    "reorder_boxes",
    "COLORS",
    "get_weights_path",
    "clear_cache",
]

