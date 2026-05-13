"""Evaluate an exported drowsiness classifier on the test split."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def evaluate(
    model_path: str = "ml/exported_models/drowsiness_model.keras",
    dataset_dir: str = "ml/datasets/processed/test",
    output_dir: str = "ml/exported_models",
    *,
    image_size: int = 160,
    batch_size: int = 32,
) -> dict[str, float]:
    import tensorflow as tf
    from tensorflow import keras

    model_file = Path(model_path)
    test_dir = Path(dataset_dir)
    if not model_file.exists():
        raise FileNotFoundError(f"Model not found: {model_file}")
    if not test_dir.exists():
        raise FileNotFoundError(f"Test dataset not found: {test_dir}")

    model = keras.models.load_model(model_file)
    test_ds = keras.utils.image_dataset_from_directory(
        test_dir,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=False,
    )
    class_names = test_ds.class_names

    probabilities = model.predict(test_ds, verbose=1)
    predicted = np.argmax(probabilities, axis=1)
    actual = np.concatenate([np.argmax(labels.numpy(), axis=1) for _, labels in test_ds])

    confusion = tf.math.confusion_matrix(
        actual,
        predicted,
        num_classes=len(class_names),
    ).numpy()
    accuracy = float(np.mean(predicted == actual))

    metrics: dict[str, float] = {"accuracy": accuracy}
    for index, class_name in enumerate(class_names):
        true_positive = float(confusion[index, index])
        false_positive = float(confusion[:, index].sum() - true_positive)
        false_negative = float(confusion[index, :].sum() - true_positive)
        precision = true_positive / max(true_positive + false_positive, 1.0)
        recall = true_positive / max(true_positive + false_negative, 1.0)
        f1_score = 2 * precision * recall / max(precision + recall, 1e-9)
        metrics[f"{class_name}_precision"] = precision
        metrics[f"{class_name}_recall"] = recall
        metrics[f"{class_name}_f1"] = f1_score

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "evaluation_metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )
    with (target / "confusion_matrix.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["actual/predicted", *class_names])
        for class_name, row in zip(class_names, confusion):
            writer.writerow([class_name, *row.tolist()])

    print(json.dumps(metrics, indent=2))
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate drowsiness image classifier.")
    parser.add_argument("--model", default="ml/exported_models/drowsiness_model.keras")
    parser.add_argument("--dataset", default="ml/datasets/processed/test")
    parser.add_argument("--output", default="ml/exported_models")
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evaluate(
        args.model,
        args.dataset,
        args.output,
        image_size=args.image_size,
        batch_size=args.batch_size,
    )
