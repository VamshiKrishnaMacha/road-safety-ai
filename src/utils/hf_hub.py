"""Hugging Face Hub model download utility.

Downloads missing YOLO model checkpoints from a remote Hugging Face Hub
repository at application startup.  Falls back gracefully when the Hub is
unreachable or the repo is not configured.
"""
import os
from pathlib import Path
from typing import List, Optional


def hf_model_repo() -> Optional[str]:
    """Return the HF Hub repo ID where model weights are stored.

    Priority:
        1. ``HF_MODEL_REPO`` environment variable.
        2. The hard-coded default (user must update this before deployment).
    """
    return os.environ.get("HF_MODEL_REPO", "vamshikrishnamacha/road-safety-models") or None


def model_dir() -> Path:
    """Return the project root directory where .pt files are expected."""
    # This file lives in src/utils/ -> project root is two levels up
    return Path(__file__).resolve().parents[2]


def download_models(
    filenames: Optional[List[str]] = None,
    repo_id: Optional[str] = None,
    local_dir: Optional[Path] = None,
) -> List[str]:
    """Download missing model files from Hugging Face Hub.

    Args:
        filenames: List of model filenames to ensure exist locally.
            Defaults to the known model checkpoints.
        repo_id: Hugging Face Hub repository ID.
            Defaults to ``HF_MODEL_REPO`` env var or a placeholder.
        local_dir: Directory to save downloaded files.
            Defaults to the project root.

    Returns:
        List of paths to models that were successfully downloaded.
    """
    if filenames is None:
        from src.config.constants import MODEL_FILES

        filenames = MODEL_FILES

    if repo_id is None:
        repo_id = os.environ.get("HF_MODEL_REPO", "")

    if local_dir is None:
        local_dir = model_dir()

    if not repo_id:
        return []

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        return []

    downloaded: List[str] = []
    for fname in filenames:
        dest = local_dir / fname
        if dest.exists():
            continue
        try:
            fetched = hf_hub_download(
                repo_id=repo_id,
                filename=fname,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
            )
            downloaded.append(fetched)
        except Exception:
            # Graceful fallback — don't crash if the Hub is unreachable
            continue

    return downloaded


def ensure_models() -> None:
    """Convenience entry-point: download all configured models that are missing."""
    download_models()
