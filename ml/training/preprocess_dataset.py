"""Prepare an image dataset for model training.

Expected raw layout:

    ml/datasets/raw/
      normal/
      closed_eyes/
      yawning/
      drowsy/

The script copies images into train/val/test class folders. Keep the split
stable with --seed so evaluation remains comparable between runs.
"""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _iter_images(class_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in class_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def _copy_split(files: list[Path], class_name: str, output_dir: Path, split: str) -> None:
    target_dir = output_dir / split / class_name
    target_dir.mkdir(parents=True, exist_ok=True)

    for index, source in enumerate(files):
        target = target_dir / f"{source.stem}_{index:05d}{source.suffix.lower()}"
        shutil.copy2(source, target)


def preprocess_dataset(
    input_dir: str,
    output_dir: str,
    *,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> None:
    source = Path(input_dir)
    target = Path(output_dir)

    if not source.exists():
        raise FileNotFoundError(f"Raw dataset directory not found: {source}")
    if val_ratio < 0 or test_ratio < 0 or val_ratio + test_ratio >= 1:
        raise ValueError("val_ratio + test_ratio must be less than 1")

    class_dirs = [path for path in sorted(source.iterdir()) if path.is_dir()]
    if not class_dirs:
        raise ValueError(f"No class folders found in {source}")

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    for class_dir in class_dirs:
        files = _iter_images(class_dir)
        if not files:
            continue

        rng.shuffle(files)
        total = len(files)
        test_count = int(total * test_ratio)
        val_count = int(total * val_ratio)

        test_files = files[:test_count]
        val_files = files[test_count:test_count + val_count]
        train_files = files[test_count + val_count:]

        _copy_split(train_files, class_dir.name, target, "train")
        _copy_split(val_files, class_dir.name, target, "val")
        _copy_split(test_files, class_dir.name, target, "test")

        print(
            f"{class_dir.name}: train={len(train_files)} "
            f"val={len(val_files)} test={len(test_files)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split raw class folders for training.")
    parser.add_argument("--input", default="ml/datasets/raw")
    parser.add_argument("--output", default="ml/datasets/processed")
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    preprocess_dataset(
        args.input,
        args.output,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )
