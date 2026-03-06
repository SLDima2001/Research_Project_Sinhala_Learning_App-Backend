<<<<<<< HEAD
# Sinhala learning app for 7-10 age children

## Project Overview

**Purpose**
An offline-capable mobile app that teaches Sinhala to primary school children through AI-driven interactive learning combining pronunciation practice, AR experiences, cultural storytelling, visual learning, and handwriting development.

## Core Architecture

**Platform:** React Native (Expo) - cross-platform mobile
**Game Engine:** Unity - interactive storytelling
**AI Capabilities:** Speech recognition, object detection, text-to-image generation
**Offline-First:** Pre-downloaded models and cached content for rural accessibility

## System Features

1. **Real-Time Voice Feedback & Pronunciation**
App speaks sentences with karaoke-style highlighting; child repeats; instant color-coded feedback (green=correct, red=mispronounced, gray=skipped); points awarded for accuracy.

2. **AR Object Recognition & Vocabulary Building**
Point camera at real objects; app identifies and displays Sinhala names with pronunciation; builds personalized vocabulary from surroundings.

3. **Gamified Sinhala Storytelling**
Interactive Sri Lankan folk stories with decision-based progression; animated visuals, TTS narration; badges and points system; teaches vocabulary and cultural heritage.

4. **Text-to-Image Generation**
Capture or type Sinhala text; app generates matching images; reinforces visual comprehension and vocabulary through AI-generated illustrations.

5. **Sinhala Handwriting Practice**
Displays letter/word formation patterns; children trace on screen; scoring based on stroke accuracy and form.

6. **AI-Driven Progress Dashboard**
Aggregates performance across all modules; visualizes strengths and improvement areas; provides adaptive learning recommendations; parent/teacher reports.

## Contributions & Collaboration

| Name | IT Number | Contribution |
|-----|-----|-----|
| **Fernando S K​​** | IT22904782 | Interactive Sinhala Culture & History Modules with Gamified Narratives​ |
| **Karunadasa M S T​​** | IT22007056 | Sinhala learning app with real time voice feedback and AR integration  |
| **Hettiarachchi M H A S K** |IT22322944 | An Interactive Sinhala Learning App With Text-to-imageClassification  |
| **Praveen K.K.G.D** | IT22900968  | AI-Powered Dashboard for Tracking Child Learning Progress with Sinhala Handwriting Recognition​  |

## GitHub Repository Links

Frontend - https://github.com/SLDima2001/Research_Project_Sinhala_Learning_App
Backend - https://github.com/SLDima2001/Research_Project_Sinhala_Learning_App-Backend

---

# 🎓 Sinhala Handwriting Recognition - AI Model Training System (Backend)

## 🚀 START HERE

This is a **complete, production-ready training system** for Sinhala handwritten character recognition using deep learning.

### ⚡ Quick Start (Choose One)

**Windows Users:**
```
1. Open: api/train.bat
2. Double-click it
3. Wait 2-4 hours
4. Done!
```

**Command Line:**
```bash
cd api
python train_sinhala_model.py
```

---

## 📚 Documentation Guide

Read these in order:

1. **[QUICK_START.md](QUICK_START.md)** ⭐ (5 min)
2. **[VISUAL_SUMMARY.md](VISUAL_SUMMARY.md)** (10 min)
3. **[SETUP_SUMMARY.md](SETUP_SUMMARY.md)** (10 min)
4. **[TRAINING_GUIDE.md](TRAINING_GUIDE.md)** (20 min)
5. **[FILE_INDEX.md](FILE_INDEX.md)** (reference)

---

## 📁 What's Included

### 🐍 Python Scripts (5 new files)
- **train_sinhala_model.py** - Main training script
- **test_model.py** - Model testing utility
- **quick_reference.py** - Quick commands
- **training_config.py** - Configuration management
- **api/README_TRAINING.md** - Training reference

### 🚀 Batch Scripts (1 new file)
- **train.bat** - Windows quick start

### 📚 Documentation (5 new files)
- **QUICK_START.md** - Quick start guide
- **VISUAL_SUMMARY.md** - Visual overview
- **SETUP_SUMMARY.md** - Setup summary
- **TRAINING_GUIDE.md** - Detailed guide
- **FILE_INDEX.md** - File index

---

## 🎯 What You Get

```
✅ Complete Training Pipeline
   - Data loading and preprocessing
   - Advanced data augmentation
   - Model building and training
   - Evaluation and saving

✅ Production-Ready Model
   - CNN with 4 convolutional blocks
   - Batch normalization
   - Dropout regularization
   - 454 Sinhala character classes

✅ Comprehensive Testing
   - Batch prediction testing
   - Confusion matrix generation
   - Classification reports
   - Performance visualization

✅ Easy Configuration
   - Preset configurations
   - Centralized management
   - Save/load from JSON

✅ Detailed Documentation
   - 5 comprehensive guides
   - Inline code comments
   - Troubleshooting section
   - Usage examples

✅ Quick Start Scripts
   - Windows batch script
   - Command-line interface
   - Python API
```

---

## 📊 Dataset

- **Total Classes**: 454 Sinhala characters
- **Training Images**: 26,000+
- **Image Format**: JPG/PNG grayscale
- **Image Size**: Variable (resized to 128x128)
- **Average per Class**: ~60 images

---

## 🎓 Training Pipeline

```
Load Dataset (26,000+ images)
    ↓
Data Augmentation (2-3x increase)
    ↓
Build CNN Model (4 conv blocks)
    ↓
Train Model (100 epochs)
    ↓
Evaluate on Test Set
    ↓
Save Model & Metadata
    ↓
Generate Performance Graphs
```

---

## 📈 Expected Performance

- **Training Accuracy**: 95-99%
- **Validation Accuracy**: 90-95%
- **Test Accuracy**: 88-93%
- **Training Time**: 2-4 hours (CPU), 30-60 minutes (GPU)
- **Model Size**: 50-100 MB

---

## 🛠️ Quick Commands

```bash
# Check dataset
python check_dataset.py

# Start training
python train_sinhala_model.py

# Test model
python test_model.py

# Quick commands
python quick_reference.py check          # Check dataset
python quick_reference.py model          # Check model
python quick_reference.py predict <img>  # Predict image
python quick_reference.py score <img> <class>  # Calculate score
python quick_reference.py batch <folder> # Batch predict
```

---

## 📋 Prerequisites

- Python 3.9+
- 8GB+ RAM
- 10GB+ free disk space
- Dependencies: `pip install -r requirements.txt`

---

## 🚀 Getting Started

### Step 1: Verify Dataset
```bash
cd api
python check_dataset.py
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start Training
```bash
python train_sinhala_model.py
```

### Step 4: Monitor Training
Watch the console output for:
- Dataset loading progress
- Model architecture summary
- Training progress (epoch by epoch)
- Validation accuracy
- Best model checkpoint saves

### Step 5: Review Results
After training, check:
- `models/sinhala_model.keras` - Trained model
- `models/training_history.png` - Performance graphs
- `models/sinhala_model_info.json` - Model metadata

---

## 🔧 Configuration

Edit `train_sinhala_model.py` to customize:

```python
DATASET_PATH = "../dataset/train"      # Dataset location
IMG_SIZE = 128                          # Image size
EPOCHS = 100                            # Training epochs
BATCH_SIZE = 32                         # Batch size
AUGMENTATION_FACTOR = 2                 # Data augmentation
VALIDATION_SPLIT = 0.15                 # Validation percentage
TEST_SPLIT = 0.15                       # Test percentage
```

---

## 📊 Output Files

After training, you'll have:

```
models/
├── sinhala_model.keras              # Trained model
├── sinhala_model_info.json          # Model metadata
├── sinhala_model_history.json       # Training history
├── best_model.keras                 # Best checkpoint
├── training_history.png             # Performance graphs
├── training_config.json             # Configuration used
├── confusion_matrix.png             # Confusion matrix (after testing)
└── classification_report.txt        # Detailed metrics (after testing)
```

---

## 🐛 Troubleshooting

### Out of Memory
```python
BATCH_SIZE = 16  # or 8
IMG_SIZE = 96    # or 64
```

### Low Accuracy
```python
EPOCHS = 150                # increase from 100
AUGMENTATION_FACTOR = 3     # increase from 2
```

### Training is Slow
- Install GPU support (CUDA/cuDNN)
- Reduce IMG_SIZE
- Increase BATCH_SIZE
- Reduce AUGMENTATION_FACTOR

For more help, see [TRAINING_GUIDE.md](TRAINING_GUIDE.md)

---

## 📖 Using the Trained Model

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

---

## 📚 File Structure

```
Research_Project_Sinhala_Learning_App-Backend/
│
├── 📄 README.md                         ← You are here
├── 📄 QUICK_START.md                    ← Quick start guide
├── 📄 VISUAL_SUMMARY.md                 ← Visual overview
├── 📄 SETUP_SUMMARY.md                  ← Setup summary
├── 📄 TRAINING_GUIDE.md                 ← Detailed guide
├── 📄 FILE_INDEX.md                     ← File index
│
├── api/
│   ├── 🚀 train_sinhala_model.py        ← Main training script
│   ├── 🚀 train.bat                     ← Windows quick start
│   ├── 🧪 test_model.py                 ← Testing utility
│   ├── ⚙️  quick_reference.py           ← Quick commands
│   ├── ⚙️  training_config.py           ← Configuration
│   ├── 📄 README_TRAINING.md            ← Training reference
│   ├── 📄 sinhala_model.py              ← Model inference
│   ├── 📄 app.py                        ← Flask API
│   ├── 📄 requirements.txt              ← Dependencies
│   └── models/                          ← Trained models
│
└── dataset/
    ├── train/                           ← Training data (454 classes)
    ├── test/                            ← Test data
    └── valid/                           ← Validation data
```

---

## 🎯 Next Steps

1. **Read** [QUICK_START.md](QUICK_START.md) (5 minutes)
2. **Verify** dataset with `python check_dataset.py`
3. **Train** with `python train_sinhala_model.py`
4. **Test** with `python test_model.py`
5. **Review** `models/training_history.png`
6. **Deploy** with Flask API

=======
# Research_Project_Sinhala_Learning_App




















Git Repo Links- Backend-https://github.com/SLDima2001/Research_Project_Sinhala_Learning_App-Backend/tree/real_time_feedback_Backend
                Frontend-
>>>>>>> origin/real_time_feedback_Backend
