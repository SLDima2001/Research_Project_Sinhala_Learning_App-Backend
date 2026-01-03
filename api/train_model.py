"""
Complete Sinhala Handwriting Recognition Model Training Script
This script trains a CNN model on your Sinhala handwriting dataset
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
import json
from datetime import datetime

class SinhalaModelTrainer:
    def __init__(self, dataset_path, img_height=128, img_width=128):
        """
        Initialize the trainer
        
        Args:
            dataset_path: Path to dataset folder with structure:
                dataset/
                    letter_0/
                        image1.png
                        image2.png
                    letter_1/
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
        
    def load_dataset(self):
        """Load and preprocess the dataset"""
        print("=" * 60)
        print("Loading Dataset...")
        print("=" * 60)
        
        images = []
        labels = []
        
        # Get all subdirectories (each represents a letter class)
        class_folders = sorted([d for d in self.dataset_path.iterdir() if d.is_dir()])
        self.class_names = [d.name for d in class_folders]
        
        print(f"\nFound {len(self.class_names)} letter classes")
        
        for class_idx, class_folder in enumerate(class_folders):
            print(f"Loading class {class_idx}: {class_folder.name}...", end=" ")
            
            image_files = list(class_folder.glob("*.png")) + \
                         list(class_folder.glob("*.jpg")) + \
                         list(class_folder.glob("*.jpeg"))
            
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
                    
                except Exception as e:
                    print(f"\nError loading {img_path}: {e}")
                    continue
            
            print(f"{len(image_files)} images loaded")
        
        # Convert to numpy arrays
        X = np.array(images)
        y = np.array(labels)
        
        # Add channel dimension (grayscale)
        X = np.expand_dims(X, axis=-1)
        
        print(f"\nDataset loaded successfully!")
        print(f"Total images: {len(X)}")
        print(f"Image shape: {X.shape[1:]}")
        print(f"Number of classes: {len(self.class_names)}")
        
        return X, y
    
    def augment_data(self, images, labels, augmentation_factor=3):
        """
        Augment the dataset with transformations
        
        Args:
            images: Original images
            labels: Original labels
            augmentation_factor: How many augmented versions per image
        """
        print("\n" + "=" * 60)
        print("Augmenting Dataset...")
        print("=" * 60)
        
        augmented_images = []
        augmented_labels = []
        
        for img, label in zip(images, labels):
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
        
        print(f"Original dataset size: {len(images)}")
        print(f"Augmented dataset size: {len(X_aug)}")
        print(f"Augmentation factor: {len(X_aug) / len(images):.1f}x")
        
        return X_aug, y_aug
    
    def build_model(self, num_classes):
        """Build CNN model for Sinhala handwriting recognition"""
        print("\n" + "=" * 60)
        print("Building Model Architecture...")
        print("=" * 60)
        
        model = keras.Sequential([
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', 
                         input_shape=(self.img_height, self.img_width, 1)),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Fourth Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Flatten and Dense Layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            # Output Layer
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("\nModel Architecture:")
        model.summary()
        
        self.model = model
        return model
    
    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2):
        """Train the model"""
        print("\n" + "=" * 60)
        print("Training Model...")
        print("=" * 60)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        print(f"\nTraining samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        
        # Callbacks
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                'models/best_model.keras',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            )
        ]
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
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
        print("\n" + "=" * 60)
        print("Evaluating Model...")
        print("=" * 60)
        
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        print(f"\nTest Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy * 100:.2f}%")
        
        return test_loss, test_accuracy
    
    def save_model(self, save_path='models/sinhala_model.keras'):
        """Save the trained model"""
        print("\n" + "=" * 60)
        print("Saving Model...")
        print("=" * 60)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save Keras model
        self.model.save(save_path)
        print(f"✓ Model saved to: {save_path}")
        
        # Save class names
        class_info = {
            'class_names': self.class_names,
            'num_classes': len(self.class_names),
            'img_height': self.img_height,
            'img_width': self.img_width,
            'trained_on': datetime.now().isoformat()
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


def main():
    """Main training pipeline"""
    print("\n" + "=" * 60)
    print("SINHALA HANDWRITING RECOGNITION - MODEL TRAINING")
    print("=" * 60)
    
    # Configuration
    DATASET_PATH = "../dataset/train"  # Change this to your dataset path
    IMG_SIZE = 128
    EPOCHS = 50
    BATCH_SIZE = 32
    AUGMENTATION_FACTOR = 3
    
    # Initialize trainer
    trainer = SinhalaModelTrainer(
        dataset_path=DATASET_PATH,
        img_height=IMG_SIZE,
        img_width=IMG_SIZE
    )
    
    # Step 1: Load dataset
    X, y = trainer.load_dataset()
    
    # Step 2: Augment data (optional but recommended)
    print("\nDo you want to augment the data? (recommended)")
    X_aug, y_aug = trainer.augment_data(X, y, augmentation_factor=AUGMENTATION_FACTOR)
    
    # Step 3: Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_aug, y_aug, test_size=0.15, random_state=42, stratify=y_aug
    )
    
    print(f"\nFinal split:")
    print(f"Training: {len(X_train)} images")
    print(f"Testing: {len(X_test)} images")
    
    # Step 4: Build model
    num_classes = len(trainer.class_names)
    trainer.build_model(num_classes)
    
    # Step 5: Train model
    trainer.train(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE)
    
    # Step 6: Evaluate model
    trainer.evaluate(X_test, y_test)
    
    # Step 7: Save model
    trainer.save_model('models/sinhala_model.keras')
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check the 'models' folder for saved model files")
    print("2. Update sinhala_model.py to use the trained model")
    print("3. Test the model with your Flask API")


if __name__ == "__main__":
    main()