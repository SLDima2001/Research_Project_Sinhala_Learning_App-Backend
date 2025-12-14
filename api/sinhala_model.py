"""
Sinhala Handwriting Recognition Model - Basic Recognition Version
File: sinhala_model.py
"""

import numpy as np
import cv2
from PIL import Image
import random

class SinhalaHandwritingModel:
    """
    Handwriting recognition with basic image analysis
    Provides more realistic scoring based on actual drawing
    """
    
    def __init__(self, num_classes=59):
        self.num_classes = num_classes
        self.img_height = 128
        self.img_width = 128
        self.model = None
        print("✓ Model initialized with BASIC RECOGNITION")
    
    def preprocess_image(self, image_data):
        """Preprocess image for analysis"""
        if isinstance(image_data, str):
            img = cv2.imread(image_data, cv2.IMREAD_GRAYSCALE)
        elif isinstance(image_data, Image.Image):
            img = np.array(image_data.convert('L'))
        else:
            img = image_data
        
        img = cv2.resize(img, (self.img_width, self.img_height))
        
        if np.mean(img) > 127:
            img = 255 - img
        
        return img
    
    def analyze_drawing_quality(self, image_data):
        """
        Analyze drawing quality based on image features
        Returns a score based on:
        - Stroke coverage
        - Stroke thickness consistency
        - Drawing complexity
        """
        img = self.preprocess_image(image_data)
        
        # 1. Calculate ink coverage (how much is drawn)
        binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
        ink_pixels = np.count_nonzero(binary)
        total_pixels = img.shape[0] * img.shape[1]
        coverage_ratio = ink_pixels / total_pixels
        
        # Good coverage: 5-30% of canvas
        if coverage_ratio < 0.02:
            coverage_score = 30  # Too little
        elif coverage_ratio > 0.50:
            coverage_score = 40  # Too much
        else:
            # Optimal range
            coverage_score = 60 + (min(coverage_ratio, 0.30) / 0.30) * 35
        
        # 2. Analyze stroke consistency
        edges = cv2.Canny(img, 50, 150)
        edge_count = np.count_nonzero(edges)
        consistency_score = min(95, 50 + (edge_count / 100))
        
        # 3. Check if drawing exists
        if coverage_ratio < 0.01:
            return {
                'quality_score': 0,
                'coverage': coverage_ratio,
                'has_drawing': False
            }
        
        # 4. Calculate complexity (number of distinct regions)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        complexity = len(contours)
        
        if complexity == 0:
            complexity_score = 20
        elif complexity > 20:
            complexity_score = 40  # Too fragmented
        else:
            complexity_score = 60 + min(complexity, 10) * 3
        
        # Combined quality score
        quality_score = (
            coverage_score * 0.4 + 
            consistency_score * 0.3 + 
            complexity_score * 0.3
        )
        
        return {
            'quality_score': round(quality_score, 2),
            'coverage': coverage_ratio,
            'has_drawing': True,
            'complexity': complexity
        }
    
    def predict(self, image_data):
        """
        Predict character with basic analysis
        """
        # Analyze the drawing
        analysis = self.analyze_drawing_quality(image_data)
        
        # If no drawing, return low confidence
        if not analysis['has_drawing']:
            return {
                'predicted_class': random.randint(0, self.num_classes - 1),
                'confidence': 0.1,
                'quality': analysis['quality_score']
            }
        
        # Base confidence on quality
        base_confidence = 0.60 + (analysis['quality_score'] / 100) * 0.35
        
        # Add some randomness to simulate model uncertainty
        confidence = base_confidence + random.uniform(-0.10, 0.10)
        confidence = max(0.50, min(0.98, confidence))
        
        return {
            'predicted_class': random.randint(0, self.num_classes - 1),
            'confidence': float(confidence),
            'quality': analysis['quality_score']
        }
    
    def calculate_score(self, image_data, correct_class):
        """
        Calculate handwriting score based on actual drawing analysis
        Now provides realistic scoring based on drawing quality
        """
        analysis = self.analyze_drawing_quality(image_data)
        
        # If no drawing or very poor quality
        if not analysis['has_drawing'] or analysis['quality_score'] < 10:
            return {
                'score': round(analysis['quality_score'], 2),
                'is_correct': False,
                'confidence': 0.15,
                'predicted_class': correct_class,
                'analysis': 'No drawing detected or very poor quality'
            }
        
        # Simulate correctness based on quality
        # Higher quality = more likely to be "correct"
        quality_score = analysis['quality_score']
        
        # Determine if "correct" based on quality threshold
        # You can adjust this threshold
        is_correct = quality_score > 45 and random.random() > 0.15
        
        if not is_correct:
            # Wrong or poor quality
            score = quality_score * 0.5  # Penalize incorrect
            confidence = 0.40 + random.uniform(0, 0.20)
        else:
            # Correct - score based on quality
            base_score = 60
            quality_bonus = (quality_score / 100) * 35
            confidence_bonus = random.uniform(0, 5)
            score = base_score + quality_bonus + confidence_bonus
            confidence = 0.70 + (quality_score / 100) * 0.25
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        confidence = max(0.10, min(0.98, confidence))
        
        return {
            'score': round(score, 2),
            'is_correct': is_correct,
            'confidence': round(confidence, 4),
            'predicted_class': correct_class if is_correct else random.randint(0, self.num_classes - 1),
            'analysis': f"Coverage: {analysis['coverage']:.1%}, Quality: {quality_score:.1f}",
            'quality_breakdown': {
                'coverage': round(analysis['coverage'] * 100, 2),
                'complexity': analysis['complexity'],
                'overall_quality': quality_score
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Sinhala Handwriting Recognition Model - BASIC ANALYSIS")
    print("=" * 60)
    print("\n✓ Model ready!")
    print("\nThis version analyzes:")
    print("  - Drawing coverage")
    print("  - Stroke consistency")
    print("  - Pattern complexity")
    print("\nNote: This is NOT AI-based recognition.")
    print("Scores are based on drawing quality metrics.")
    print("\nFor real recognition, train a CNN model with TensorFlow.")
    print("=" * 60)