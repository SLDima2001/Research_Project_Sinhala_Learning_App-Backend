"""
Sinhala Handwriting Recognition - Model Testing & Validation Utility
Tests the trained model and provides performance metrics
"""

import numpy as np
import cv2
import os
from pathlib import Path
import json
from sinhala_model import SinhalaHandwritingModel
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import seaborn as sns

class ModelTester:
    def __init__(self, model_path='models/sinhala_model.keras', dataset_path='../dataset/test'):
        """
        Initialize the model tester
        
        Args:
            model_path: Path to trained model
            dataset_path: Path to test dataset
        """
        self.model = SinhalaHandwritingModel(model_path)
        self.dataset_path = Path(dataset_path)
        self.test_images = []
        self.test_labels = []
        self.predictions = []
        
    def load_test_dataset(self):
        """Load test dataset"""
        print("=" * 70)
        print("LOADING TEST DATASET")
        print("=" * 70)
        
        if not self.dataset_path.exists():
            print(f"⚠ Test dataset not found at: {self.dataset_path}")
            print("Using training dataset instead...")
            self.dataset_path = Path("../dataset/train")
        
        class_folders = sorted([d for d in self.dataset_path.iterdir() if d.is_dir()],
                              key=lambda x: int(x.name) if x.name.isdigit() else x.name)
        
        print(f"[OK] Found {len(class_folders)} classes")
        
        total_loaded = 0
        for class_idx, class_folder in enumerate(class_folders):
            image_files = list(class_folder.glob("*.png")) + \
                         list(class_folder.glob("*.jpg")) + \
                         list(class_folder.glob("*.jpeg"))
            
            # Load only first 5 images per class for quick testing
            for img_path in image_files[:5]:
                try:
                    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        self.test_images.append(img)
                        self.test_labels.append(class_idx)
                        total_loaded += 1
                except:
                    continue
        
        print(f"[OK] Loaded {total_loaded} test images")
        print(f"{'=' * 70}\n")
        
        return len(self.test_images) > 0
    
    def test_single_image(self, image_path):
        """Test prediction on a single image"""
        print("=" * 70)
        print("TESTING SINGLE IMAGE")
        print("=" * 70)
        
        if not os.path.exists(image_path):
            print(f"[ERROR] Image not found: {image_path}")
            return
        
        print(f"\nImage: {image_path}")
        
        result = self.model.predict(image_path)
        
        print(f"\nPrediction Results:")
        print(f"  Predicted Class: {result['predicted_class']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Model Mode: {result.get('model_mode', 'unknown')}")
        
        if 'top_3' in result:
            print(f"\n  Top 3 Predictions:")
            for i, pred in enumerate(result['top_3'], 1):
                print(f"    {i}. Class {pred['class']}: {pred['confidence']:.2%}")
        
        print(f"\n{'=' * 70}\n")
    
    def batch_test(self):
        """Test model on batch of images"""
        print("=" * 70)
        print("BATCH TESTING")
        print("=" * 70)
        
        if not self.test_images:
            print("�� No test images loaded")
            return
        
        print(f"\nTesting {len(self.test_images)} images...")
        
        self.predictions = []
        for idx, img in enumerate(self.test_images):
            if (idx + 1) % max(1, len(self.test_images) // 10) == 0:
                print(f"  Progress: {idx + 1}/{len(self.test_images)}")
            
            result = self.model.predict(img)
            self.predictions.append(result['predicted_class'])
        
        # Calculate accuracy
        accuracy = accuracy_score(self.test_labels, self.predictions)
        
        print(f"\n[OK] Batch testing completed!")
        print(f"  Accuracy: {accuracy * 100:.2f}%")
        print(f"  Correct: {sum(np.array(self.predictions) == np.array(self.test_labels))}/{len(self.test_labels)}")
        print(f"\n{'=' * 70}\n")
        
        return accuracy
    
    def generate_confusion_matrix(self, save_path='models/confusion_matrix.png'):
        """Generate and save confusion matrix"""
        if not self.predictions:
            print("[ERROR] No predictions available. Run batch_test() first.")
            return
        
        print("Generating confusion matrix...")
        
        # Get unique classes
        unique_classes = sorted(set(self.test_labels + self.predictions))
        
        # Calculate confusion matrix
        cm = confusion_matrix(self.test_labels, self.predictions, labels=unique_classes)
        
        # Plot
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', cbar=True)
        plt.title('Confusion Matrix - Sinhala Handwriting Recognition')
        plt.xlabel('Predicted Class')
        plt.ylabel('True Class')
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"[OK] Confusion matrix saved to: {save_path}")
        plt.close()
    
    def generate_classification_report(self):
        """Generate classification report"""
        if not self.predictions:
            print("[ERROR] No predictions available. Run batch_test() first.")
            return
        
        print("\n" + "=" * 70)
        print("CLASSIFICATION REPORT")
        print("=" * 70 + "\n")
        
        report = classification_report(self.test_labels, self.predictions, 
                                      output_dict=False, zero_division=0)
        print(report)
        
        # Save report
        report_path = 'models/classification_report.txt'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\n[OK] Report saved to: {report_path}")
    
    def test_model_info(self):
        """Test and display model information"""
        print("=" * 70)
        print("MODEL INFORMATION")
        print("=" * 70)
        
        info_path = 'models/sinhala_model_info.json'
        
        if not os.path.exists(info_path):
            print(f"[ERROR] Model info file not found: {info_path}")
            return
        
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        
        print(f"\n[OK] Model Information:")
        print(f"  Number of Classes: {info.get('num_classes', 'N/A')}")
        print(f"  Image Size: {info.get('img_width', 'N/A')}x{info.get('img_height', 'N/A')}")
        print(f"  Total Parameters: {info.get('total_parameters', 'N/A'):,}")
        print(f"  Architecture: {info.get('model_architecture', 'N/A')}")
        print(f"  Trained On: {info.get('trained_on', 'N/A')}")
        print(f"  Classes: {len(info.get('class_names', []))} loaded")
        
        print(f"\n{'=' * 70}\n")
    
    def test_preprocessing(self, image_path):
        """Test image preprocessing"""
        print("=" * 70)
        print("TESTING IMAGE PREPROCESSING")
        print("=" * 70)
        
        if not os.path.exists(image_path):
            print(f"[ERROR] Image not found: {image_path}")
            return
        
        print(f"\nImage: {image_path}")
        
        # Load original
        original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        print(f"  Original shape: {original.shape}")
        print(f"  Original dtype: {original.dtype}")
        print(f"  Original range: [{original.min()}, {original.max()}]")
        
        # Preprocess
        processed = self.model.preprocess_image(image_path)
        print(f"\n  Processed shape: {processed.shape}")
        print(f"  Processed dtype: {processed.dtype}")
        print(f"  Processed range: [{processed.min():.3f}, {processed.max():.3f}]")
        
        # Visualize
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        
        axes[0].imshow(original, cmap='gray')
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        axes[1].imshow(processed[0, :, :, 0], cmap='gray')
        axes[1].set_title('Preprocessed Image')
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.savefig('models/preprocessing_test.png', dpi=100, bbox_inches='tight')
        print(f"\n[OK] Preprocessing visualization saved to: models/preprocessing_test.png")
        plt.close()
        
        print(f"\n{'=' * 70}\n")


def main():
    """Main testing pipeline"""
    print("\n" + "=" * 70)
    print("SINHALA HANDWRITING RECOGNITION - MODEL TESTING")
    print("=" * 70 + "\n")
    
    # Initialize tester
    tester = ModelTester()
    
    # Test 1: Model information
    tester.test_model_info()
    
    # Test 2: Load test dataset
    if tester.load_test_dataset():
        # Test 3: Batch testing
        accuracy = tester.batch_test()
        
        # Test 4: Generate reports
        tester.generate_classification_report()
        tester.generate_confusion_matrix()
    
    # Test 5: Test single image (if available)
    test_image_path = '../dataset/train/1/1.png'
    if os.path.exists(test_image_path):
        tester.test_single_image(test_image_path)
        tester.test_preprocessing(test_image_path)
    
    print("=" * 70)
    print("[OK] TESTING COMPLETED!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - models/confusion_matrix.png")
    print("  - models/classification_report.txt")
    print("  - models/preprocessing_test.png")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
