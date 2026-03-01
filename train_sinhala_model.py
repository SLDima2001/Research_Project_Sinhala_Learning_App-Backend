"""
Complete Sinhala Handwriting Recognition Model Training Script
This script trains a CNN model on your Sinhala handwriting dataset
Improved version with better error handling, visualization, and monitoring
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import cv2
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
import json
from datetime import datetime
import matplotlib.pyplot as plt
import sys

class SinhalaModelTrainer:
    def __init__(self, dataset_path, img_height=128, img_width=128):
        """
        Initialize the trainer
        
        Args:
            dataset_path: Path to dataset folder with structure:
                dataset/
                    train/
                        1/
                            image1.png
                            image2.png
                        2/
                            image1.png
                        ...
            img_height: Image height for training
            img_width: Image width for training
        """
        self.dataset_path = Path(dataset_path)
        self.img_height = img_height
        self.img_width = img_width
        self.model = None
        self.class_names = []
        self.history = None
        self.class_to_letter = {}  # Mapping from class index to letter
        
    def load_dataset(self):
        """Load and preprocess the dataset"""
        print("=" * 70)
        print("STEP 1: LOADING DATASET")
        print("=" * 70)
        
        images = []
        labels = []
        
        # Get all subdirectories (each represents a letter class)
        class_folders = sorted([d for d in self.dataset_path.iterdir() if d.is_dir()],
                              key=lambda x: int(x.name) if x.name.isdigit() else x.name)
        
        if not class_folders:
            raise ValueError(f"No class folders found in {self.dataset_path}")
        
        self.class_names = [d.name for d in class_folders]
        
        print(f"\n✓ Found {len(self.class_names)} letter classes")
        print(f"✓ Dataset path: {self.dataset_path.absolute()}")
        
        total_images_found = 0
        
        for class_idx, class_folder in enumerate(class_folders):
            image_files = list(class_folder.glob("*.png")) + \
                         list(class_folder.glob("*.jpg")) + \
                         list(class_folder.glob("*.jpeg"))
            
            if not image_files:
                print(f"  ⚠ Class {class_idx} ({class_folder.name}): No images found")
                continue
            
            print(f"  Loading class {class_idx:3d} ({class_folder.name:3s}): ", end="", flush=True)
            
            loaded_count = 0
            for img_path in image_files:
                try:
                    # Read and preprocess image
                    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                    
                    if img is None:
                        continue
                    
                    # Resize to target size
                    img = cv2.resize(img, (self.img_width, self.img_height))
                    
                    # Invert if background is white (most handwriting is black on white)
                    if np.mean(img) > 127:
                        img = 255 - img
                    
                    # Normalize to [0, 1]
                    img = img.astype('float32') / 255.0
                    
                    images.append(img)
                    labels.append(class_idx)
                    loaded_count += 1
                    total_images_found += 1
                    
                except Exception as e:
                    print(f"\n    Error loading {img_path}: {e}")
                    continue
            
            print(f"{loaded_count:4d} images")
        
        if not images:
            raise ValueError("No images were loaded from the dataset!")
        
        # Convert to numpy arrays
        X = np.array(images)
        y = np.array(labels)
        
        # Add channel dimension (grayscale)
        X = np.expand_dims(X, axis=-1)
        
        print(f"\n{'=' * 70}")
        print(f"✓ Dataset loaded successfully!")
        print(f"  Total images: {len(X)}")
        print(f"  Image shape: {X.shape[1:]}")
        print(f"  Number of classes: {len(self.class_names)}")
        print(f"  Data type: {X.dtype}")
        print(f"  Value range: [{X.min():.3f}, {X.max():.3f}]")
        print(f"{'=' * 70}\n")
        
        return X, y
    
    def augment_data(self, images, labels, augmentation_factor=2):
        """
        Augment the dataset with transformations
        
        Args:
            images: Original images
            labels: Original labels
            augmentation_factor: How many augmented versions per image
        """
        print("=" * 70)
        print("STEP 2: DATA AUGMENTATION")
        print("=" * 70)
        
        augmented_images = []
        augmented_labels = []
        
        total_images = len(images)
        
        for idx, (img, label) in enumerate(zip(images, labels)):
            # Show progress
            if (idx + 1) % max(1, total_images // 10) == 0:
                print(f"  Processing: {idx + 1}/{total_images} ({(idx + 1) / total_images * 100:.1f}%)")
            
            # Add original
            augmented_images.append(img)
            augmented_labels.append(label)
            
            # Create augmented versions
            for _ in range(augmentation_factor):
                aug_img = img.copy()
                
                # Random rotation (-15 to +15 degrees)
                angle = np.random.uniform(-15, 15)
                h, w = aug_img.shape[:2]
                M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
                aug_img = cv2.warpAffine(aug_img, M, (w, h), 
                                        borderMode=cv2.BORDER_CONSTANT, 
                                        borderValue=0)
                
                # Random shift (-10% to +10%)
                shift_x = int(np.random.uniform(-0.1, 0.1) * w)
                shift_y = int(np.random.uniform(-0.1, 0.1) * h)
                M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
                aug_img = cv2.warpAffine(aug_img, M, (w, h),
                                        borderMode=cv2.BORDER_CONSTANT,
                                        borderValue=0)
                
                # Random zoom (0.9 to 1.1)
                scale = np.random.uniform(0.9, 1.1)
                M = cv2.getRotationMatrix2D((w/2, h/2), 0, scale)
                aug_img = cv2.warpAffine(aug_img, M, (w, h),
                                        borderMode=cv2.BORDER_CONSTANT,
                                        borderValue=0)
                
                # Random noise
                noise = np.random.normal(0, 0.02, aug_img.shape)
                aug_img = np.clip(aug_img + noise, 0, 1)
                
                augmented_images.append(aug_img)
                augmented_labels.append(label)
        
        X_aug = np.array(augmented_images)
        y_aug = np.array(augmented_labels)
        
        print(f"\n{'=' * 70}")
        print(f"✓ Data augmentation completed!")
        print(f"  Original dataset size: {len(images)}")
        print(f"  Augmented dataset size: {len(X_aug)}")
        print(f"  Augmentation factor: {len(X_aug) / len(images):.1f}x")
        print(f"{'=' * 70}\n")
        
        return X_aug, y_aug
    
    def build_model(self, num_classes):
        """Build CNN model for Sinhala handwriting recognition"""
        print("=" * 70)
        print("STEP 3: BUILDING MODEL ARCHITECTURE")
        print("=" * 70)
        
        model = keras.Sequential([
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same',
                         input_shape=(self.img_height, self.img_width, 1),
                         name='conv1'),
            layers.BatchNormalization(name='bn1'),
            layers.MaxPooling2D((2, 2), name='pool1'),
            layers.Dropout(0.25, name='dropout1'),
            
            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same', name='conv2'),
            layers.BatchNormalization(name='bn2'),
            layers.MaxPooling2D((2, 2), name='pool2'),
            layers.Dropout(0.25, name='dropout2'),
            
            # Third Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same', name='conv3'),
            layers.BatchNormalization(name='bn3'),
            layers.MaxPooling2D((2, 2), name='pool3'),
            layers.Dropout(0.25, name='dropout3'),
            
            # Fourth Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu', padding='same', name='conv4'),
            layers.BatchNormalization(name='bn4'),
            layers.MaxPooling2D((2, 2), name='pool4'),
            layers.Dropout(0.25, name='dropout4'),
            
            # Flatten and Dense Layers
            layers.Flatten(name='flatten'),
            layers.Dense(512, activation='relu', name='dense1'),
            layers.BatchNormalization(name='bn5'),
            layers.Dropout(0.5, name='dropout5'),
            
            layers.Dense(256, activation='relu', name='dense2'),
            layers.BatchNormalization(name='bn6'),
            layers.Dropout(0.5, name='dropout6'),
            
            # Output Layer
            layers.Dense(num_classes, activation='softmax', name='output')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(f"\n✓ Model architecture created!")
        print(f"\nModel Summary:")
        model.summary()
        
        self.model = model
        return model
    
    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2):
        """Train the model"""
        print("\n" + "=" * 70)
        print("STEP 4: TRAINING MODEL")
        print("=" * 70)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        print(f"\n✓ Data split completed!")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Validation samples: {len(X_val)}")
        print(f"  Training epochs: {epochs}")
        print(f"  Batch size: {batch_size}")
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Callbacks
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                'models/best_model.keras',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1,
                mode='max'
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1,
                min_delta=0.0001
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            ),
            keras.callbacks.TensorBoard(
                log_dir='logs',
                histogram_freq=1,
                write_graph=True,
                update_freq='epoch'
            )
        ]
        
        print(f"\n{'=' * 70}")
        print("Starting training...")
        print(f"{'=' * 70}\n")
        
        # Train
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        print("\n" + "=" * 70)
        print("STEP 5: EVALUATING MODEL")
        print("=" * 70)
        
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        print(f"\n✓ Evaluation completed!")
        print(f"  Test Loss: {test_loss:.4f}")
        print(f"  Test Accuracy: {test_accuracy * 100:.2f}%")
        
        return test_loss, test_accuracy
    
    def plot_training_history(self, save_path='models/training_history.png'):
        """Plot and save training history"""
        if self.history is None:
            print("No training history available")
            return
        
        print(f"\nGenerating training history plots...")
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Training Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss plot
        axes[1].plot(self.history.history['loss'], label='Training Loss')
        axes[1].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"✓ Training history plot saved to: {save_path}")
        plt.close()
    
    def save_model(self, save_path='models/sinhala_model.keras'):
        """Save the trained model"""
        print("\n" + "=" * 70)
        print("STEP 6: SAVING MODEL")
        print("=" * 70)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save Keras model
        self.model.save(save_path)
        print(f"\n✓ Model saved to: {save_path}")
        
        # Save class names
        class_info = {
            'class_names': self.class_names,
            'num_classes': len(self.class_names),
            'img_height': self.img_height,
            'img_width': self.img_width,
            'trained_on': datetime.now().isoformat(),
            'model_architecture': 'CNN with 4 Conv blocks + Dense layers',
            'total_parameters': int(self.model.count_params())
        }
        
        info_path = save_path.replace('.keras', '_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(class_info, f, ensure_ascii=False, indent=2)
        print(f"✓ Model info saved to: {info_path}")
        
        # Save training history
        if self.history:
            history_path = save_path.replace('.keras', '_history.json')
            history_dict = {k: [float(v) for v in vals] 
                          for k, vals in self.history.history.items()}
            with open(history_path, 'w') as f:
                json.dump(history_dict, f, indent=2)
            print(f"✓ Training history saved to: {history_path}")
        
        print(f"\n{'=' * 70}")
        print("✓ Model saved successfully!")
        print(f"{'=' * 70}\n")


def main():
    """Main training pipeline"""
    print("\n" + "=" * 70)
    print("SINHALA HANDWRITING RECOGNITION - MODEL TRAINING")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # Configuration
    DATASET_PATH = "../dataset/train"  # Change this to your dataset path
    IMG_SIZE = 128
    EPOCHS = 100
    BATCH_SIZE = 32
    AUGMENTATION_FACTOR = 2
    VALIDATION_SPLIT = 0.15
    TEST_SPLIT = 0.15
    
    try:
        # Initialize trainer
        trainer = SinhalaModelTrainer(
            dataset_path=DATASET_PATH,
            img_height=IMG_SIZE,
            img_width=IMG_SIZE
        )
        
        # Step 1: Load dataset
        X, y = trainer.load_dataset()
        
        # Step 2: Augment data
        print("Augmenting data for better model generalization...")
        X_aug, y_aug = trainer.augment_data(X, y, augmentation_factor=AUGMENTATION_FACTOR)
        
        # Step 3: Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_aug, y_aug, test_size=TEST_SPLIT, random_state=42, stratify=y_aug
        )
        
        print(f"\n{'=' * 70}")
        print("FINAL DATA SPLIT")
        print(f"{'=' * 70}")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")
        print(f"  (Validation split during training: {VALIDATION_SPLIT * 100:.0f}%)")
        print(f"{'=' * 70}\n")
        
        # Step 4: Build model
        num_classes = len(trainer.class_names)
        trainer.build_model(num_classes)
        
        # Step 5: Train model
        trainer.train(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, 
                     validation_split=VALIDATION_SPLIT)
        
        # Step 6: Evaluate model
        trainer.evaluate(X_test, y_test)
        
        # Step 7: Plot training history
        trainer.plot_training_history()
        
        # Step 8: Save model
        trainer.save_model('models/sinhala_model.keras')
        
        print("\n" + "=" * 70)
        print("✓ TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nNext steps:")
        print("1. Check the 'models' folder for saved model files")
        print("2. Review training_history.png for performance visualization")
        print("3. Update sinhala_model.py to use the trained model")
        print("4. Test the model with your Flask API")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPlease check:")
        print("1. Dataset path is correct")
        print("2. Dataset has proper folder structure (class folders with images)")
        print("3. All required packages are installed")
        sys.exit(1)


if __name__ == "__main__":
    main()
