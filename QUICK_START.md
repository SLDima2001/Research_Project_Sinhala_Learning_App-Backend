# 🚀 QUICK START GUIDE - Sinhala Handwriting Recognition Model Training

## ⚡ 30-Second Quick Start

### Windows Users
1. Open `api` folder
2. Double-click `train.bat`
3. Wait for training to complete (2-4 hours)
4. Check `models/` folder for trained model

### All Users (Command Line)
```bash
cd api
python train_sinhala_model.py
```

---

## 📋 Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] 8GB+ RAM available
- [ ] 10GB+ free disk space
- [ ] Dataset in `dataset/train/` folder
- [ ] Dependencies installed: `pip install -r requirements.txt`

---

## 🎯 Step-by-Step Training

### Step 1: Verify Dataset
```bash
cd api
python check_dataset.py
```

Expected output:
```
✅ Train folder exists!
✅ Total classes: 454
✅ Total training images: 26,000+
🎉 Dataset looks PERFECT! Ready to train!
```

### Step 2: Install Dependencies (if not done)
```bash
pip install -r requirements.txt
```

### Step 3: Start Training
```bash
python train_sinhala_model.py
```

Or on Windows, just double-click `train.bat`

### Step 4: Monitor Training
Watch the console output for:
- Dataset loading progress
- Model architecture summary
- Training progress (epoch by epoch)
- Validation accuracy
- Best model checkpoint saves

### Step 5: Review Results
After training completes, check:
- `models/sinhala_model.keras` - Trained model
- `models/training_history.png` - Performance graphs
- `models/sinhala_model_info.json` - Model metadata

---

## 📊 What to Expect

### Training Time
- **CPU**: 2-4 hours
- **GPU**: 30-60 minutes

### Performance
- **Training Accuracy**: 95-99%
- **Validation Accuracy**: 90-95%
- **Test Accuracy**: 88-93%

### Output Files
```
models/
├── sinhala_model.keras              (50-100 MB)
├── sinhala_model_info.json          (metadata)
├── sinhala_model_history.json       (training history)
├── best_model.keras                 (checkpoint)
└── training_history.png             (graphs)
```

---

## 🛠️ Common Tasks

### Test the Trained Model
```bash
python test_model.py
```

### Predict a Single Image
```bash
python quick_reference.py predict ../dataset/train/1/1.jpg
```

### Calculate Handwriting Score
```bash
python quick_reference.py score ../dataset/train/1/1.jpg 1
```

### Check Model Status
```bash
python quick_reference.py model
```

---

## ⚙️ Configuration Options

### Quick Test (5 minutes)
Edit `train_sinhala_model.py`, in `main()` function:
```python
EPOCHS = 5
BATCH_SIZE = 64
AUGMENTATION_FACTOR = 1
```

### High Accuracy (Longer Training)
```python
EPOCHS = 200
BATCH_SIZE = 16
AUGMENTATION_FACTOR = 3
```

### GPU Optimized
```python
EPOCHS = 150
BATCH_SIZE = 64
AUGMENTATION_FACTOR = 2
```

---

## 🐛 Troubleshooting

### "Out of Memory" Error
**Solution**: Reduce batch size in `train_sinhala_model.py`
```python
BATCH_SIZE = 16  # or 8
```

### "Dataset not found" Error
**Solution**: Verify dataset path
```bash
python check_dataset.py
```

### Very Low Accuracy
**Solution**: Increase training
```python
EPOCHS = 150  # increase from 100
AUGMENTATION_FACTOR = 3  # increase from 2
```

### Training is Very Slow
**Solution**: 
- Install GPU support (CUDA/cuDNN)
- Reduce image size: `IMG_SIZE = 96`
- Increase batch size: `BATCH_SIZE = 64`

---

## 📚 Documentation

- **TRAINING_GUIDE.md** - Detailed guide with all options
- **README_TRAINING.md** - Complete reference
- **SETUP_SUMMARY.md** - What was created and why
- **train_sinhala_model.py** - Fully commented code

---

## 🎓 Understanding the Training

### Data Augmentation
Creates variations of images to improve model generalization:
- Rotation: ±15 degrees
- Shift: ±10%
- Zoom: 0.9x to 1.1x
- Noise: Random pixel variations

### Model Architecture
```
Input (128x128 grayscale)
    ↓
Conv Block 1: 32 filters → BatchNorm → MaxPool → Dropout
    ↓
Conv Block 2: 64 filters → BatchNorm → MaxPool → Dropout
    ↓
Conv Block 3: 128 filters → BatchNorm → MaxPool → Dropout
    ↓
Conv Block 4: 256 filters → BatchNorm → MaxPool → Dropout
    ↓
Flatten
    ↓
Dense: 512 neurons → BatchNorm → Dropout
    ↓
Dense: 256 neurons → BatchNorm → Dropout
    ↓
Output: 454 classes (softmax)
```

### Training Process
1. **Load Data**: Read images from disk
2. **Augment**: Create variations
3. **Split**: 70% train, 15% validation, 15% test
4. **Train**: Update model weights
5. **Validate**: Check on validation set
6. **Evaluate**: Test on test set
7. **Save**: Store best model

---

## ✅ After Training

### 1. Verify Model Works
```bash
python quick_reference.py model
```

### 2. Test Predictions
```bash
python test_model.py
```

### 3. Review Performance
- Open `models/training_history.png`
- Check accuracy curves
- Look for overfitting

### 4. Deploy
- Model is ready to use with Flask API
- Can be integrated with mobile app
- Use `sinhala_model.py` for predictions

---

## 🚀 Next Steps

1. **Train the model** (this is the main step)
2. **Test predictions** with `test_model.py`
3. **Review performance** in `training_history.png`
4. **Deploy** with Flask API in `app.py`
5. **Integrate** with mobile application

---

## 📞 Need Help?

1. Check **TRAINING_GUIDE.md** for detailed troubleshooting
2. Review error messages in console
3. Verify dataset structure with `check_dataset.py`
4. Check system requirements (Python 3.9+, 8GB RAM)
5. Review code comments in `train_sinhala_model.py`

---

## 🎉 You're Ready!

Your complete training system is set up and ready to go. The model will be trained on 454 Sinhala character classes with 26,000+ images.

**Start training now:**
```bash
cd api
python train_sinhala_model.py
```

Or on Windows, double-click `train.bat`

---

**Version**: 2.0  
**Status**: Ready to Train  
**Dataset**: 454 classes, 26,000+ images  
**Model**: CNN with 4 convolutional blocks
