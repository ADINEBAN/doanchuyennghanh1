"""Runtime predictor wrapper with real inference pipeline."""

from __future__ import annotations

import logging
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

from app.ai.labels import DEFAULT_LABELS
from app.ai.model_loader import load_model

LOGGER = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    label: str
    confidence: float


class DrowsinessPredictor:
    """Wraps a loaded model and provides a ``predict`` method that accepts
    an RGB image region (e.g. cropped face or eye region) and returns a
    classification result.
    """

    def __init__(
        self,
        model_path: Union[str, Path],
        labels: Optional[list[str]] = None,
        input_size: tuple[int, int] = (160, 160),
    ) -> None:
        resolved_model_path = Path(model_path)
        self.model_path = str(resolved_model_path)
        self.labels = labels or self._load_labels(resolved_model_path)
        self.input_size = input_size
        self.model: Any = load_model(model_path)
        self._is_onnx = self.model is not None and hasattr(self.model, "run")

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, image: np.ndarray) -> PredictionResult:
        """Predict the drowsiness state from a face/eye crop.

        Args:
            image: An RGB numpy array (any size; will be resized internally).

        Returns:
            PredictionResult with label and confidence.
        """
        if self.model is None:
            return PredictionResult(label="normal", confidence=0.0)

        try:
            preprocessed = self._preprocess(image)

            if self._is_onnx:
                return self._predict_onnx(preprocessed)
            else:
                return self._predict_keras(preprocessed)
        except Exception as exc:
            LOGGER.warning("Prediction failed: %s", exc)
            return PredictionResult(label="normal", confidence=0.0)

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Resize, normalize, and batch the image."""
        import cv2

        resized = cv2.resize(image, self.input_size)
        normalized = resized.astype(np.float32) / 255.0
        # Add batch dimension: (1, H, W, C)
        return np.expand_dims(normalized, axis=0)

    def _predict_keras(self, batch: np.ndarray) -> PredictionResult:
        predictions = self.model.predict(batch, verbose=0)
        idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][idx])
        label = self.labels[idx] if idx < len(self.labels) else "unknown"
        return PredictionResult(label=label, confidence=confidence)

    def _predict_onnx(self, batch: np.ndarray) -> PredictionResult:
        input_name = self.model.get_inputs()[0].name
        outputs = self.model.run(None, {input_name: batch})
        predictions = outputs[0]
        idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][idx])
        label = self.labels[idx] if idx < len(self.labels) else "unknown"
        return PredictionResult(label=label, confidence=confidence)

    @staticmethod
    def _load_labels(model_path: Path) -> list[str]:
        labels_path = model_path.with_name("labels.json")
        if labels_path.exists():
            try:
                labels = json.loads(labels_path.read_text(encoding="utf-8"))
                if isinstance(labels, list) and all(isinstance(item, str) for item in labels):
                    return labels
            except Exception as exc:
                LOGGER.warning("Failed to load labels from %s: %s", labels_path, exc)
        return list(DEFAULT_LABELS)
