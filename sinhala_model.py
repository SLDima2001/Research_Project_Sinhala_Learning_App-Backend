"""
Sinhala Handwriting Recognition Model - Production Version with Trained Model
File: sinhala_model.py
"""

import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from tensorflow import keras
import json
import os
import random

class SinhalaHandwritingModel:
    """
    Production handwriting recognition model using trained CNN
    Automatically loads trained model or falls back to mock mode
    """
    
    def __init__(self, model_path='models/sinhala_model.keras', num_classes=454):
        """
        Initialize the Sinhala handwriting recognition model
        
        Args:
            model_path: Path to the trained Keras model file
            num_classes: Number of Sinhala letter classes (default: 59)
        """
        self.num_classes = num_classes
        self.img_height = 128
        self.img_width = 128
        self.model = None
        self.class_names = []
        self.model_loaded = False
        
        print("=" * 60)
        print("Sinhala Handwriting Recognition Model")
        print("=" * 60)
        
        # Try to load the trained model
        if os.path.exists(model_path):
            self.load_model(model_path)
        else:
            print(f"\n⚠️  Model file not found at: {model_path}")
            print("⚠️  Running in MOCK MODE")
            print("⚠️  Please train the model first using train_model.py")
            print("\nTo train the model:")
            print("  1. Prepare your dataset in 'dataset/' folder")
            print("  2. Run: python train_model.py")
            print("  3. Restart this application")
        
        print("=" * 60 + "\n")
    
    def load_model(self, model_path):
        """
        Load the trained Keras model from disk
        
        Args:
            model_path: Path to the saved model file
        """
        try:
            print(f"\nLoading model from: {model_path}")
            
            # Load the Keras model
            self.model = keras.models.load_model(model_path)
            self.model_loaded = True
            
            print("✓ Model loaded successfully!")
            
            # Load class information (letter names, etc.)
            info_path = model_path.replace('.keras', '_info.json')
            if os.path.exists(info_path):
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    self.class_names = info.get('class_names', [])
                    self.img_height = info.get('img_height', 128)
                    self.img_width = info.get('img_width', 128)
                    
                print(f"✓ Loaded {len(self.class_names)} class names")
                print(f"✓ Input size: {self.img_height}x{self.img_width}")
                
                trained_on = info.get('trained_on', 'Unknown')
                print(f"✓ Model trained on: {trained_on}")
            else:
                print("⚠️  Model info file not found, using defaults")
            
            # Test the model with a dummy input
            dummy_input = np.zeros((1, self.img_height, self.img_width, 1))
            _ = self.model.predict(dummy_input, verbose=0)
            print("✓ Model test successful!")
            
        except Exception as e:
            print(f"\n✗ Error loading model: {e}")
            print("⚠️  Falling back to MOCK MODE")
            self.model_loaded = False
            self.model = None
    
    def preprocess_image(self, image_data):
        """
        Preprocess image for model input
        Handles various input types: file path, PIL Image, or numpy array
        
        Args:
            image_data: Image as file path (str), PIL Image, or numpy array
            
        Returns:
            Preprocessed image ready for model input (numpy array)
        """
        # Convert to numpy array based on input type
        if isinstance(image_data, str):
            # File path
            img = cv2.imread(image_data, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Could not read image from path: {image_data}")
        elif isinstance(image_data, Image.Image):
            # PIL Image
            img = np.array(image_data.convert('L'))
        else:
            # Assume numpy array
            img = image_data
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize to model input size
        img = cv2.resize(img, (self.img_width, self.img_height))
        
        # Invert if background is white (convert to black background)
        # This helps with consistency in training
        if np.mean(img) > 127:
            img = 255 - img
        
        # Normalize pixel values to [0, 1]
        img = img.astype('float32') / 255.0
        
        # Add channel dimension for grayscale (height, width, 1)
        img = np.expand_dims(img, axis=-1)
        
        # Add batch dimension (1, height, width, 1)
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def predict(self, image_data):
        """
        Predict the Sinhala letter from handwriting image
        
        Args:
            image_data: Input image (various formats supported)
            
        Returns:
            dict containing:
                - predicted_class: Class ID of predicted letter
                - confidence: Confidence score (0-1)
                - top_3: Top 3 predictions with confidence
                - all_probabilities: Full probability distribution
        """
        # Preprocess the image
        processed_img = self.preprocess_image(image_data)
        
        # Use trained model if available, otherwise mock prediction
        if not self.model_loaded or self.model is None:
            return self._mock_predict(processed_img)
        
        try:
            # Get predictions from the trained model
            predictions = self.model.predict(processed_img, verbose=0)[0]
            
            # Get the predicted class (highest probability)
            predicted_class = int(np.argmax(predictions))
            confidence = float(predictions[predicted_class])
            
            # Get top 3 predictions
            top_3_indices = np.argsort(predictions)[-3:][::-1]
            top_3_predictions = [
                {
                    'class': int(idx),
                    'confidence': float(predictions[idx]),
                    'letter': self.class_names[idx] if idx < len(self.class_names) else f"class_{idx}"
                }
                for idx in top_3_indices
            ]
            
            return {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'top_3': top_3_predictions,
                'all_probabilities': predictions.tolist(),
                'model_mode': 'trained'
            }
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return self._mock_predict(processed_img)
    
    def _mock_predict(self, processed_img):
        """
        Fallback mock prediction when trained model is not available
        Used for testing purposes only
        
        Args:
            processed_img: Preprocessed image
            
        Returns:
            Mock prediction dictionary
        """
        predicted_class = random.randint(0, self.num_classes - 1)
        confidence = random.uniform(0.6, 0.95)
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'top_3': [
                {
                    'class': predicted_class, 
                    'confidence': confidence, 
                    'letter': 'mock'
                },
                {
                    'class': (predicted_class + 1) % self.num_classes, 
                    'confidence': confidence * 0.6, 
                    'letter': 'mock'
                },
                {
                    'class': (predicted_class + 2) % self.num_classes, 
                    'confidence': confidence * 0.3, 
                    'letter': 'mock'
                }
            ],
            'model_mode': 'mock',
            'warning': 'Using mock predictions - train the model for real predictions'
        }
    
    def calculate_score(self, image_data, correct_class):
        """
        Calculate handwriting score based on model prediction
        Compares prediction with correct answer and assigns score
        
        Args:
            image_data: Input handwriting image
            correct_class: The correct class ID for this handwriting
            
        Returns:
            dict containing:
                - score: Score from 0-100
                - is_correct: Boolean indicating if prediction matches correct class
                - confidence: Model's confidence in prediction
                - predicted_class: What the model predicted
                - model_loaded: Whether real model is being used
                - quality: Image quality metrics
        """
        # Get prediction from the model
        prediction = self.predict(image_data)
        
        predicted_class = prediction['predicted_class']
        confidence = prediction['confidence']
        
        # Check if the prediction is correct
        is_correct = (predicted_class == correct_class)
        
        # Calculate score based on correctness and confidence
        if is_correct:
            # Correct prediction
            # Base score: 70, Confidence bonus: up to 30 points
            base_score = 70
            confidence_bonus = confidence * 30
            score = base_score + confidence_bonus
            
        else:
            # Wrong prediction
            # Check if correct class is in top 3 predictions
            top_3_classes = [p['class'] for p in prediction.get('top_3', [])]
            
            if correct_class in top_3_classes:
                # Close but not perfect - give partial credit
                correct_class_conf = next(
                    (p['confidence'] for p in prediction['top_3'] 
                     if p['class'] == correct_class),
                    0.0
                )
                score = 40 + (correct_class_conf * 30)
            else:
                # Completely wrong
                score = 20 + (confidence * 20)
        
        # Analyze drawing quality
        quality_info = self._analyze_quality(image_data)
        
        # Adjust score based on drawing quality
        if not quality_info['has_content']:
            # No drawing or very poor quality
            score = min(score, 30)
        
        # Ensure score is within valid range [0, 100]
        score = max(0, min(100, score))
        
        return {
            'score': round(float(score), 2),
            'is_correct': is_correct,
            'confidence': round(float(confidence), 4),
            'predicted_class': predicted_class,
            'correct_class': correct_class,
            'model_loaded': self.model_loaded,
            'model_mode': prediction.get('model_mode', 'unknown'),
            'quality': quality_info,
            'top_3': prediction.get('top_3', [])
        }
    
    def _analyze_quality(self, image_data):
        """
        Analyze the quality of the handwriting image
        Checks for presence of content and coverage
        
        Args:
            image_data: Input image
            
        Returns:
            dict with quality metrics
        """
        # Convert to grayscale numpy array
        if isinstance(image_data, Image.Image):
            img = np.array(image_data.convert('L'))
        elif isinstance(image_data, str):
            img = cv2.imread(image_data, cv2.IMREAD_GRAYSCALE)
        else:
            img = image_data
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize for consistency
        img = cv2.resize(img, (self.img_width, self.img_height))
        
        # Calculate ink coverage (how much is drawn)
        binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
        ink_pixels = np.count_nonzero(binary)
        total_pixels = img.shape[0] * img.shape[1]
        coverage = ink_pixels / total_pixels
        
        # Determine if there's actual content
        # At least 2% coverage is considered content
        has_content = coverage > 0.02
        
        # Calculate complexity (number of connected components)
        num_labels, labels = cv2.connectedComponents(binary)
        complexity = num_labels - 1  # Subtract background
        
        return {
            'coverage': round(float(coverage), 4),
            'has_content': has_content,
            'ink_pixels': int(ink_pixels),
            'total_pixels': int(total_pixels),
            'complexity': int(complexity)
        }
    
    def batch_predict(self, image_list):
        """
        Predict multiple images at once (batch prediction)
        More efficient than predicting one by one
        
        Args:
            image_list: List of images to predict
            
        Returns:
            List of prediction dictionaries
        """
        if not self.model_loaded or self.model is None:
            # Fall back to individual mock predictions
            return [self._mock_predict(self.preprocess_image(img)) 
                    for img in image_list]
        
        try:
            # Preprocess all images
            processed_images = np.vstack([
                self.preprocess_image(img) for img in image_list
            ])
            
            # Batch prediction
            predictions = self.model.predict(processed_images, verbose=0)
            
            # Process results
            results = []
            for pred in predictions:
                predicted_class = int(np.argmax(pred))
                confidence = float(pred[predicted_class])
                
                top_3_indices = np.argsort(pred)[-3:][::-1]
                top_3_predictions = [
                    {
                        'class': int(idx),
                        'confidence': float(pred[idx]),
                        'letter': self.class_names[idx] if idx < len(self.class_names) else f"class_{idx}"
                    }
                    for idx in top_3_indices
                ]
                
                results.append({
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'top_3': top_3_predictions,
                    'model_mode': 'trained'
                })
            
            return results
            
        except Exception as e:
            print(f"Error during batch prediction: {e}")
            return [self._mock_predict(self.preprocess_image(img)) 
                    for img in image_list]


# Test function
def test_model():
    """
    Test the model with a sample or mock image
    """
    print("\n" + "=" * 60)
    print("Testing Sinhala Handwriting Model")
    print("=" * 60 + "\n")
    
    # Initialize model
    model = SinhalaHandwritingModel()
    
    # Create a test image (mock handwriting)
    test_image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
    
    # Add some "handwriting" strokes
    cv2.line(test_image, (30, 30), (90, 90), 255, 3)
    cv2.circle(test_image, (64, 64), 20, 255, 2)
    
    print("Testing prediction...")
    result = model.predict(test_image)
    
    print(f"\nPrediction Results:")
    print(f"  Predicted Class: {result['predicted_class']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Model Mode: {result.get('model_mode', 'unknown')}")
    
    if 'top_3' in result:
        print(f"\n  Top 3 Predictions:")
        for i, pred in enumerate(result['top_3'], 1):
            print(f"    {i}. Class {pred['class']}: {pred['confidence']:.2%}")
    
    print("\nTesting score calculation...")
    score_result = model.calculate_score(test_image, correct_class=0)
    
    print(f"\nScore Results:")
    print(f"  Score: {score_result['score']}/100")
    print(f"  Is Correct: {score_result['is_correct']}")
    print(f"  Confidence: {score_result['confidence']:.2%}")
    print(f"  Quality - Has Content: {score_result['quality']['has_content']}")
    print(f"  Quality - Coverage: {score_result['quality']['coverage']:.2%}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run test when script is executed directly
    test_model()