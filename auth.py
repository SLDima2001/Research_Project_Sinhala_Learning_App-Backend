"""
Authentication routes for user registration and login
Uses MongoDB for user storage and JWT for session management
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# MongoDB Configuration
# Set MONGO_URI environment variable with your correct MongoDB connection string
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/
# For local MongoDB: mongodb://localhost:27017/
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['sinhala_learning_app']
users_collection = db['users']

# JWT Secret Key
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Index will be created on first use
_index_created = False

def ensure_index():
    """Create unique index on email field if not already created"""
    global _index_created
    if not _index_created:
        try:
            users_collection.create_index('email', unique=True)
            _index_created = True
        except Exception as e:
            print(f"Warning: Could not create index: {e}")


def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = users_collection.find_one({'_id': data['user_id']})
            
            if not current_user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    print("\n=== REGISTER REQUEST RECEIVED ===")
    try:
        ensure_index()
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Validate input
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email already registered'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(password)
        
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name or email.split('@')[0],
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, SECRET_KEY, algorithm='HS256')
        
        # Ensure token is a string (PyJWT 1.x returns bytes, 2.x returns string)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'name': user_data['name']
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'message': 'Registration failed', 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login an existing user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        # Find user
        user = users_collection.find_one({'email': email})
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password_hash(user['password'], password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Generate JWT token
        user_id = str(user['_id'])
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, SECRET_KEY, algorithm='HS256')
        
        # Ensure token is a string (PyJWT 1.x returns bytes, 2.x returns string)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_id,
                'email': user['email'],
                'name': user.get('name', email.split('@')[0])
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed', 'error': str(e)}), 500


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if token is valid and return user info"""
    try:
        user_id = str(current_user['_id'])
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': current_user['email'],
                'name': current_user.get('name', current_user['email'].split('@')[0])
            }
        }), 200
    except Exception as e:
        print(f"Verify error: {str(e)}")
        return jsonify({'success': False, 'message': 'Verification failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user profile"""
    try:
        user_id = str(current_user['_id'])
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': current_user['email'],
                'name': current_user.get('name', current_user['email'].split('@')[0]),
                'created_at': current_user.get('created_at').isoformat() if current_user.get('created_at') else None
            }
        }), 200
    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get user info'}), 500
