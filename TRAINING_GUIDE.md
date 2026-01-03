# Sinhala Handwriting Recognition - Model Training Guide

## Overview
This guide explains how to train an AI model for Sinhala handwriting recognition using your dataset.

## Project Structure
```
Research_Project_Sinhala_Learning_App-Backend/
├── api/
│   ├── train_sinhala_model.py      # Main training script (NEW)
│   ├── train.bat                    # Quick start training (NEW)
│   ├── sinhala_model.py             # Model inference/prediction
│   ├── app.py                       # Flask API
│   ├── requirements.txt             # Python dependencies
│   └── models/                      # Trained models (will be created)
│
└── dataset/
    ├── train/                       # Training data (264 classes)
    │   ├── 1/
    │   ├── 2/
    │   └── ... (up to 264)
    ├── test/                        # Test data
    └── valid/                       # Validation data
```

## Prerequisites

### System Requirements
- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended)
- GPU support (NVIDIA CUDA) is optional but recommended for faster training
- Windows 10/11 or Linux

### Python Packages
All required packages are listed in `requirements.txt`:
- TensorFlow 2.20.0
- NumPy 1.26.4
- OpenCV 4.10.0.84
- Pillow 11.0.0
- scikit-learn 1.5.2
- Flask 3.1.0

## Installation Steps

### 1. Install Python Dependencies
```bash
cd api
pip install -r requirements.txt
```

### 2. Verify Dataset
Before training, verify your dataset structure:
```bash
python check_dataset.py
```

Expected output:
```
✅ Train folder exists!
✅ Total classes: 264
✅ Total training images: ~26,000+
✅ Average per class: ~100 images
🎉 Dataset looks PERFECT! Ready to train!
```

## Training the Model

### Quick Start (Windows)
Simply double-click `train.bat` in the `api` folder:
```
train.bat
```

### Manual Training (All Platforms)
```bash
cd api
python train_sinhala_model.py
```

### Training Configuration
Edit these parameters in `train_sinhala_model.py` (in the `main()` function):

```python
DATASET_PATH = "../dataset/train"      # Path to training data
IMG_SIZE = 128                          # Image size (128x128 pixels)
EPOCHS = 100                            # Number of training epochs
BATCH_SIZE = 32                         # Batch size for training
AUGMENTATION_FACTOR = 2                 # Data augmentation multiplier
VALIDATION_SPLIT = 0.15                 # Validation data percentage
TEST_SPLIT = 0.15                       # Test data percentage
```

## Training Process

### Step-by-Step Breakdown

1. **Load Dataset** (Step 1)
   - Loads all images from the dataset folder
   - Converts to grayscale
   - Resizes to 128x128 pixels
   - Normalizes pixel values to [0, 1]
   - Displays dataset statistics

2. **Data Augmentation** (Step 2)
   - Creates additional training samples through transformations:
     - Random rotation (-15° to +15°)
     - Random shift (-10% to +10%)
     - Random zoom (0.9x to 1.1x)
     - Random noise addition
   - Increases dataset size by augmentation factor

3. **Build Model** (Step 3)
   - Creates a CNN (Convolutional Neural Network) with:
     - 4 convolutional blocks (32→64→128→256 filters)
     - Batch normalization layers
     - Max pooling layers
     - Dropout layers (0.25-0.5)
     - 2 dense layers (512→256 neurons)
     - Output layer with softmax activation

4. **Train Model** (Step 4)
   - Trains the model on augmented dataset
   - Uses Adam optimizer with learning rate 0.001
   - Monitors validation accuracy
   - Implements early stopping if no improvement
   - Saves best model checkpoint
   - Reduces learning rate on plateau

5. **Evaluate Model** (Step 5)
   - Tests model on held-out test set
   - Reports test loss and accuracy

6. **Save Model** (Step 6)
   - Saves trained model as `sinhala_model.keras`
   - Saves model metadata as `sinhala_model_info.json`
   - Saves training history as `sinhala_model_history.json`
   - Generates performance visualization

## Output Files

After training completes, check the `models/` folder:

```
models/
├── sinhala_model.keras              # Trained model (main file)
├── sinhala_model_info.json          # Model metadata
├── sinhala_model_history.json       # Training history
├── best_model.keras                 # Best checkpoint
└── training_history.png             # Performance graphs
```

### Model Info File (`sinhala_model_info.json`)
```json
{
  "class_names": ["1", "2", "3", ...],
  "num_classes": 264,
  "img_height": 128,
  "img_width": 128,
  "trained_on": "2024-01-15T10:30:45.123456",
  "model_architecture": "CNN with 4 Conv blocks + Dense layers",
  "total_parameters": 2847456
}
```

## Training Monitoring

### During Training
The script displays:
- Current epoch and batch progress
- Training loss and accuracy
- Validation loss and accuracy
- Learning rate adjustments
- Best model checkpoint saves

### After Training
Review the generated files:
- `training_history.png` - Shows accuracy and loss curves
- `sinhala_model_history.json` - Detailed metrics per epoch

## Expected Performance

### Typical Results
- **Training Accuracy**: 95-99%
- **Validation Accuracy**: 90-95%
- **Test Accuracy**: 88-93%
- **Training Time**: 2-4 hours (CPU), 30-60 minutes (GPU)

### Factors Affecting Performance
- Dataset size and quality
- Image preprocessing
- Model architecture
- Training hyperparameters
- Data augmentation

## Troubleshooting

### Issue: "No class folders found"
**Solution**: Verify dataset path is correct and contains numbered folders (1, 2, 3, etc.)

### Issue: "Out of memory" error
**Solution**: 
- Reduce BATCH_SIZE (try 16 or 8)
- Reduce IMG_SIZE (try 96 or 64)
- Close other applications

### Issue: Low accuracy
**Solution**:
- Increase EPOCHS (try 150-200)
- Increase AUGMENTATION_FACTOR (try 3-4)
- Check dataset quality
- Verify image preprocessing

### Issue: Training is very slow
**Solution**:
- Install GPU support (CUDA/cuDNN)
- Reduce IMG_SIZE
- Increase BATCH_SIZE
- Reduce AUGMENTATION_FACTOR

## Using the Trained Model

### In Python
```python
from sinhala_model import SinhalaHandwritingModel

# Load the trained model
model = SinhalaHandwritingModel('models/sinhala_model.keras')

# Make predictions
result = model.predict('path/to/image.png')
print(f"Predicted class: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.2%}")

# Calculate score for learning app
score = model.calculate_score('path/to/image.png', correct_class=5)
print(f"Score: {score['score']}/100")
```

### In Flask API
The `app.py` automatically uses the trained model if available:
```bash
python app.py
```

Then make requests:
```bash
curl -X POST -F "image=@test.png" http://localhost:5000/predict
```

## Advanced Configuration

### Hyperparameter Tuning
For better results, experiment with:

```python
# In train_sinhala_model.py, modify the trainer.train() call:
trainer.train(
    X_train, y_train,
    epochs=150,              # Increase for more training
    batch_size=16,           # Smaller batch for more updates
    validation_split=0.2     # More validation data
)

# Modify model architecture in build_model():
layers.Conv2D(64, (5, 5), activation='relu')  # Larger kernels
layers.Dropout(0.3)                            # More dropout
```

### Using Different Image Sizes
```python
IMG_SIZE = 96  # or 64, 96, 128, 256
```

Smaller sizes = faster training but less detail
Larger sizes = slower training but more detail

## Next Steps

1. **Train the model** using `train.bat` or `python train_sinhala_model.py`
2. **Monitor training** - Watch the console output
3. **Review results** - Check `training_history.png`
4. **Test predictions** - Use `sinhala_model.py` to test
5. **Deploy** - Integrate with Flask API in `app.py`
6. **Fine-tune** - Adjust hyperparameters if needed

## Support & Documentation

### Key Files
- `train_sinhala_model.py` - Main training script with detailed comments
- `sinhala_model.py` - Model inference and prediction
- `app.py` - Flask API for web integration
- `check_dataset.py` - Dataset validation utility

### Model Architecture
The CNN model includes:
- **Input**: 128x128 grayscale images
- **Conv Blocks**: 4 blocks with increasing filters (32→64→128→256)
- **Regularization**: Batch normalization, dropout, early stopping
- **Output**: 264 classes (Sinhala letters)

## Performance Tips

1. **Data Quality**: Ensure images are clear and properly labeled
2. **Augmentation**: Use augmentation to increase effective dataset size
3. **Batch Size**: Larger batches = faster training, smaller = better generalization
4. **Learning Rate**: Start with 0.001, adjust if needed
5. **Epochs**: Train until validation accuracy plateaus
6. **GPU**: Use GPU for 10-20x faster training

## License & Attribution
This training script is part of the Sinhala Learning App research project.

---

**Last Updated**: 2024
**Version**: 2.0
