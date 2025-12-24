# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Utility for downloading model weights from Hugging Face Hub.

This module provides functionality to automatically download the Nemotron OCR
model weights from the Hugging Face repository if they are not present locally.
"""

from pathlib import Path
from typing import Optional

from huggingface_hub import hf_hub_download, snapshot_download

# Hugging Face repository for Nemotron OCR weights
HF_REPO_ID = "nvidia/nemotron-ocr-v1"

# List of required checkpoint files
CHECKPOINT_FILES = [
    "checkpoints/detector.pth",
    "checkpoints/recognizer.pth",
    "checkpoints/relational.pth",
    "checkpoints/charset.txt",
]


def get_default_cache_dir() -> Path:
    """
    Get the default cache directory for storing downloaded weights.
    
    Uses the standard HuggingFace cache location.
    
    Returns:
        Path to the cache directory.
    """
    from huggingface_hub import constants
    return Path(constants.HF_HUB_CACHE)


def ensure_weights_available(
    model_dir: Optional[Path] = None,
    repo_id: str = HF_REPO_ID,
    force_download: bool = False,
    token: Optional[str] = None,
) -> Path:
    """
    Ensure model weights are available, downloading them if necessary.
    
    This function checks if the required checkpoint files exist in the specified
    model directory. If any files are missing, it downloads them from the
    Hugging Face Hub.
    
    Args:
        model_dir: Path to the directory containing model weights.
                   If None, uses the HuggingFace cache directory.
        repo_id: Hugging Face repository ID.
        force_download: If True, re-download even if files exist.
        token: Hugging Face authentication token (optional, for private repos).
    
    Returns:
        Path to the directory containing the model checkpoints.
    
    Raises:
        RuntimeError: If download fails.
    """
    # If model_dir is provided and all files exist, use it directly
    if model_dir is not None and not force_download:
        model_path = Path(model_dir)
        if _all_checkpoints_present(model_path):
            return model_path
    
    # Download to HuggingFace cache if no local path provided or files missing
    try:
        # Download only the checkpoints folder from the repo
        cache_dir = snapshot_download(
            repo_id=repo_id,
            allow_patterns=["checkpoints/*"],
            force_download=force_download,
            token=token,
        )
        checkpoint_dir = Path(cache_dir) / "checkpoints"
        
        if not _all_checkpoints_present_flat(checkpoint_dir):
            raise RuntimeError(
                f"Downloaded weights are incomplete. Expected files in {checkpoint_dir}"
            )
        
        return checkpoint_dir
        
    except Exception as e:
        raise RuntimeError(
            f"Failed to download model weights from {repo_id}. "
            f"Please ensure you have internet access and the repository exists. "
            f"Error: {e}"
        ) from e


def _all_checkpoints_present(base_path: Path) -> bool:
    """Check if all required checkpoint files are present in the given directory."""
    required_files = ["detector.pth", "recognizer.pth", "relational.pth", "charset.txt"]
    return all((base_path / f).is_file() for f in required_files)


def _all_checkpoints_present_flat(checkpoint_dir: Path) -> bool:
    """Check if all required checkpoint files are present in a flat directory."""
    required_files = ["detector.pth", "recognizer.pth", "relational.pth", "charset.txt"]
    return all((checkpoint_dir / f).is_file() for f in required_files)


def download_weights(
    output_dir: Optional[Path] = None,
    repo_id: str = HF_REPO_ID,
    force_download: bool = False,
    token: Optional[str] = None,
) -> Path:
    """
    Explicitly download model weights to a specified directory.
    
    This is a convenience function for users who want to pre-download
    weights to a specific location.
    
    Args:
        output_dir: Directory to save the weights. If None, uses HuggingFace cache.
        repo_id: Hugging Face repository ID.
        force_download: If True, re-download even if files exist.
        token: Hugging Face authentication token (optional).
    
    Returns:
        Path to the directory containing the downloaded checkpoints.
    
    Example:
        >>> from nemotron_ocr.inference.weight_downloader import download_weights
        >>> checkpoint_dir = download_weights(output_dir=Path("./my_checkpoints"))
        >>> # Use checkpoint_dir with NemotronOCR
        >>> from nemotron_ocr.inference.pipeline import NemotronOCR
        >>> ocr = NemotronOCR(model_dir=checkpoint_dir)
    """
    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Download individual files to the output directory
        required_files = ["detector.pth", "recognizer.pth", "relational.pth", "charset.txt"]
        for filename in required_files:
            hf_hub_download(
                repo_id=repo_id,
                filename=f"checkpoints/{filename}",
                local_dir=output_path.parent,
                force_download=force_download,
                token=token,
            )
        
        # The files are downloaded to output_path.parent/checkpoints/
        checkpoint_dir = output_path.parent / "checkpoints"
        if output_path != checkpoint_dir:
            # If user specified a different path, we downloaded to parent/checkpoints
            # Return the actual location
            return checkpoint_dir
        return output_path
    else:
        return ensure_weights_available(
            model_dir=None,
            repo_id=repo_id,
            force_download=force_download,
            token=token,
        )

