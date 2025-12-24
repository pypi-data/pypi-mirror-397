# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Nemotron Table Structure v1

A specialized object detection model for table structure extraction based on YOLOX.
"""

__version__ = "1.0.0"

from .model import define_model, YoloXWrapper, get_weights_path
from .utils import (
    plot_sample,
    postprocess_preds_table_structure,
    reformat_for_plotting,
    reorder_boxes,
)

__all__ = [
    "define_model",
    "get_weights_path",
    "YoloXWrapper",
    "plot_sample",
    "postprocess_preds_table_structure",
    "reformat_for_plotting",
    "reorder_boxes",
]



