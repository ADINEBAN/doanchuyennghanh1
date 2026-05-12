"""Dataset preprocessing entry point."""

from __future__ import annotations

from pathlib import Path


def preprocess_dataset(input_dir: str, output_dir: str) -> None:
    source = Path(input_dir)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    print(f"Preprocess dataset from {source} to {target}.")
    print("TODO: add resize, split, and augmentation preparation.")


if __name__ == "__main__":
    preprocess_dataset("ml/datasets/raw", "ml/datasets/processed")
