# Sinhala Handwriting Recognition - AI Model Training

## 🎯 Overview

This project trains a deep learning CNN model to recognize Sinhala handwritten characters. The model is designed for use in a mobile learning application to provide real-time handwriting recognition and scoring.

## 📊 Dataset Information

- **Total Classes**: 264 Sinhala characters
- **Training Images**: 26,000+ images
- **Test Images**: Available in `dataset/test/`
- **Validation Images**: Available in `dataset/valid/`
- **Image Format**: PNG/JPG grayscale
- **Image Size**: Variable (resized to 128x128 during training)

## 🚀 Quick Start

### Option 1: Windows (Easiest)
```bash
cd api
train.bat
```

### Option 2: Command Line (All Platforms)
```bash
cd api
python train_sinhala_model.py
```

### Option 3: Python Script
```python
from train_sinhala_model import SinhalaModelTrainer

trainer = SinhalaModelTrainer("../dataset/train")
X, y = trainer.load_dataset()
X_aug, y_aug = trainer.augment_data(X, y)
trainer.build_model(len(trainer.class_names))
trainer.train(X_aug, y_aug, epochs=100)
trainer.save_model()
```

## 📋 Prerequisites

### System Requirements
- Python 3.9+
- 8GB RAM (16GB recommended)
- 10GB free disk space
- Windows 10/11 or Linux

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import tensorflow; print('TensorFlow OK')"
```

## 📁 Project Structure

```
api/
├── train_sinhala_model.py      ← Main training script (NEW)
├── train.bat                    ← Quick start (Windows) (NEW)
├── sinhala_model.py             ← Model inference
├── test_model.py                ← Testing utilities (NEW)
├── quick_reference.py           ← Quick commands (NEW)
├── app.py                       ← Flask API
├── requirements.txt             ← Dependencies
└── models/                      ← Trained models (created after training)
    ├── sinhala_model.keras
    ├── sinhala_model_info.json
    ├── sinhala_model_history.json
    ├── training_history.png
    └── best_model.keras

dataset/
├── train/                       ← Training data (264 folders)
├── test/                        ← Test data
└── valid/                       ← Validation data
```

## 🔧 Configuration

Edit `train_sinhala_model.py` to customize training:

```python
# In main() function:
DATASET_PATH = "../dataset/train"      # Dataset location
IMG_SIZE = 128                          # Image size (128x128)
EPOCHS = 100                            # Training epochs
BATCH_SIZE = 32                         # Batch size
AUGMENTATION_FACTOR = 2                 # Data augmentation
VALIDATION_SPLIT = 0.15                 # Validation percentage
TEST_SPLIT = 0.15                       # Test percentage
```

## 📈 Training Process

### Step 1: Load Dataset
- Loads all images from dataset folders
- Converts to grayscale
- Resizes to 128x128 pixels
- Normalizes pixel values

### Step 2: Data Augmentation
- Random rotation (-15° to +15°)
- Random shift (-10% to +10%)
- Random zoom (0.9x to 1.1x)
- Random noise addition
- Increases dataset size by 2-3x

### Step 3: Build Model
CNN Architecture:
- 4 Convolutional blocks (32→64→128→256 filters)
- Batch normalization layers
- Max pooling layers
- Dropout layers (0.25-0.5)
- 2 Dense layers (512→256)
- Output layer (264 classes)

### Step 4: Train Model
- Optimizer: Adam (lr=0.001)
- Loss: Sparse Categorical Crossentropy
- Metrics: Accuracy
- Callbacks: Early stopping, model checkpoint, learning rate reduction

### Step 5: Evaluate
- Tests on held-out test set
- Reports accuracy and loss

### Step 6: Save Model
- Saves trained model
- Saves metadata and training history
- Generates performance visualization

## 📊 Expected Results

### Performance Metrics
- **Training Accuracy**: 95-99%
- **Validation Accuracy**: 90-95%
- **Test Accuracy**: 88-93%

### Training Time
- **CPU**: 2-4 hours
- **GPU (NVIDIA)**: 30-60 minutes

### Model Size
- **Model File**: ~50-100 MB
- **Total with metadata**: ~100-150 MB

## 🛠️ Utilities

### Check Dataset
```bash
python check_dataset.py
```

### Test Model
```bash
python test_model.py
```

### Quick Commands
```bash
# Check dataset status
python quick_reference.py check

# Check model status
python quick_reference.py model

# Predict single image
python quick_reference.py predict ../dataset/train/1/1.png

# Calculate score
python quick_reference.py score ../dataset/train/1/1.png 1

# Batch predict
python quick_reference.py batch ../dataset/train/1
```

## 💻 Using the Trained Model

### In Python
```python
from sinhala_model import SinhalaHandwritingModel

# Load model
model = SinhalaHandwritingModel('models/sinhala_model.keras')

# Predict
result = model.predict('image.png')
print(f"Class: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.2%}")

# Calculate score
score = model.calculate_score('image.png', correct_class=5)
print(f"Score: {score['score']}/100")
```

### In Flask API
```bash
python app.py
```

Then make requests:
```bash
curl -X POST -F "image=@test.png" http://localhost:5000/predict
```

## 🐛 Troubleshooting

### Issue: "No class folders found"
**Solution**: Verify dataset path and folder structure

### Issue: "Out of memory"
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

### Issue: Training is slow
**Solution**:
- Install GPU support (CUDA/cuDNN)
- Reduce IMG_SIZE
- Increase BATCH_SIZE
- Reduce AUGMENTATION_FACTOR

## 📚 Documentation

- **TRAINING_GUIDE.md** - Detailed training guide
- **train_sinhala_model.py** - Commented training script
- **sinhala_model.py** - Model inference documentation
- **test_model.py** - Testing utilities

## 🔍 Model Architecture Details

### Input Layer
- 128x128 grayscale images
- Normalized to [0, 1]

### Convolutional Blocks
```
Block 1: Conv2D(32) → BatchNorm → MaxPool → Dropout(0.25)
Block 2: Conv2D(64) → BatchNorm → MaxPool → Dropout(0.25)
Block 3: Conv2D(128) → BatchNorm → MaxPool → Dropout(0.25)
Block 4: Conv2D(256) → BatchNorm → MaxPool → Dropout(0.25)
```

### Dense Layers
```
Flatten → Dense(512) → BatchNorm → Dropout(0.5)
       → Dense(256) → BatchNorm → Dropout(0.5)
       → Dense(264) → Softmax
```

### Total Parameters
- Approximately 2.8 million parameters

## 📊 Output Files

After training, check `models/` folder:

```
models/
├── sinhala_model.keras              # Main model file
├── sinhala_model_info.json          # Model metadata
├── sinhala_model_history.json       # Training history
├── best_model.keras                 # Best checkpoint
├── training_history.png             # Performance graphs
├── confusion_matrix.png             # Confusion matrix (after testing)
└── classification_report.txt        # Detailed metrics (after testing)
```

## 🎓 Learning Resources

### Understanding the Model
- CNN basics: https://en.wikipedia.org/wiki/Convolutional_neural_network
- TensorFlow/Keras: https://www.tensorflow.org/guide
- Image preprocessing: https://en.wikipedia.org/wiki/Digital_image_processing

### Improving Performance
1. **Data Quality**: Ensure clear, well-labeled images
2. **Augmentation**: Use more augmentation for small datasets
3. **Architecture**: Experiment with different layer configurations
4. **Hyperparameters**: Tune learning rate, batch size, epochs
5. **Regularization**: Adjust dropout and batch normalization

## 🚀 Next Steps

1. **Train the model**
   ```bash
   cd api
   python train_sinhala_model.py
   ```

2. **Monitor training**
   - Watch console output
   - Check TensorBoard logs (optional)

3. **Review results**
   - Check `training_history.png`
   - Review accuracy metrics

4. **Test predictions**
   ```bash
   python test_model.py
   ```

5. **Deploy**
   - Update Flask API
   - Test with mobile app
   - Monitor performance

## 📝 Notes

- First training may take longer due to data loading
- Model will be saved automatically during training
- Early stopping prevents overfitting
- Learning rate is reduced on plateau
- Best model checkpoint is saved

## 🤝 Support

For issues or questions:
1. Check TRAINING_GUIDE.md
2. Review error messages carefully
3. Verify dataset structure
4. Check system requirements
5. Review code comments

## 📄 License

This project is part of the Sinhala Learning App research project.

---

**Version**: 2.0  
**Last Updated**: 2024  
**Status**: Ready for training
