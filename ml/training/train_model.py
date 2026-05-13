"""Train a lightweight drowsiness image classifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def train(
    dataset_dir: str = "ml/datasets/processed",
    output_dir: str = "ml/exported_models",
    *,
    image_size: int = 160,
    batch_size: int = 32,
    epochs: int = 15,
    fine_tune_epochs: int = 5,
    learning_rate: float = 1e-3,
) -> Path:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    dataset_path = Path(dataset_dir)
    train_dir = dataset_path / "train"
    val_dir = dataset_path / "val"
    if not train_dir.exists() or not val_dir.exists():
        raise FileNotFoundError(
            "Processed dataset must contain train/ and val/. "
            "Run preprocess_dataset.py first."
        )

    train_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        label_mode="categorical",
    )
    val_ds = keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=False,
    )
    class_names = train_ds.class_names
    num_classes = len(class_names)

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)

    augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.06),
            layers.RandomZoom(0.08),
            layers.RandomContrast(0.12),
        ],
        name="augmentation",
    )

    base_model = keras.applications.MobileNetV3Small(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = keras.Input(shape=(image_size, image_size, 3))
    x = augmentation(inputs)
    x = keras.applications.mobilenet_v3.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = keras.Model(inputs, outputs)

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy", keras.metrics.Precision(name="precision"), keras.metrics.Recall(name="recall")],
    )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    callbacks = [
        keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(
            output_path / "drowsiness_model.keras",
            save_best_only=True,
            monitor="val_accuracy",
        ),
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=callbacks)

    if fine_tune_epochs > 0:
        base_model.trainable = True
        for layer in base_model.layers[:-25]:
            layer.trainable = False
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate / 10),
            loss="categorical_crossentropy",
            metrics=["accuracy", keras.metrics.Precision(name="precision"), keras.metrics.Recall(name="recall")],
        )
        fine_history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=fine_tune_epochs,
            callbacks=callbacks,
        )
        for key, values in fine_history.history.items():
            history.history.setdefault(key, []).extend(values)

    final_model_path = output_path / "drowsiness_model.keras"
    model.save(final_model_path)
    (output_path / "labels.json").write_text(
        json.dumps(class_names, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "training_history.json").write_text(
        json.dumps(history.history, indent=2),
        encoding="utf-8",
    )
    print(f"Saved model: {final_model_path}")
    print(f"Labels: {class_names}")
    return final_model_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train drowsiness image classifier.")
    parser.add_argument("--dataset", default="ml/datasets/processed")
    parser.add_argument("--output", default="ml/exported_models")
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--fine-tune-epochs", type=int, default=5)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(
        args.dataset,
        args.output,
        image_size=args.image_size,
        batch_size=args.batch_size,
        epochs=args.epochs,
        fine_tune_epochs=args.fine_tune_epochs,
        learning_rate=args.learning_rate,
    )
