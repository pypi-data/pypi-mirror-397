# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Weights management for Nemotron Graphic Elements v1.

This module handles downloading model weights from Hugging Face Hub
when they are not bundled with the package.
"""

import os
from pathlib import Path
from typing import Optional

from huggingface_hub import hf_hub_download


# Hugging Face repository information
HF_REPO_ID = "nvidia/nemotron-graphic-elements-v1"
WEIGHTS_FILENAME = "nemotron_graphic_elements_v1/weights.pth"

# Default cache directory for weights
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "nemotron_graphic_elements_v1"


def get_weights_path(
    cache_dir: Optional[str] = None,
    force_download: bool = False,
    token: Optional[str] = None,
) -> str:
    """
    Get the path to the model weights, downloading if necessary.

    This function first checks if weights exist in the package directory
    (for development or manual installation). If not found, it downloads
    the weights from Hugging Face Hub to the cache directory.

    Args:
        cache_dir: Directory to cache downloaded weights. Defaults to
            ~/.cache/nemotron_graphic_elements_v1
        force_download: If True, re-download even if weights exist in cache.
        token: Hugging Face token for accessing gated models (if needed).

    Returns:
        str: Path to the weights file.

    Raises:
        RuntimeError: If weights cannot be found or downloaded.
    """
    # First, check if weights exist in the package directory (dev mode)
    package_dir = Path(__file__).parent
    local_weights = package_dir / "weights.pth"
    
    if local_weights.exists() and not force_download:
        return str(local_weights)
    
    # Set up cache directory
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR
    else:
        cache_dir = Path(cache_dir)
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_weights = cache_dir / "weights.pth"
    
    # Check if weights are already cached
    if cached_weights.exists() and not force_download:
        return str(cached_weights)
    
    # Download from Hugging Face Hub
    print(f" -> Downloading weights from Hugging Face Hub ({HF_REPO_ID})...")
    
    try:
        downloaded_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=WEIGHTS_FILENAME,
            cache_dir=str(cache_dir),
            force_download=force_download,
            token=token,
            local_dir=str(cache_dir),
            local_dir_use_symlinks=False,
        )
        
        # The file might be downloaded to a subdirectory, move to expected location
        downloaded_path = Path(downloaded_path)
        if downloaded_path != cached_weights:
            # Copy to the expected location if different
            import shutil
            shutil.copy2(downloaded_path, cached_weights)
        
        print(f" -> Weights downloaded to {cached_weights}")
        return str(cached_weights)
        
    except Exception as e:
        raise RuntimeError(
            f"Failed to download weights from Hugging Face Hub.\n"
            f"Repository: {HF_REPO_ID}\n"
            f"Error: {e}\n\n"
            f"Please ensure you have internet access and the huggingface_hub "
            f"package is installed. You can also manually download the weights "
            f"from https://huggingface.co/{HF_REPO_ID} and place them at:\n"
            f"  {cached_weights}"
        ) from e


def clear_cache(cache_dir: Optional[str] = None) -> None:
    """
    Clear the cached weights.

    Args:
        cache_dir: Directory where weights are cached. Defaults to
            ~/.cache/nemotron_graphic_elements_v1
    """
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR
    else:
        cache_dir = Path(cache_dir)
    
    cached_weights = cache_dir / "weights.pth"
    
    if cached_weights.exists():
        cached_weights.unlink()
        print(f" -> Removed cached weights from {cached_weights}")
    else:
        print(f" -> No cached weights found at {cached_weights}")

