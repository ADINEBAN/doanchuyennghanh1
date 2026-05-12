"""Helpers for loading exported AI models in multiple formats."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Union

LOGGER = logging.getLogger(__name__)


def load_model(model_path: Union[Path, str]) -> Optional[Any]:
    """Load a model from disk.  Supports .keras, .h5, .onnx, .pt formats.

    Returns ``None`` when the file does not exist or the required library
    is not installed.
    """
    path = Path(model_path)
    if not path.exists():
        LOGGER.warning("Model file not found: %s", path)
        return None

    suffix = path.suffix.lower()

    if suffix in (".keras", ".h5"):
        return _load_keras(path)
    if suffix == ".onnx":
        return _load_onnx(path)
    if suffix == ".pt":
        return _load_pytorch(path)

    LOGGER.warning("Unsupported model format: %s", suffix)
    return None


def _load_keras(path: Path) -> Optional[Any]:
    try:
        from tensorflow import keras
        model = keras.models.load_model(path)
        LOGGER.info("Loaded Keras model from %s", path)
        return model
    except ImportError:
        LOGGER.warning("TensorFlow/Keras not installed; skipping model load.")
        return None
    except Exception as exc:
        LOGGER.error("Failed to load Keras model: %s", exc)
        return None


def _load_onnx(path: Path) -> Optional[Any]:
    try:
        import onnxruntime as ort
        session = ort.InferenceSession(str(path))
        LOGGER.info("Loaded ONNX model from %s", path)
        return session
    except ImportError:
        LOGGER.warning("onnxruntime not installed; skipping model load.")
        return None
    except Exception as exc:
        LOGGER.error("Failed to load ONNX model: %s", exc)
        return None


def _load_pytorch(path: Path) -> Optional[Any]:
    try:
        import torch
        model = torch.load(str(path), map_location="cpu")
        if hasattr(model, "eval"):
            model.eval()
        LOGGER.info("Loaded PyTorch model from %s", path)
        return model
    except ImportError:
        LOGGER.warning("PyTorch not installed; skipping model load.")
        return None
    except Exception as exc:
        LOGGER.error("Failed to load PyTorch model: %s", exc)
        return None
