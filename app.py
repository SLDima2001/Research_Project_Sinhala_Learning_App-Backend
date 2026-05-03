"""
Sinhala Learning Unified API
Combined Backend for:
1. Handwriting Recognition (454 Classes)
2. User Authentication (MongoDB + JWT)
3. Gamified Storytelling (Stories & Quizzes)
4. Text-to-Image (OCR + Real Image Search)
"""

import os
import sys
import json
import base64
import random
import traceback
import datetime
import uuid
import time
from io import BytesIO
from typing import Tuple, Dict, Optional, List

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
import io
from pydub import AudioSegment
import imageio_ffmpeg
import os

# Explicitly set ffmpeg path for pydub to the local binary provided by imageio_ffmpeg
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_exe)
AudioSegment.converter = ffmpeg_exe
AudioSegment.ffmpeg = ffmpeg_exe

from pymongo import MongoClient
from bson.binary import Binary

# Load environment variables
load_dotenv()

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# External Module Imports (Blueprints)
try:
    from auth import auth_bp
    from stories import stories_bp
    from text_to_image import text_to_image_bp
except ImportError as e:
    print(f"Warning: Could not import some module blueprints: {e}")

# Internal Model Import
try:
    from sinhala_model import SinhalaHandwritingModel
except ImportError:
    print("Warning: SinhalaHandwritingModel class not found in sinhala_model.py")

try:
    from modules.speech_feedback.processor import get_word_timestamps
    from modules.speech_feedback.evaluator import evaluate_pronunciation
except ImportError as e:
    print(f"Warning: Could not import speech feedback modules: {e}")
    get_word_timestamps = None
    evaluate_pronunciation = None

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.json.ensure_ascii = False  # Support Sinhala characters in JSON
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# MySQL/MongoDB connection (reusing ORI from .env if possible)
MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback")
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    db = mongo_client['sinhala_learning_app']  # Primary DB for users and stories
    voice_db = mongo_client['customerfeedback']  # DB for voice feedback recordings
    print("[OK] MongoDB client initialized (connection will be verified on first use)")
except Exception as _mongo_err:
    print(f"[WARN] MongoDB init failed: {_mongo_err} - running without DB")
    mongo_client = None
    db = None
    voice_db = None

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(stories_bp, url_prefix='/api')
app.register_blueprint(text_to_image_bp, url_prefix='/api/ti')

# ============================================================
# CONFIGURATION
# ============================================================
PORT = int(os.environ.get("PORT", 5002))
user_sessions = {}

# Primary Handwriting Model Initialization
try:
    model = SinhalaHandwritingModel()
    print("[OK] Primary Handwriting Model (454 classes) Initialized")
except Exception as e:
    print(f"[FAIL] Failed to load Primary Handwriting Model: {e}")
    model = None

# Sinhala character mapping (Truncated for brevity, normally loads from info.json)
SINHALA_LETTERS = {
    0: {"name": "අ", "romanized": "අ"},
    1: {"name": "ආ", "romanized": "ආ"},
    2: {"name": "ඇ", "romanized": "ඇ"},
    3: {"name": "ඈ", "romanized": "ඈ"},
    4: {"name": "ඉ", "romanized": "ඉ"},
    5: {"name": "ඊ", "romanized": "ඊ"},
    6: {"name": "උ", "romanized": "උ"},
    7: {"name": "එ", "romanized": "එ"},
    8: {"name": "ඒ", "romanized": "ඒ"},
    9: {"name": "ඔ", "romanized": "ඔ"},
    10: {"name": "ඕ", "romanized": "ඕ"},
    11: {"name": "ක", "romanized": "ක"},
    12: {"name": "කා", "romanized": "කා"},
    13: {"name": "කැ", "romanized": "කැ"},
    14: {"name": "කෑ", "romanized": "කෑ"},
    15: {"name": "කි", "romanized": "කි"},
    16: {"name": "කී", "romanized": "කී"},
    17: {"name": "කු", "romanized": "කු"},
    18: {"name": "කූ", "romanized": "කූ"},
    19: {"name": "ක්", "romanized": "ක්"},
    20: {"name": "කෝ", "romanized": "කෝ"},
    21: {"name": "ක්ර", "romanized": "ක්ර"},
    22: {"name": "ක්රි", "romanized": "ක්රි"},
    23: {"name": "ක්රී", "romanized": "ක්රී"},
    24: {"name": "ග", "romanized": "ග"},
    25: {"name": "ගා", "romanized": "ගා"},
    26: {"name": "ගැ", "romanized": "ගැ"},
    27: {"name": "ගෑ", "romanized": "ගෑ"},
    28: {"name": "ගි", "romanized": "ගි"},
    29: {"name": "ගී", "romanized": "ගී"},
    30: {"name": "ගු", "romanized": "ගු"},
    31: {"name": "ගූ", "romanized": "ගූ"},
    32: {"name": "ග්", "romanized": "ග්"},
    33: {"name": "ගෝ", "romanized": "ගෝ"},
    34: {"name": "ග්ර", "romanized": "ග්ර"},
    35: {"name": "ග්රි", "romanized": "ග්රි"},
    36: {"name": "ග්රී", "romanized": "ග්රී"},
    37: {"name": "ච", "romanized": "ච"},
    38: {"name": "චා", "romanized": "චා"},
    39: {"name": "චැ", "romanized": "චැ"},
    40: {"name": "චෑ", "romanized": "චෑ"},
    41: {"name": "චි", "romanized": "චි"},
    42: {"name": "චී", "romanized": "චී"},
    43: {"name": "චු", "romanized": "චු"},
    44: {"name": "චූ", "romanized": "චූ"},
    45: {"name": "ච්", "romanized": "ච්"},
    46: {"name": "චෝ", "romanized": "චෝ"},
    47: {"name": "ච්ර", "romanized": "ච්ර"},
    48: {"name": "ච්ර්", "romanized": "ච්ර්"},
    49: {"name": "ච්රී", "romanized": "ච්රී"},
    50: {"name": "ජ", "romanized": "ජ"},
    51: {"name": "ජා", "romanized": "ජා"},
    52: {"name": "ජැ", "romanized": "ජැ"},
    53: {"name": "ජෑ", "romanized": "ජෑ"},
    54: {"name": "ජි", "romanized": "ජි"},
    55: {"name": "ජී", "romanized": "ජී"},
    56: {"name": "ජු", "romanized": "ජු"},
    57: {"name": "ජූ", "romanized": "ජූ"},
    58: {"name": "ජ්", "romanized": "ජ්"},
    59: {"name": "ජෝ", "romanized": "ජෝ"},
    60: {"name": "ජ්ර", "romanized": "ජ්ර"},
    61: {"name": "ජ්රි", "romanized": "ජ්රි"},
    62: {"name": "ජ්රී", "romanized": "ජ්රී"},
    63: {"name": "ට", "romanized": "ට"},
    64: {"name": "ටා", "romanized": "ටා"},
    65: {"name": "ටැ", "romanized": "ටැ"},
    66: {"name": "ටෑ", "romanized": "ටෑ"},
    67: {"name": "ටි", "romanized": "ටි"},
    68: {"name": "ටී", "romanized": "ටී"},
    69: {"name": "ටු", "romanized": "ටු"},
    70: {"name": "ටූ", "romanized": "ටූ"},
    71: {"name": "ට්", "romanized": "ට්"},
    72: {"name": "ටෝ", "romanized": "ටෝ"},
    73: {"name": "ට්ර", "romanized": "ට්ර"},
    74: {"name": "ට්ර්", "romanized": "ට්ර්"},
    75: {"name": "ට්රි", "romanized": "ට්රි"},
    76: {"name": "ඩ", "romanized": "ඩ"},
    77: {"name": "ඩා", "romanized": "ඩා"},
    78: {"name": "ඩැ", "romanized": "ඩැ"},
    79: {"name": "ඩෑ", "romanized": "ඩෑ"},
    80: {"name": "ඩි", "romanized": "ඩි"},
    81: {"name": "ඩී", "romanized": "ඩී"},
    82: {"name": "ඩු", "romanized": "ඩු"},
    83: {"name": "ඩූ", "romanized": "ඩූ"},
    84: {"name": "ඩ්", "romanized": "ඩ්"},
    85: {"name": "ඩෝ", "romanized": "ඩෝ"},
    86: {"name": "ඩ්ර", "romanized": "ඩ්ර"},
    87: {"name": "ඩ්ර්", "romanized": "ඩ්ර්"},
    88: {"name": "ඩ්රි", "romanized": "ඩ්රි"},
    89: {"name": "ණ", "romanized": "ණ"},
    90: {"name": "ණා", "romanized": "ණා"},
    91: {"name": "ණි", "romanized": "ණි"},
    92: {"name": "ත", "romanized": "ත"},
    93: {"name": "තා", "romanized": "තා"},
    94: {"name": "ති", "romanized": "ති"},
    95: {"name": "තී", "romanized": "තී"},
    96: {"name": "තු", "romanized": "තු"},
    97: {"name": "තූ", "romanized": "තූ"},
    98: {"name": "ත්", "romanized": "ත්"},
    99: {"name": "තෝ", "romanized": "තෝ"},
    100: {"name": "ත්ර", "romanized": "ත්ර"},
    101: {"name": "ත්රා", "romanized": "ත්රා"},
    102: {"name": "ත්රි", "romanized": "ත්රි"},
    103: {"name": "ත්රී", "romanized": "ත්රී"},
    104: {"name": "ද", "romanized": "ද"},
    105: {"name": "දා", "romanized": "දා"},
    106: {"name": "දැ", "romanized": "දැ"},
    107: {"name": "දෑ", "romanized": "දෑ"},
    108: {"name": "දි", "romanized": "දි"},
    109: {"name": "දී", "romanized": "දී"},
    110: {"name": "දු", "romanized": "දු"},
    111: {"name": "දූ", "romanized": "දූ"},
    112: {"name": "ද්", "romanized": "ද්"},
    113: {"name": "දෝ", "romanized": "දෝ"},
    114: {"name": "ද්ර", "romanized": "ද්ර"},
    115: {"name": "ද්රෝ", "romanized": "ද්රෝ"},
    116: {"name": "ද්රා", "romanized": "ද්රා"},
    117: {"name": "ද්රි", "romanized": "ද්රි"},
    118: {"name": "ද්රී", "romanized": "ද්රී"},
    119: {"name": "න", "romanized": "න"},
    120: {"name": "නා", "romanized": "නා"},
    121: {"name": "නැ", "romanized": "නැ"},
    122: {"name": "නෑ", "romanized": "නෑ"},
    123: {"name": "නි", "romanized": "නි"},
    124: {"name": "නී", "romanized": "නී"},
    125: {"name": "නු", "romanized": "නු"},
    126: {"name": "නූ", "romanized": "නූ"},
    127: {"name": "න්", "romanized": "න්"},
    128: {"name": "නෝ", "romanized": "නෝ"},
    129: {"name": "න්ර", "romanized": "න්ර"},
    130: {"name": "න්රා", "romanized": "න්රා"},
    131: {"name": "න්රි", "romanized": "න්රි"},
    132: {"name": "න්රී", "romanized": "න්රී"},
    133: {"name": "ප", "romanized": "ප"},
    134: {"name": "පා", "romanized": "පා"},
    135: {"name": "පැ", "romanized": "පැ"},
    136: {"name": "පෑ", "romanized": "පෑ"},
    137: {"name": "පි", "romanized": "පි"},
    138: {"name": "පී", "romanized": "පී"},
    139: {"name": "පු", "romanized": "පු"},
    140: {"name": "පූ", "romanized": "පූ"},
    141: {"name": "ප්", "romanized": "ප්"},
    142: {"name": "ප්රෝ", "romanized": "ප්රෝ"},
    143: {"name": "පෝ", "romanized": "පෝ"},
    144: {"name": "ප්ර", "romanized": "ප්ර"},
    145: {"name": "ප්රා", "romanized": "ප්රා"},
    146: {"name": "ප්රි", "romanized": "ප්රි"},
    147: {"name": "ප්රී", "romanized": "ප්රී"},
    148: {"name": "බ", "romanized": "බ"},
    149: {"name": "බා", "romanized": "බා"},
    150: {"name": "බැ", "romanized": "බැ"},
    151: {"name": "බෑ", "romanized": "බෑ"},
    152: {"name": "බි", "romanized": "බි"},
    153: {"name": "බී", "romanized": "බී"},
    154: {"name": "බු", "romanized": "බු"},
    155: {"name": "බූ", "romanized": "බූ"},
    156: {"name": "බ්", "romanized": "බ්"},
    157: {"name": "බ්රෝ", "romanized": "බ්රෝ"},
    158: {"name": "බ්ර", "romanized": "බ්ර"},
    159: {"name": "බ්රා", "romanized": "බ්රා"},
    160: {"name": "බ්රි", "romanized": "බ්රි"},
    161: {"name": "බ්රී", "romanized": "බ්රී"},
    162: {"name": "බ්රෝ", "romanized": "බ්රෝ"},
    163: {"name": "ම", "romanized": "ම"},
    164: {"name": "මා", "romanized": "මා"},
    165: {"name": "මැ", "romanized": "මැ"},
    166: {"name": "මෑ", "romanized": "මෑ"},
    167: {"name": "මි", "romanized": "මි"},
    168: {"name": "මී", "romanized": "මී"},
    169: {"name": "මු", "romanized": "මු"},
    170: {"name": "මූ", "romanized": "මූ"},
    171: {"name": "ම්", "romanized": "ම්"},
    172: {"name": "මෝ", "romanized": "මෝ"},
    173: {"name": "ම්ར", "romanized": "ම්ར"},
    174: {"name": "ම්රා", "romanized": "ම්රා"},
    175: {"name": "ම්රි", "romanized": "ම්රි"},
    176: {"name": "ම්රී", "romanized": "ම්රී"},
    177: {"name": "ම්රෝ", "romanized": "ම්රෝ"},
    178: {"name": "ය", "romanized": "ය"},
    179: {"name": "යා", "romanized": "යා"},
    180: {"name": "යැ", "romanized": "යැ"},
    181: {"name": "යෑ", "romanized": "යෑ"},
    182: {"name": "යි", "romanized": "යි"},
    183: {"name": "යී", "romanized": "යී"},
    184: {"name": "යු", "romanized": "යු"},
    185: {"name": "යූ", "romanized": "යූ"},
    186: {"name": "ෝ", "romanized": "ෝ"},
    187: {"name": "ය්", "romanized": "ය්"},
    188: {"name": "hda", "romanized": "char_188"},
    189: {"name": "ර", "romanized": "ර"},
    190: {"name": "රා", "romanized": "රා"},
    191: {"name": "රැ", "romanized": "රැ"},
    192: {"name": "රැ", "romanized": "රැ"},
    193: {"name": "රු", "romanized": "රු"},
    194: {"name": "රූ", "romanized": "රූ"},
    195: {"name": "රි", "romanized": "රි"},
    196: {"name": "රී", "romanized": "රී"},
    197: {"name": "ල", "romanized": "ල"},
    198: {"name": "ලා", "romanized": "ලා"},
    199: {"name": "ලැ", "romanized": "ලැ"},
    200: {"name": "ලෑ", "romanized": "ලෑ"},
    201: {"name": "ලි", "romanized": "ලි"},
    202: {"name": "ලී", "romanized": "ලී"},
    203: {"name": "ලු", "romanized": "ලු"},
    204: {"name": "ලූ", "romanized": "ලූ"},
    205: {"name": "ල්", "romanized": "ල්"},
    206: {"name": ",da", "romanized": "char_206"},
    207: {"name": "ව", "romanized": "ව"},
    208: {"name": "වා", "romanized": "වා"},
    209: {"name": "වැ", "romanized": "වැ"},
    210: {"name": "වෑ", "romanized": "වෑ"},
    211: {"name": "වි", "romanized": "වි"},
    212: {"name": "වී", "romanized": "වී"},
    213: {"name": "වු", "romanized": "වු"},
    214: {"name": "වූ", "romanized": "වූ"},
    215: {"name": "ව්", "romanized": "ව්"},
    216: {"name": "jda", "romanized": "char_216"},
    217: {"name": "ව්ර", "romanized": "ව්ර"},
    218: {"name": "ව්රා", "romanized": "ව්රා"},
    219: {"name": "ව්රැ", "romanized": "ව්රැ"},
    220: {"name": "ව්රෑ", "romanized": "ව්රෑ"},
    221: {"name": "j%da", "romanized": "char_221"},
    222: {"name": "ශ", "romanized": "ශ"},
    223: {"name": "ශා", "romanized": "ශා"},
    224: {"name": "ශැ", "romanized": "ශැ"},
    225: {"name": "ශෑ", "romanized": "ශෑ"},
    226: {"name": "ශි", "romanized": "ශි"},
    227: {"name": "ශී", "romanized": "ශී"},
    228: {"name": "ශු", "romanized": "ශු"},
    229: {"name": "ශූ", "romanized": "ශූ"},
    230: {"name": "ශ්", "romanized": "ශ්"},
    231: {"name": "Yda", "romanized": "char_231"},
    232: {"name": "ශ්ර", "romanized": "ශ්ර"},
    233: {"name": "ශ්රා", "romanized": "ශ්රා"},
    234: {"name": "ශ්රැ", "romanized": "ශ්රැ"},
    235: {"name": "ශ්රෑ", "romanized": "ශ්රෑ"},
    236: {"name": "ශ්රි", "romanized": "ශ්රි"},
    237: {"name": "ශ්රී", "romanized": "ශ්රී"},
    238: {"name": "Y%da", "romanized": "char_238"},
    239: {"name": "ෂ", "romanized": "ෂ"},
    240: {"name": "ෂා", "romanized": "ෂා"},
    241: {"name": "ෂැ", "romanized": "ෂැ"},
    242: {"name": "ෂෑ", "romanized": "ෂෑ"},
    243: {"name": "ෂි", "romanized": "ෂි"},
    244: {"name": "ෂී", "romanized": "ෂී"},
    245: {"name": "ෂු", "romanized": "ෂු"},
    246: {"name": "ෂූ", "romanized": "ෂූ"},
    247: {"name": "ෂ්", "romanized": "ෂ්"},
    248: {"name": "Ida", "romanized": "char_248"},
    249: {"name": "ස", "romanized": "ස"},
    250: {"name": "සා", "romanized": "සා"},
    251: {"name": "සැ", "romanized": "සැ"},
    252: {"name": "සෑ", "romanized": "සෑ"},
    253: {"name": "සි", "romanized": "සි"},
    254: {"name": "සී", "romanized": "සී"},
    255: {"name": "සු", "romanized": "සු"},
    256: {"name": "සූ", "romanized": "සූ"},
    257: {"name": "ida", "romanized": "char_257"},
    258: {"name": "ස්ර", "romanized": "ස්ර"},
    259: {"name": "ස්රා", "romanized": "ස්රා"},
    260: {"name": "ස්රි", "romanized": "ස්රි"},
    261: {"name": "ස්රී", "romanized": "ස්රී"},
    262: {"name": "ස්", "romanized": "ස්"},
    263: {"name": "හ", "romanized": "හ"},
    264: {"name": "හා", "romanized": "හා"},
    265: {"name": "හැ", "romanized": "හැ"},
    266: {"name": "හෑ", "romanized": "හෑ"},
    267: {"name": "හි", "romanized": "හි"},
    268: {"name": "හී", "romanized": "හී"},
    269: {"name": "හු", "romanized": "හු"},
    270: {"name": "හූ", "romanized": "හූ"},
    271: {"name": "හ්", "romanized": "හ්"},
    272: {"name": "yda", "romanized": "char_272"},
    273: {"name": "ළ", "romanized": "ළ"},
    274: {"name": "ළා", "romanized": "ළා"},
    275: {"name": "ළැ", "romanized": "ළැ"},
    276: {"name": "ළෑ", "romanized": "ළෑ"},
    277: {"name": "ළි", "romanized": "ළි"},
    278: {"name": "ළී", "romanized": "ළී"},
    279: {"name": "ළූ", "romanized": "ළූ"},
    280: {"name": "ළූ", "romanized": "ළූ"},
    281: {"name": "ෆ", "romanized": "ෆ"},
    282: {"name": "ෆා", "romanized": "ෆා"},
    283: {"name": "ෆැ", "romanized": "ෆැ"},
    284: {"name": "ෆෑ", "romanized": "ෆෑ"},
    285: {"name": "ෆි", "romanized": "ෆි"},
    286: {"name": "ෆී", "romanized": "ෆී"},
    287: {"name": "ෆූ", "romanized": "ෆූ"},
    288: {"name": "ෆූ", "romanized": "ෆූ"},
    289: {"name": "ෆ්ර", "romanized": "ෆ්ර"},
    290: {"name": "ෆ්රි", "romanized": "ෆ්රි"},
    291: {"name": "ෆ්රී", "romanized": "ෆ්රී"},
    292: {"name": "ෆ්රැ", "romanized": "ෆ්රැ"},
    293: {"name": "ෆ්රෑ", "romanized": "ෆ්රෑ"},
    294: {"name": "ෆ්", "romanized": "ෆ්"},
    295: {"name": "*da", "romanized": "char_295"},
    296: {"name": "ක්රා", "romanized": "ක්රා"},
    297: {"name": "ක්රැ", "romanized": "ක්රැ"},
    298: {"name": "ක්රෑ", "romanized": "ක්රෑ"},
    299: {"name": "l%da", "romanized": "char_299"},
    300: {"name": ".%da", "romanized": "char_300"},
    301: {"name": "ඛ", "romanized": "ඛ"},
    302: {"name": "ඛා", "romanized": "ඛා"},
    303: {"name": "ඛි", "romanized": "ඛි"},
    304: {"name": "ඛී", "romanized": "ඛී"},
    305: {"name": "ඛ්", "romanized": "ඛ්"},
    306: {"name": "ඝ", "romanized": "ඝ"},
    307: {"name": "ඝා", "romanized": "ඝා"},
    308: {"name": "ඝැ", "romanized": "ඝැ"},
    309: {"name": "ඝෑ", "romanized": "ඝෑ"},
    310: {"name": "ඝි", "romanized": "ඝි"},
    311: {"name": "ඝී", "romanized": "ඝී"},
    312: {"name": "ඝු", "romanized": "ඝු"},
    313: {"name": "ඝූ", "romanized": "ඝූ"},
    314: {"name": ">da", "romanized": "char_314"},
    315: {"name": "ඝ්", "romanized": "ඝ්"},
    316: {"name": "ඝ්ර", "romanized": "ඝ්ර"},
    317: {"name": "ඝ්රා", "romanized": "ඝ්රා"},
    318: {"name": "ඝ්රි", "romanized": "ඝ්රි"},
    319: {"name": "ඝ්රී", "romanized": "ඝ්රී"},
    320: {"name": "ඳ", "romanized": "ඳ"},
    321: {"name": "ඳා", "romanized": "ඳා"},
    322: {"name": "ඳැ", "romanized": "ඳැ"},
    323: {"name": "ෑ", "romanized": "ෑ"},
    324: {"name": "ඳෑ", "romanized": "ඳෑ"},
    325: {"name": "ඳි", "romanized": "ඳි"},
    326: {"name": "ඳී", "romanized": "ඳී"},
    327: {"name": "ඳු", "romanized": "ඳු"},
    328: {"name": "ඳූ", "romanized": "ඳූ"},
    329: {"name": "|da", "romanized": "char_329"},
    330: {"name": "ඳ්", "romanized": "ඳ්"},
    331: {"name": "ඟ", "romanized": "ඟ"},
    332: {"name": "ඟා", "romanized": "ඟා"},
    333: {"name": "ඟැ", "romanized": "ඟැ"},
    334: {"name": "ඟෑ", "romanized": "ඟෑ"},
    335: {"name": "ඟි", "romanized": "ඟි"},
    336: {"name": "ඟී", "romanized": "ඟී"},
    337: {"name": "ඟු", "romanized": "ඟු"},
    338: {"name": "ඟූ", "romanized": "ඟූ"},
    339: {"name": "Õda", "romanized": "Õda"},
    340: {"name": "ඟ්", "romanized": "ඟ්"},
    341: {"name": "ඬ", "romanized": "ඬ"},
    342: {"name": "ැ", "romanized": "ැ"},
    343: {"name": "ඬා", "romanized": "ඬා"},
    344: {"name": "ඬැ", "romanized": "ඬැ"},
    345: {"name": "ඬෑ", "romanized": "ඬෑ"},
    346: {"name": "ඬි", "romanized": "ඬි"},
    347: {"name": "ඬී", "romanized": "ඬී"},
    348: {"name": "ඬු", "romanized": "ඬු"},
    349: {"name": "ඬූ", "romanized": "ඬූ"},
    350: {"name": "ඬda", "romanized": "ඬda"},
    351: {"name": "ඬ්", "romanized": "ඬ්"},
    352: {"name": "ඹ", "romanized": "ඹ"},
    353: {"name": "ඹා", "romanized": "ඹා"},
    354: {"name": "ඹැ", "romanized": "ඹැ"},
    355: {"name": "ඹෑ", "romanized": "ඹෑ"},
    356: {"name": "ඹි", "romanized": "ඹි"},
    357: {"name": "ඹී", "romanized": "ඹී"},
    358: {"name": "ඹු", "romanized": "ඹු"},
    359: {"name": "ඹූ", "romanized": "ඹූ"},
    360: {"name": "Uda", "romanized": "char_360"},
    361: {"name": "ඹ්", "romanized": "ඹ්"},
    362: {"name": "භ", "romanized": "භ"},
    363: {"name": "භා", "romanized": "භා"},
    364: {"name": "භැ", "romanized": "භැ"},
    365: {"name": "භෑ", "romanized": "භෑ"},
    366: {"name": "භි", "romanized": "භි"},
    367: {"name": "භී", "romanized": "භී"},
    368: {"name": "භු", "romanized": "භු"},
    369: {"name": "භූ", "romanized": "භූ"},
    370: {"name": "Nda", "romanized": "char_370"},
    371: {"name": "භ්", "romanized": "භ්"},
    372: {"name": "ධ", "romanized": "ධ"},
    373: {"name": "ධා", "romanized": "ධා"},
    374: {"name": "ධැ", "romanized": "ධැ"},
    375: {"name": "ධෑ", "romanized": "ධෑ"},
    376: {"name": ",ධි", "romanized": ",ධි"},
    377: {"name": ",ධී", "romanized": ",ධී"},
    378: {"name": ",ධු", "romanized": ",ධු"},
    379: {"name": ",ධූ", "romanized": ",ධූ"},
    380: {"name": "ධෝ", "romanized": "ධෝ"},
    381: {"name": "ධ්", "romanized": "ධ්"},
    382: {"name": "ඨ", "romanized": "ඨ"},
    383: {"name": "ඨා", "romanized": "ඨා"},
    384: {"name": "ඨැ", "romanized": "ඨැ"},
    385: {"name": "ඨි", "romanized": "ඨි"},
    386: {"name": "ඨී", "romanized": "ඨී"},
    387: {"name": "ඨු", "romanized": "ඨු"},
    388: {"name": "ඨූ", "romanized": "ඨූ"},
    389: {"name": "ඨ්", "romanized": "ඨ්"},
    390: {"name": "ඪ", "romanized": "ඪ"},
    391: {"name": "ඪා", "romanized": "ඪා"},
    392: {"name": "ඪි", "romanized": "ඪි"},
    393: {"name": "Vda", "romanized": "char_393"},
    394: {"name": "ඵ", "romanized": "ඵ"},
    395: {"name": "ඵා", "romanized": "ඵා"},
    396: {"name": "ඵු", "romanized": "ඵු"},
    397: {"name": "ඵි", "romanized": "ඵි"},
    398: {"name": "Mda", "romanized": "char_398"},
    399: {"name": "ඵ්", "romanized": "ඵ්"},
    400: {"name": "ථ", "romanized": "ථ"},
    401: {"name": "ථා", "romanized": "ථා"},
    402: {"name": "ථැ", "romanized": "ථැ"},
    403: {"name": "ථ්", "romanized": "ථ්"},
    404: {"name": "ා", "romanized": "ා"},
    405: {"name": "ෟ", "romanized": "ෟ"},
    406: {"name": "ණැ", "romanized": "ණැ"},
    407: {"name": "ණෑ", "romanized": "ණෑ"},
    408: {"name": "ෘ", "romanized": "ෘ"},
    409: {"name": "ණී", "romanized": "ණී"},
    410: {"name": "ණු", "romanized": "ණු"},
    411: {"name": "ණූ", "romanized": "ණූ"},
    412: {"name": "Kda", "romanized": "char_412"},
    413: {"name": "ණ්", "romanized": "ණ්"},
    414: {"name": "ඥ", "romanized": "ඥ"},
    415: {"name": "ඥා", "romanized": "ඥා"},
    416: {"name": "{da", "romanized": "char_416"},
    417: {"name": "ඤ", "romanized": "ඤ"},
    418: {"name": "ඤා", "romanized": "ඤා"},
    419: {"name": "ඤු", "romanized": "ඤු"},
    420: {"name": "[da", "romanized": "char_420"},
    421: {"name": "ඤ්", "romanized": "ඤ්"},
    422: {"name": "ඣ", "romanized": "ඣ"},
    423: {"name": "ඣා", "romanized": "ඣා"},
    424: {"name": "ඣු", "romanized": "ඣු"},
    425: {"name": "COda", "romanized": "char_425"},
    426: {"name": "ඣ්", "romanized": "ඣ්"},
    427: {"name": "ඦ", "romanized": "ඦ"},
    428: {"name": "ඦා", "romanized": "ඦා"},
    429: {"name": "ඦැ", "romanized": "ඦැ"},
    430: {"name": "ඦෑ", "romanized": "ඦෑ"},
    431: {"name": "ඦි", "romanized": "ඦි"},
    432: {"name": "ඦු", "romanized": "ඦු"},
    433: {"name": "ඦූ", "romanized": "ඦූ"},
    434: {"name": "ඦෝ", "romanized": "ඦෝ"},
    435: {"name": "ඦ්", "romanized": "ඦ්"},
    436: {"name": "ඡ", "romanized": "ඡ"},
    437: {"name": "ඡා", "romanized": "ඡා"},
    438: {"name": "ඡැ", "romanized": "ඡැ"},
    439: {"name": "ඡෑ", "romanized": "ඡෑ"},
    440: {"name": "ඡි", "romanized": "ඡි"},
    441: {"name": "ඡේ", "romanized": "ඡේ"},
    442: {"name": "තැ", "romanized": "තැ"},
    443: {"name": "තෑ", "romanized": "තෑ"},
    444: {"name": "ත්රැ", "romanized": "ත්රැ"},
    445: {"name": "ත්රෑ", "romanized": "ත්රෑ"},
    446: {"name": ";%da", "romanized": "char_446"},
    447: {"name": "ළු", "romanized": "ළු"},
    448: {"name": "ෲ", "romanized": "ෲ"},
    449: {"name": "HQ", "romanized": "char_449"},
    450: {"name": "ff", "romanized": "char_450"},
    451: {"name": "f", "romanized": "char_451"},
    452: {"name": "H", "romanized": "char_452"},
    453: {"name": "Hq", "romanized": "char_453"},
}


# ============================================================
# UTILITIES / ERROR HANDLING
# ============================================================
@app.errorhandler(Exception)
def handle_error(error):
    print(f"ERROR: {str(error)}")
    traceback.print_exc()
    status_code = getattr(error, 'code', 500)
    return jsonify({
        'success': False,
        'message': str(error),
        'error': error.__class__.__name__
    }), status_code

# ============================================================
# CORE ENDPOINTS
# ============================================================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'success': True,
        'message': 'Sinhala Learning Unified API - v3.0',
        'status': 'Online',
        'endpoints': [
            '/api/auth/*', '/api/stories', '/api/quiz/submit',
            '/api/predict', '/api/get-random-letter',
            '/api/ti/generate-image', '/api/ti/ocr-and-generate'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'models_loaded': model.model_loaded if model else False
    })

# ============================================================
# SENTENCES MODULE (Voice Feedback Practice - MongoDB Atlas)
# ============================================================
# MongoDB Atlas DB: 'customerfeedback', Collection: 'metadata'
# Fields: filename (str), text (str - Sinhala sentence)
_SENTENCES_DATA = []

def _load_sentences_from_mongo():
    """Load sentences from MongoDB Atlas (same connection as standalone voice backend)"""
    try:
        from pymongo import MongoClient as _MC
        import pymongo.errors
        _uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        # Use short timeouts to prevent hanging on startup
        _client = _MC(_uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, socketTimeoutMS=3000)
        _db_cf = _client['customerfeedback']
        metadata_col = _db_cf['metadata']
        timings_col = _db_cf['word_timings']

        # Force a quick check to see if server is available before doing a full query
        _client.admin.command('ping')

        metadata_docs = list(metadata_col.find())
        if not metadata_docs:
            print("[WARN] No sentences found in MongoDB metadata collection")
            return []

        # Load timings if available
        timings_doc = timings_col.find_one() or {}

        sentences = []
        for doc in metadata_docs:
            filename = doc.get('filename', '')
            text = doc.get('text', '')
            if not filename or not text:
                continue
            word_count = len(text.split())
            difficulty = 'easy' if word_count <= 6 else ('medium' if word_count <= 8 else 'hard')
            sentences.append({
                'id': filename,
                'text': text,
                'words': text.split(),
                'difficulty': difficulty,
                'hasAudio': False,  # Audio files not available on unified backend
                'audioPath': None,
                'timings': timings_doc.get(filename, [])
            })

        print(f"[OK] Loaded {len(sentences)} sentences from MongoDB Atlas (customerfeedback/metadata)")
        return sentences

    except Exception as e:
        print(f"[WARN] MongoDB sentences unavailable: {e}")
        return []

# Load sentences at startup
_SENTENCES_DATA = _load_sentences_from_mongo()

# Offline fallback (used when MongoDB is unavailable)
_OFFLINE_SENTENCES = [
    {"id": "off_001", "text": "ආයුබෝවන් සුභ දවසක්", "words": ["ආයුබෝවන්", "සුභ", "දවසක්"], "difficulty": "easy"},
    {"id": "off_002", "text": "ඔබ කොහෙද යන්නේ", "words": ["ඔබ", "කොහෙද", "යන්නේ"], "difficulty": "easy"},
    {"id": "off_003", "text": "මගේ නම සිතාරා", "words": ["මගේ", "නම", "සිතාරා"], "difficulty": "easy"},
    {"id": "off_004", "text": "ඔබට ස්තූතියි", "words": ["ඔබට", "ස්තූතියි"], "difficulty": "easy"},
    {"id": "off_005", "text": "සිංහල ඉගෙනීම ප්‍රසාදජනකයි", "words": ["සිංහල", "ඉගෙනීම", "ප්‍රසාදජනකයි"], "difficulty": "medium"},
    {"id": "off_006", "text": "ගෙදර යමු", "words": ["ගෙදර", "යමු"], "difficulty": "easy"},
    {"id": "off_007", "text": "ඔයා කොහොමද", "words": ["ඔයා", "කොහොමද"], "difficulty": "easy"},
    {"id": "off_008", "text": "අම්මා හොඳ කෑම හදනවා", "words": ["අම්මා", "හොඳ", "කෑම", "හදනවා"], "difficulty": "easy"},
    {"id": "off_009", "text": "ලංකාව ලස්සන රටක්", "words": ["ලංකාව", "ලස්සන", "රටක්"], "difficulty": "easy"},
    {"id": "off_010", "text": "හිරු එළිය ලස්සනයි", "words": ["හිරු", "එළිය", "ලස්සනයි"], "difficulty": "easy"},
    {"id": "off_011", "text": "කලාව ජීවිතය සුන්දර කරයි", "words": ["කලාව", "ජීවිතය", "සුන්දර", "කරයි"], "difficulty": "medium"},
    {"id": "off_012", "text": "මම ළමයෙක්", "words": ["මම", "ළමයෙක්"], "difficulty": "easy"},
    {"id": "off_013", "text": "මට පොත් ආසයි", "words": ["මට", "පොත්", "ආසයි"], "difficulty": "easy"},
    {"id": "off_014", "text": "කුරුල්ලෝ ගී කියනවා", "words": ["කුරුල්ලෝ", "ගී", "කියනවා"], "difficulty": "easy"},
    {"id": "off_015", "text": "පාසල ළඟ ගස් තිබෙනවා", "words": ["පාසල", "ළඟ", "ගස්", "තිබෙනවා"], "difficulty": "medium"},
]

def _get_active_sentences():
    """Return MongoDB sentences if available, else offline fallback"""
    return _SENTENCES_DATA if _SENTENCES_DATA else _OFFLINE_SENTENCES

@app.route('/api/sentences/random', methods=['GET'])
@app.route('/api/sentences/random/<difficulty>', methods=['GET'])
def get_random_sentences(difficulty=None):
    """Return random practice sentences, optionally filtered by difficulty"""
    count = int(request.args.get('count', 10))
    try:
        data = _get_active_sentences()
        source = 'mongodb' if _SENTENCES_DATA else 'offline'
        if difficulty and difficulty.lower() not in ('all', 'offline'):
            data = [s for s in data if s.get('difficulty') == difficulty.lower()]
        if not data:
            data = _OFFLINE_SENTENCES
            source = 'offline'
        selected = random.sample(data, min(count, len(data)))
        return jsonify({'sentences': selected, 'count': len(selected), 'source': source})
    except Exception as e:
        return jsonify({'sentences': _OFFLINE_SENTENCES[:count], 'count': min(count, len(_OFFLINE_SENTENCES)), 'source': 'offline', 'error': str(e)})

@app.route('/api/sentences', methods=['GET'])
def get_all_sentences():
    """Return all sentences"""
    try:
        data = _get_active_sentences()
        source = 'mongodb' if _SENTENCES_DATA else 'offline'
        return jsonify({'sentences': data, 'total': len(data), 'source': source})
    except Exception as e:
        return jsonify({'sentences': _OFFLINE_SENTENCES, 'total': len(_OFFLINE_SENTENCES), 'source': 'offline', 'error': str(e)})

# ============================================================
# HANDWRITING MODULE ROUTES
# ============================================================
@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict Sinhala character from handwritten image"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400
        
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Determine expected letter/class from payload or session
        expected_letter = data.get('expected_letter')
        expected_class = data.get('expected_class')
        
        session_id = data.get('session_id')
        if session_id and session_id in user_sessions:
            session_data = user_sessions[session_id]
            if not expected_letter:
                expected_letter = session_data.get('letter', {}).get('character', None)
            if expected_class is None:
                expected_class = session_data.get('letter', {}).get('id', None)
                
        # If expected_letter was provided but no expected_class, try to reverse lookup
        if expected_letter and expected_class is None:
            for k, v in SINHALA_LETTERS.items():
                if v.get('name') == expected_letter or v.get('romanized') == expected_letter or str(k) == str(expected_letter):
                    expected_class = k
                    break
        
        if model and model.model_loaded:
            # If we know the expected class, use the dedicated calculating function which handles penalties robustly
            if expected_class is not None:
                score_result = model.calculate_score(image, int(expected_class))
                
                # Make sure to return the actual Sinhala character name instead of an index
                predicted_letter_name = SINHALA_LETTERS.get(score_result['predicted_class'], {}).get('name', str(score_result['predicted_class']))
                
                # Update feedback strings
                feedback = 'Very good! Keep practicing!' if score_result['score'] >= 90 else 'Good effort! Keep trying!' if score_result['score'] >= 75 else 'Try again, make sure it matches the shape!'
                
                return jsonify({
                    'success': True,
                    'score': score_result['score'],
                    'confidence': score_result['confidence'],
                    'is_correct': score_result['is_correct'],
                    'feedback': feedback,
                    'predicted_letter': predicted_letter_name
                })
                
            # Fallback to standard prediction if we don't know what to expect
            prediction = model.predict(image)
            confidence_val = float(prediction.get('confidence', 0.0))
            score_val = round(confidence_val * 100, 2)
            
            raw_letter = prediction['top_3'][0]['letter'] if prediction.get('top_3') else 'Unknown'
            # Convert class format e.g. "10" to actual Sinhala character
            if str(raw_letter).isdigit():
                predicted_letter = SINHALA_LETTERS.get(int(raw_letter), {}).get('name', raw_letter)
            else:
                predicted_letter = raw_letter
            
            is_correct = score_val > 50
            if expected_letter and predicted_letter != expected_letter:
                 is_correct = False
                 # Massive penalty because it predicted the wrong letter
                 score_val = max(0, score_val - 80)

            return jsonify({
                'success': True,
                'score': score_val,
                'confidence': confidence_val,
                'is_correct': is_correct,
                'feedback': 'Very good! Keep practicing!' if score_val >= 90 else 'Good effort! Keep trying!' if score_val >= 75 else 'Keep practicing, you can do it!',
                'predicted_letter': predicted_letter
            })
        else:
            return jsonify({'success': False, 'message': 'Handwriting Model is offline'}), 503
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-random-letter', methods=['GET'])
def get_random_letter():
    user_id = request.args.get('user_id', 'anonymous')

    # Valid independent vowels and base consonants for practice
    VALID_PRACTICE_CLASSES = [
        0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 139, 150, 161, 165, # Independent vowels
        180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, # Consonants
        360, 375, 390, 405, 420, 435
    ]

    # Use the model's class names if available, otherwise fall back to a subset
    if model and model.model_loaded and model.class_names:
        available_valid_classes = [c for c in model.class_names if c.isdigit() and int(c) in VALID_PRACTICE_CLASSES]
        
        if available_valid_classes:
            class_str = random.choice(available_valid_classes)
            letter_id = model.class_names.index(class_str)
        else:
            letter_id = random.randint(0, len(model.class_names) - 1)
            class_str = model.class_names[letter_id]
        
        # letter_id is the 0-based index into class_names — this matches the model's predicted_class output directly
        # The folder name (class_str) is 1-indexed e.g. "1","17" — do NOT use that as the id
        char_info = SINHALA_LETTERS.get(letter_id, {"name": class_str, "romanized": class_str})
        character = char_info["name"]
        romanized = char_info["romanized"]
    else:
        # Fallback: pick from a list of common Sinhala vowels & consonants
        SINHALA_LETTERS_LIST = [
            {'id': 0, 'character': 'අ', 'romanized': 'a'},
            {'id': 1, 'character': 'ආ', 'romanized': 'aa'},
            {'id': 2, 'character': 'ඇ', 'romanized': 'ae'},
            {'id': 3, 'character': 'ඈ', 'romanized': 'aae'},
            {'id': 4, 'character': 'ඉ', 'romanized': 'i'},
            {'id': 5, 'character': 'ඊ', 'romanized': 'ii'},
            {'id': 6, 'character': 'උ', 'romanized': 'u'},
            {'id': 7, 'character': 'ඌ', 'romanized': 'uu'},
            {'id': 8, 'character': 'එ', 'romanized': 'e'},
            {'id': 9, 'character': 'ඒ', 'romanized': 'ee'},
            {'id': 10, 'character': 'ඔ', 'romanized': 'o'},
            {'id': 11, 'character': 'ඕ', 'romanized': 'oo'},
            {'id': 12, 'character': 'ක', 'romanized': 'ka'},
            {'id': 13, 'character': 'ග', 'romanized': 'ga'},
            {'id': 14, 'character': 'ච', 'romanized': 'cha'},
            {'id': 15, 'character': 'ජ', 'romanized': 'ja'},
            {'id': 16, 'character': 'ට', 'romanized': 'ta'},
            {'id': 17, 'character': 'ඩ', 'romanized': 'da'},
            {'id': 18, 'character': 'ත', 'romanized': 'tha'},
            {'id': 19, 'character': 'ද', 'romanized': 'dha'},
            {'id': 20, 'character': 'න', 'romanized': 'na'},
            {'id': 21, 'character': 'ප', 'romanized': 'pa'},
            {'id': 22, 'character': 'බ', 'romanized': 'ba'},
            {'id': 23, 'character': 'ම', 'romanized': 'ma'},
            {'id': 24, 'character': 'ය', 'romanized': 'ya'},
            {'id': 25, 'character': 'ර', 'romanized': 'ra'},
            {'id': 26, 'character': 'ල', 'romanized': 'la'},
            {'id': 27, 'character': 'ව', 'romanized': 'va'},
            {'id': 28, 'character': 'ස', 'romanized': 'sa'},
            {'id': 29, 'character': 'හ', 'romanized': 'ha'},
        ]
        chosen = random.choice(SINHALA_LETTERS_LIST)
        session_id = str(uuid.uuid4())
        user_sessions[session_id] = {'letter': chosen, 'timestamp': time.time()}
        return jsonify({'success': True, 'letter': chosen, 'session_id': session_id})

    letter_data = {'id': letter_id, 'character': character, 'romanized': romanized}
    session_id = str(uuid.uuid4())
    user_sessions[session_id] = {'letter': letter_data, 'timestamp': time.time()}

    return jsonify({
        'success': True,
        'letter': letter_data,
        'session_id': session_id
    })

# ============================================================
# VOICE PROCESSING HANDLERS
# ============================================================

@socketio.on('connect')
def handle_connect():
    print("Client connected to SocketIO")
    emit('connection_response', {'status': 'connected'})

@socketio.on('process_voice')
def handle_voice(data):
    """Process full voice recording"""
    try:
        from datetime import datetime
        if 'audio' not in data or 'target' not in data:
            emit('error', {'message': 'Missing audio or target text'})
            return

        audio_base64 = data['audio']
        target_text = data['target']

        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
        audio_bytes = base64.b64decode(audio_base64)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{UPLOAD_FOLDER}/temp_{timestamp}.wav"
        
        try:
            audio_io = io.BytesIO(audio_bytes)
            # Try to load it as whatever format it came in
            try:
                audio = AudioSegment.from_file(audio_io)
            except:
                # Fallback to m4a/aac since Expo uses that
                audio_io.seek(0)
                audio = AudioSegment.from_file(audio_io, format="m4a")
                
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(temp_filename, format="wav")
            print(f"Successfully converted and saved {temp_filename}")
        except Exception as e:
            print(f"Pydub conversion failed: {e}")
            raise Exception(f"Failed to process and format audio: {e}")

        if not get_word_timestamps or not evaluate_pronunciation:
            raise Exception("Speech feedback modules not loaded")

        raw_timestamps = get_word_timestamps(temp_filename)
        
        with open("debug_voice.txt", "a", encoding="utf-8") as f:
            f.write("====== VOICE PRACTICE DEBUG (FULL) ======\n")
            f.write(f"Target Text: '{target_text}'\n")
            f.write(f"Raw Timestamps (Spoken): {raw_timestamps}\n")
        
        final_feedback = evaluate_pronunciation(raw_timestamps, target_text)
        
        with open("debug_voice.txt", "a", encoding="utf-8") as f:
            f.write(f"Final Feedback: {final_feedback}\n")
            f.write("=========================================\n\n")
        
        emit('feedback_ui_update', final_feedback)
        
        try:
            os.remove(temp_filename)
        except:
            pass
            
    except Exception as e:
        print(f"Error in handle_voice: {str(e)}")
        traceback.print_exc()
        emit('error', {'message': str(e)})

@socketio.on('process_partial_audio')
def handle_partial_voice(data):
    """Process partial voice stream"""
    try:
        if 'audio' not in data or 'target' not in data:
            return
            
        audio_base64 = data['audio']
        target_text = data['target']
        
        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
        audio_bytes = base64.b64decode(audio_base64)
        
        temp_filename = f"{UPLOAD_FOLDER}/stream_temp_{request.sid}.wav"
        
        try:
            audio_io = io.BytesIO(audio_bytes)
            try:
                audio = AudioSegment.from_file(audio_io)
            except:
                audio_io.seek(0)
                audio = AudioSegment.from_file(audio_io, format="m4a")
                
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(temp_filename, format="wav")
            print(f"Partial stream processed: {temp_filename}")
        except Exception as e:
            print(f"Partial pydub conversion failed: {e}")
            return # Skip this chunk if we can't parse the format
                
        if get_word_timestamps and evaluate_pronunciation:
            raw_timestamps = get_word_timestamps(temp_filename)
            final_feedback = evaluate_pronunciation(raw_timestamps, target_text)
            print(f"--- PARTIAL DEBUG ---")
            print(f"Target: {target_text}")
            print(f"Spoken: {raw_timestamps}")
            print(f"Feedback: {final_feedback}")
            print(f"---------------------")
            emit('partial_feedback_update', final_feedback)
            
        try:
            os.remove(temp_filename)
        except:
            pass
            
    except Exception as e:
        print(f"Partial processing error: {e}")

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print(f"Unified Sinhala Learning API running on http://0.0.0.0:{PORT}")
    print("=" * 60)
    # Use '0.0.0.0' with allow_unsafe_werkzeug to prevent Windows socket errors
    try:
        socketio.run(app, host='0.0.0.0', port=PORT, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"[WARN] 0.0.0.0 binding failed ({e}), trying 127.0.0.1...")
        socketio.run(app, host='127.0.0.1', port=PORT, debug=False, allow_unsafe_werkzeug=True)
