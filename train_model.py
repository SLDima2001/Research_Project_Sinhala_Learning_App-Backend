"""
Sinhala Handwriting Recognition - Model Training Script
Uses ImageDataGenerator for memory-efficient batch loading.
"""

import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import json
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
DATASET_TRAIN_PATH = "dataset/train"   # Folder with numbered subfolders
DATASET_VALID_PATH = "dataset/valid"   # Validation folder (use train split if missing)
IMG_HEIGHT = 128
IMG_WIDTH  = 128
BATCH_SIZE = 32
EPOCHS = 30
NUM_CLASSES = 454
# ============================================================

# Explicit numerical folder order: "1", "2", "3" ... "454"
# CRITICAL: Without this, Keras sorts alphabetically (1,10,100...) = wrong mapping!
ORDERED_FOLDERS = [str(i) for i in range(1, NUM_CLASSES + 1)]


def build_model(num_classes, img_height, img_width):
    """Build MobileNetV2 model for Sinhala handwriting recognition."""
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(img_height, img_width, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Fine-tune the top layers of the base model
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer=Adam(learning_rate=0.0005),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def main():
    print("\n" + "=" * 60)
    print("SINHALA HANDWRITING RECOGNITION - MODEL TRAINING")
    print("=" * 60)

    # ---- Data Generators ----
    # Training generator with mild augmentation
    train_datagen = ImageDataGenerator(
        rescale=1.0/255,
        rotation_range=15,
        zoom_range=0.15,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.1,
        fill_mode='nearest',
        validation_split=0.15 if not os.path.isdir(DATASET_VALID_PATH) else 0.0
    )

    # For validation, no augmentation
    valid_datagen = ImageDataGenerator(rescale=1.0/255)

    use_split = not os.path.isdir(DATASET_VALID_PATH)

    print(f"\nLoading training data from: {DATASET_TRAIN_PATH}")
    train_generator = train_datagen.flow_from_directory(
        DATASET_TRAIN_PATH,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        color_mode='rgb',
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=ORDERED_FOLDERS,           # Force numerical order!
        subset='training' if use_split else None,
        shuffle=True
    )

    if use_split:
        print("No 'dataset/valid' found — using 15% of training data for validation.")
        val_generator = train_datagen.flow_from_directory(
            DATASET_TRAIN_PATH,
            target_size=(IMG_HEIGHT, IMG_WIDTH),
            color_mode='rgb',
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            classes=ORDERED_FOLDERS,
            subset='validation',
            shuffle=False
        )
    else:
        print(f"Loading validation data from: {DATASET_VALID_PATH}")
        val_generator = valid_datagen.flow_from_directory(
            DATASET_VALID_PATH,
            target_size=(IMG_HEIGHT, IMG_WIDTH),
            color_mode='rgb',
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            classes=ORDERED_FOLDERS,
            shuffle=False
        )

    print(f"\nTraining batches: {len(train_generator)}")
    print(f"Validation batches: {len(val_generator)}")
    print(f"Classes found: {train_generator.num_classes}")

    # ---- Build Model ----
    print("\n" + "=" * 60)
    print("Building model...")
    print("=" * 60)
    model = build_model(NUM_CLASSES, IMG_HEIGHT, IMG_WIDTH)
    model.summary()

    # ---- Callbacks ----
    os.makedirs('models', exist_ok=True)

    callbacks = [
        ModelCheckpoint(
            'models/sinhala_model.keras',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=8,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-6,
            verbose=1
        )
    ]

    # ---- Train ----
    print("\n" + "=" * 60)
    print(f"Starting training for up to {EPOCHS} epochs...")
    print("=" * 60)

    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1
    )

    # ---- Save Info ----
    info = {
        'num_classes': NUM_CLASSES,
        'img_height': IMG_HEIGHT,
        'img_width': IMG_WIDTH,
        'class_names': ORDERED_FOLDERS,
        'trained_on': datetime.now().isoformat(),
        'final_val_accuracy': float(max(history.history.get('val_accuracy', [0])))
    }
    with open('models/sinhala_model_info.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    history_dict = {k: [float(v) for v in vals] for k, vals in history.history.items()}
    with open('models/sinhala_model_history.json', 'w') as f:
        json.dump(history_dict, f, indent=2)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETED!")
    print(f"Best validation accuracy: {info['final_val_accuracy']*100:.2f}%")
    print("Model saved to: models/sinhala_model.keras")
    print("Now restart your Flask API: python app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
