# Sinhala Handwriting Recognition Backend

Flask backend server for recognizing Sinhala handwritten text and generating images.

## Quick Start

### Option 1: Use the Startup Script (Recommended)
```bash
start_server.bat
```

### Option 2: Manual Setup
```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```

## Configuration

The server will start on `http://0.0.0.0:5001`

Update your mobile app's API_URL with your computer's IP address:
```typescript
const API_URL = 'http://YOUR_IP_ADDRESS:5001';
```

## Files

- `app.py` - Main Flask application
- `label_map.json` - Mapping of model outputs to Sinhala words (20 classes)
- `model/sinhala_handwriting_model (1).h5` - Trained TensorFlow model
- `requirements.txt` - Python dependencies
- `start_server.bat` - Automated startup script

## API Endpoints

### GET /health
Check server status and model information

### POST /predict
OCR prediction from image
- Input: multipart/form-data with 'file' field
- Output: detected text, confidence, top 3 predictions

### POST /generate-image
Generate image from Sinhala text
- Input: JSON with 'prompt' field
- Output: base64 encoded image

### POST /ocr-and-generate
Combined OCR + image generation
- Input: multipart/form-data with 'file' field
- Output: detected text, confidence, and generated image

## Supported Words

The model recognizes 20 Sinhala words:
බල්ලා, බළලා, ගස, මල, අහස, හිරු, චන්දය, තරු, ගෙදර, බස්, කාර්, පාසල, පුටුව, මේසය, පොත, පන්සල, මිනිසා, ළමයා, එළුවා, බුකුටා

## Troubleshooting

See the main [SETUP_GUIDE.md](../SETUP_GUIDE.md) for detailed troubleshooting steps.
