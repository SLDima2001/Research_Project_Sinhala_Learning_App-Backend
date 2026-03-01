"""
Sinhala Handwriting Recognition - Training Configuration
Centralized configuration for model training
"""

import json
from pathlib import Path
from datetime import datetime

class TrainingConfig:
    """Training configuration management"""
    
    # Dataset Configuration
    DATASET_PATH = "../dataset/train"
    TEST_DATASET_PATH = "../dataset/test"
    VALID_DATASET_PATH = "../dataset/valid"
    
    # Image Configuration
    IMG_HEIGHT = 128
    IMG_WIDTH = 128
    IMG_CHANNELS = 1  # Grayscale
    
    # Training Configuration
    EPOCHS = 100
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001
    VALIDATION_SPLIT = 0.15
    TEST_SPLIT = 0.15
    
    # Data Augmentation
    AUGMENTATION_FACTOR = 2
    AUGMENTATION_CONFIG = {
        'rotation_range': 15,           # -15 to +15 degrees
        'shift_range': 0.1,             # -10% to +10%
        'zoom_range': (0.9, 1.1),       # 0.9x to 1.1x
        'noise_std': 0.02,              # Gaussian noise standard deviation
    }
    
    # Model Architecture
    MODEL_NAME = "sinhala_cnn_v2"
    MODEL_ARCHITECTURE = {
        'conv_blocks': 4,
        'filters': [32, 64, 128, 256],
        'kernel_size': 3,
        'pool_size': 2,
        'dropout_conv': 0.25,
        'dropout_dense': 0.5,
        'dense_units': [512, 256],
    }
    
    # Callbacks Configuration
    CALLBACKS_CONFIG = {
        'early_stopping': {
            'monitor': 'val_loss',
            'patience': 15,
            'min_delta': 0.0001,
            'restore_best_weights': True,
        },
        'model_checkpoint': {
            'monitor': 'val_accuracy',
            'save_best_only': True,
            'mode': 'max',
        },
        'reduce_lr': {
            'monitor': 'val_loss',
            'factor': 0.5,
            'patience': 5,
            'min_lr': 0.00001,
        },
    }
    
    # Optimizer Configuration
    OPTIMIZER_CONFIG = {
        'type': 'adam',
        'learning_rate': 0.001,
        'beta_1': 0.9,
        'beta_2': 0.999,
        'epsilon': 1e-7,
    }
    
    # Loss and Metrics
    LOSS_FUNCTION = 'sparse_categorical_crossentropy'
    METRICS = ['accuracy']
    
    # Output Configuration
    MODELS_DIR = 'models'
    LOGS_DIR = 'logs'
    MODEL_FILENAME = 'sinhala_model.keras'
    INFO_FILENAME = 'sinhala_model_info.json'
    HISTORY_FILENAME = 'sinhala_model_history.json'
    PLOT_FILENAME = 'training_history.png'
    
    # Preprocessing Configuration
    PREPROCESSING_CONFIG = {
        'normalize': True,
        'normalize_range': (0, 1),
        'invert_if_white_bg': True,
        'white_bg_threshold': 127,
    }
    
    # Random Seed (for reproducibility)
    RANDOM_SEED = 42
    
    # Logging Configuration
    VERBOSE = 1  # 0=silent, 1=progress bar, 2=one line per epoch
    TENSORBOARD_ENABLED = True
    
    @classmethod
    def get_model_path(cls):
        """Get full model path"""
        return f"{cls.MODELS_DIR}/{cls.MODEL_FILENAME}"
    
    @classmethod
    def get_info_path(cls):
        """Get full info path"""
        return f"{cls.MODELS_DIR}/{cls.INFO_FILENAME}"
    
    @classmethod
    def get_history_path(cls):
        """Get full history path"""
        return f"{cls.MODELS_DIR}/{cls.HISTORY_FILENAME}"
    
    @classmethod
    def get_plot_path(cls):
        """Get full plot path"""
        return f"{cls.MODELS_DIR}/{cls.PLOT_FILENAME}"
    
    @classmethod
    def to_dict(cls):
        """Convert configuration to dictionary"""
        config_dict = {}
        for key in dir(cls):
            if not key.startswith('_') and key.isupper():
                value = getattr(cls, key)
                if not callable(value):
                    config_dict[key] = value
        return config_dict
    
    @classmethod
    def save_config(cls, filepath='models/training_config.json'):
        """Save configuration to JSON file"""
        Path(cls.MODELS_DIR).mkdir(exist_ok=True)
        
        config_dict = cls.to_dict()
        config_dict['saved_at'] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"✓ Configuration saved to: {filepath}")
    
    @classmethod
    def load_config(cls, filepath='models/training_config.json'):
        """Load configuration from JSON file"""
        if not Path(filepath).exists():
            print(f"⚠ Configuration file not found: {filepath}")
            return False
        
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        # Update class attributes
        for key, value in config_dict.items():
            if key != 'saved_at' and hasattr(cls, key):
                setattr(cls, key, value)
        
        print(f"✓ Configuration loaded from: {filepath}")
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "=" * 70)
        print("TRAINING CONFIGURATION")
        print("=" * 70)
        
        config_dict = cls.to_dict()
        
        sections = {
            'Dataset': ['DATASET_PATH', 'TEST_DATASET_PATH', 'VALID_DATASET_PATH'],
            'Image': ['IMG_HEIGHT', 'IMG_WIDTH', 'IMG_CHANNELS'],
            'Training': ['EPOCHS', 'BATCH_SIZE', 'LEARNING_RATE', 'VALIDATION_SPLIT', 'TEST_SPLIT'],
            'Augmentation': ['AUGMENTATION_FACTOR'],
            'Model': ['MODEL_NAME'],
            'Output': ['MODELS_DIR', 'MODEL_FILENAME'],
        }
        
        for section, keys in sections.items():
            print(f"\n{section}:")
            for key in keys:
                if key in config_dict:
                    value = config_dict[key]
                    print(f"  {key}: {value}")
        
        print(f"\n{'=' * 70}\n")
    
    @classmethod
    def validate_config(cls):
        """Validate configuration"""
        print("\nValidating configuration...")
        
        errors = []
        warnings = []
        
        # Check dataset path
        if not Path(cls.DATASET_PATH).exists():
            errors.append(f"Dataset path not found: {cls.DATASET_PATH}")
        
        # Check image size
        if cls.IMG_HEIGHT < 32 or cls.IMG_WIDTH < 32:
            warnings.append(f"Image size is very small: {cls.IMG_HEIGHT}x{cls.IMG_WIDTH}")
        
        if cls.IMG_HEIGHT > 512 or cls.IMG_WIDTH > 512:
            warnings.append(f"Image size is very large: {cls.IMG_HEIGHT}x{cls.IMG_WIDTH}")
        
        # Check epochs
        if cls.EPOCHS < 10:
            warnings.append(f"Number of epochs is low: {cls.EPOCHS}")
        
        if cls.EPOCHS > 500:
            warnings.append(f"Number of epochs is very high: {cls.EPOCHS}")
        
        # Check batch size
        if cls.BATCH_SIZE < 8:
            warnings.append(f"Batch size is very small: {cls.BATCH_SIZE}")
        
        if cls.BATCH_SIZE > 256:
            warnings.append(f"Batch size is very large: {cls.BATCH_SIZE}")
        
        # Check learning rate
        if cls.LEARNING_RATE < 0.00001:
            warnings.append(f"Learning rate is very small: {cls.LEARNING_RATE}")
        
        if cls.LEARNING_RATE > 0.1:
            warnings.append(f"Learning rate is very large: {cls.LEARNING_RATE}")
        
        # Check splits
        if cls.VALIDATION_SPLIT + cls.TEST_SPLIT >= 1.0:
            errors.append(f"Validation + Test split >= 1.0: {cls.VALIDATION_SPLIT + cls.TEST_SPLIT}")
        
        # Report results
        if errors:
            print("\n✗ ERRORS:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        if warnings:
            print("\n⚠ WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors:
            print("\n✓ Configuration is valid!")
        
        return True


# Preset configurations for different scenarios
class PresetConfigs:
    """Preset configurations for different training scenarios"""
    
    @staticmethod
    def quick_test():
        """Quick test configuration (fast training for testing)"""
        TrainingConfig.EPOCHS = 5
        TrainingConfig.BATCH_SIZE = 64
        TrainingConfig.AUGMENTATION_FACTOR = 1
        print("✓ Quick test configuration loaded")
    
    @staticmethod
    def balanced():
        """Balanced configuration (good accuracy with reasonable time)"""
        TrainingConfig.EPOCHS = 100
        TrainingConfig.BATCH_SIZE = 32
        TrainingConfig.AUGMENTATION_FACTOR = 2
        print("✓ Balanced configuration loaded")
    
    @staticmethod
    def high_accuracy():
        """High accuracy configuration (best results, longer training)"""
        TrainingConfig.EPOCHS = 200
        TrainingConfig.BATCH_SIZE = 16
        TrainingConfig.AUGMENTATION_FACTOR = 3
        print("✓ High accuracy configuration loaded")
    
    @staticmethod
    def gpu_optimized():
        """GPU optimized configuration"""
        TrainingConfig.EPOCHS = 150
        TrainingConfig.BATCH_SIZE = 64
        TrainingConfig.AUGMENTATION_FACTOR = 2
        print("✓ GPU optimized configuration loaded")
    
    @staticmethod
    def cpu_optimized():
        """CPU optimized configuration"""
        TrainingConfig.EPOCHS = 50
        TrainingConfig.BATCH_SIZE = 16
        TrainingConfig.AUGMENTATION_FACTOR = 1
        print("✓ CPU optimized configuration loaded")


def main():
    """Test configuration"""
    print("\n" + "=" * 70)
    print("TRAINING CONFIGURATION TEST")
    print("=" * 70)
    
    # Print current configuration
    TrainingConfig.print_config()
    
    # Validate configuration
    TrainingConfig.validate_config()
    
    # Save configuration
    TrainingConfig.save_config()
    
    print("\n" + "=" * 70)
    print("Configuration test completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
