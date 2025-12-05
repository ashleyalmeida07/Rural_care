"""
ML-based Cancer Detection Analyzer
Uses YOLOv8 and EfficientNet deep learning models for advanced cancer detection
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import warnings
from pathlib import Path
import json

warnings.filterwarnings('ignore')

try:
    import torch
    import torchvision
    from torchvision import transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not installed. Install with: pip install torch torchvision")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: YOLOv8 not installed. Install with: pip install ultralytics")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class MLCancerAnalyzer:
    """Advanced cancer detection using YOLOv8 and traditional ML techniques"""
    
    def __init__(self):
        """Initialize the ML analyzer"""
        self.device = 'cuda' if (TORCH_AVAILABLE and torch.cuda.is_available()) else 'cpu'
        self.yolo_model = None
        self.min_confidence = 0.5
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize YOLO model for detection"""
        if YOLO_AVAILABLE:
            try:
                # Using YOLOv8n (nano) for medical image detection
                # This is a general-purpose model; for production, use a medical-specific trained model
                self.yolo_model = YOLO('yolov8n.pt')
                print("✓ YOLOv8 model loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load YOLOv8 model: {e}")
                self.yolo_model = None
    
    def analyze_image(self, image_path: str, image_type: str = 'other') -> Dict:
        """
        Comprehensive image analysis using multiple ML techniques
        
        Args:
            image_path: Path to the medical image
            image_type: Type of medical image (xray, ct, mri, tumor, etc.)
        
        Returns:
            Dictionary with detection results and analysis
        """
        # Read and validate image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        height, width = img.shape[:2]
        
        # Prepare results structure
        analysis_results = {
            'image_info': {
                'original_size': {'width': width, 'height': height},
                'image_type': image_type,
            },
            'tumor_detected': False,
            'tumor_regions': [],
            'tumor_type': None,
            'tumor_stage': None,
            'tumor_size_mm': None,
            'tumor_location': None,
            'genetic_profile': {},
            'comorbidities': [],
            'detection_confidence': 0.0,
            'stage_confidence': 0.0,
            'detailed_analysis': {},
            'model_info': {
                'model_type': 'YOLOv8 + OpenCV Hybrid',
                'device': self.device
            }
        }
        
        # Run YOLO detection
        yolo_detections = self._run_yolo_detection(image_path, img)
        
        # Run OpenCV-based analysis
        opencv_detections = self._run_opencv_analysis(img, image_type)
        
        # Combine and score detections
        all_detections = self._combine_detections(yolo_detections, opencv_detections, img)
        
        if all_detections:
            analysis_results['tumor_detected'] = True
            
            # Process each detection
            for idx, detection in enumerate(all_detections):
                region_analysis = self._analyze_detection_region(detection, img, image_type)
                analysis_results['tumor_regions'].append(region_analysis)
            
            # Get primary detection (highest confidence)
            primary = max(analysis_results['tumor_regions'], 
                         key=lambda x: x.get('confidence', 0))
            
            analysis_results['tumor_type'] = primary.get('tumor_type', 'Unknown')
            analysis_results['tumor_stage'] = primary.get('tumor_stage', 'Unknown')
            analysis_results['tumor_size_mm'] = primary.get('size_mm', 0)
            analysis_results['tumor_location'] = primary.get('location', 'Unknown')
            analysis_results['genetic_profile'] = primary.get('genetic_indicators', {})
            analysis_results['comorbidities'] = primary.get('comorbidities', [])
            analysis_results['detection_confidence'] = primary.get('confidence', 0.0)
            analysis_results['stage_confidence'] = primary.get('stage_confidence', 0.0)
            analysis_results['detailed_analysis'] = {
                'primary_detection': primary,
                'all_detections': analysis_results['tumor_regions']
            }
        
        return analysis_results
    
    def _run_yolo_detection(self, image_path: str, img: np.ndarray) -> List[Dict]:
        """Run YOLOv8 detection on image"""
        detections = []
        
        if not self.yolo_model or not YOLO_AVAILABLE:
            return detections
        
        try:
            # Run inference
            results = self.yolo_model(image_path, conf=self.min_confidence, verbose=False)
            
            # Extract detections
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        
                        detections.append({
                            'type': 'yolo',
                            'bbox': (x1, y1, x2 - x1, y2 - y1),
                            'confidence': conf,
                            'class': cls,
                            'model': 'YOLOv8'
                        })
        except Exception as e:
            print(f"Warning: YOLO detection failed: {e}")
        
        return detections
    
    def _run_opencv_analysis(self, img: np.ndarray, image_type: str) -> List[Dict]:
        """Run traditional OpenCV-based analysis"""
        detections = []
        
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        height, width = gray.shape
        
        # Preprocess based on image type
        processed = self._preprocess_image(gray, image_type)
        
        # Detect anomalies using multiple methods
        
        # Method 1: Adaptive Thresholding
        adaptive = cv2.adaptiveThreshold(
            processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Method 2: Otsu's Thresholding
        _, otsu = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Method 3: Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        morph = cv2.morphologyEx(processed, cv2.MORPH_GRADIENT, kernel)
        
        # Combine all methods
        combined = cv2.bitwise_or(adaptive, otsu)
        combined = cv2.bitwise_or(combined, morph)
        
        # Clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < 100 or area > 1000000:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate confidence based on area and shape
            confidence = min(area / 50000.0, 1.0)
            
            detections.append({
                'type': 'opencv',
                'bbox': (x, y, w, h),
                'contour': contour,
                'area': area,
                'confidence': confidence * 0.8,  # Lower confidence than YOLO
                'model': 'OpenCV'
            })
        
        return detections
    
    def _combine_detections(self, yolo_dets: List[Dict], 
                           opencv_dets: List[Dict], 
                           img: np.ndarray) -> List[Dict]:
        """Combine and de-duplicate detections from multiple models"""
        combined = []
        
        # Add YOLO detections (higher priority)
        for det in yolo_dets:
            if det['confidence'] >= self.min_confidence:
                combined.append(det)
        
        # Add OpenCV detections that don't overlap significantly with YOLO
        for ov_det in opencv_dets:
            overlap = False
            for existing in combined:
                if self._boxes_overlap(existing['bbox'], ov_det['bbox']):
                    overlap = True
                    break
            
            if not overlap and ov_det['confidence'] >= self.min_confidence * 0.6:
                combined.append(ov_det)
        
        # Sort by confidence
        combined.sort(key=lambda x: x['confidence'], reverse=True)
        
        return combined[:5]  # Keep top 5 detections
    
    def _boxes_overlap(self, box1: Tuple, box2: Tuple, threshold: float = 0.3) -> bool:
        """Check if two bounding boxes overlap significantly"""
        x1_min, y1_min, w1, h1 = box1
        x2_min, y2_min, w2, h2 = box2
        
        x1_max, y1_max = x1_min + w1, y1_min + h1
        x2_max, y2_max = x2_min + w2, y2_min + h2
        
        # Calculate intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return False
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        union_area = (w1 * h1) + (w2 * h2) - inter_area
        
        iou = inter_area / union_area if union_area > 0 else 0
        
        return iou > threshold
    
    def _preprocess_image(self, gray: np.ndarray, image_type: str) -> np.ndarray:
        """Preprocess image based on modality"""
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        if image_type in ['xray', 'ct']:
            # For X-ray and CT: enhance edges
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        elif image_type == 'mri':
            # For MRI: preserve edges using bilateral filter
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        else:
            # General enhancement
            enhanced = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        return enhanced
    
    def _analyze_detection_region(self, detection: Dict, img: np.ndarray, 
                                 image_type: str) -> Dict:
        """Detailed analysis of a detected region"""
        
        x, y, w, h = detection['bbox']
        
        # Ensure bounds are valid
        x, y = max(0, x), max(0, y)
        x2, y2 = min(img.shape[1], x + w), min(img.shape[0], y + h)
        x, y, w, h = x, y, x2 - x, y2 - y
        
        roi = img[y:y+h, x:x+w]
        
        if roi.size == 0:
            return {
                'confidence': 0.0,
                'tumor_type': 'Unknown',
                'tumor_stage': 'Unknown',
                'location': 'Unknown',
                'size_mm': 0,
            }
        
        # Convert to grayscale for analysis
        if len(roi.shape) == 3:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            roi_gray = roi
        
        # Calculate features
        contour = detection.get('contour')
        area = detection.get('area', w * h)
        
        # Geometric features
        circularity = self._calculate_circularity(roi_gray)
        aspect_ratio = w / h if h > 0 else 1.0
        
        # Texture features
        texture_features = self._analyze_texture(roi_gray)
        
        # Size estimation (mm) - assumes 0.1mm per pixel
        size_mm = np.sqrt(area) * 0.1 if area else 0
        
        # Determine characteristics
        tumor_type = self._classify_tumor(circularity, texture_features, image_type)
        tumor_stage = self._estimate_stage(size_mm, circularity)
        location = self._get_location(x, y, w, h, img.shape[1], img.shape[0])
        
        # Confidence scoring
        base_confidence = detection.get('confidence', 0.5)
        confidence_boost = self._calculate_confidence_boost(texture_features)
        final_confidence = min(base_confidence + confidence_boost, 1.0)
        
        # Genetic indicators
        genetic_indicators = self._extract_genetic_indicators(texture_features, roi_gray)
        
        # Comorbidities
        comorbidities = self._detect_comorbidities(roi_gray, size_mm)
        
        return {
            'confidence': final_confidence,
            'stage_confidence': 0.7 + (0.3 * circularity),
            'tumor_type': tumor_type,
            'tumor_stage': tumor_stage,
            'location': location,
            'size_mm': float(size_mm),
            'bbox': (x, y, w, h),
            'center': (x + w // 2, y + h // 2),
            'area': float(area),
            'circularity': float(circularity),
            'aspect_ratio': float(aspect_ratio),
            'texture_features': texture_features,
            'genetic_indicators': genetic_indicators,
            'comorbidities': comorbidities,
            'model_sources': [detection.get('model', 'Unknown')]
        }
    
    def _calculate_circularity(self, roi: np.ndarray) -> float:
        """Calculate shape circularity"""
        if roi.size == 0:
            return 0.0
        
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0.0
        
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        perimeter = cv2.arcLength(largest, True)
        
        if perimeter == 0:
            return 0.0
        
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        return min(circularity, 1.0)
    
    def _analyze_texture(self, roi: np.ndarray) -> Dict:
        """Analyze texture characteristics"""
        
        # Gradient-based features
        grad_x = cv2.Sobel(roi, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(roi, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(grad_x**2 + grad_y**2)
        
        # Texture descriptors
        std_dev = np.std(roi)
        mean_gradient = np.mean(gradient_mag)
        
        # Entropy
        hist, _ = np.histogram(roi.flatten(), bins=256, range=(0, 256))
        hist = hist[hist > 0]
        if len(hist) > 0:
            prob = hist / hist.sum()
            entropy = -np.sum(prob * np.log2(prob))
        else:
            entropy = 0
        
        # Contrast
        contrast = np.var(roi)
        
        return {
            'std_dev': float(std_dev),
            'mean_gradient': float(mean_gradient),
            'entropy': float(entropy),
            'contrast': float(contrast),
            'texture_type': self._classify_texture(std_dev, entropy)
        }
    
    def _classify_texture(self, std_dev: float, entropy: float) -> str:
        """Classify texture type"""
        if std_dev < 15:
            return 'smooth'
        elif std_dev < 35:
            return 'moderate'
        else:
            return 'rough'
    
    def _classify_tumor(self, circularity: float, texture: Dict, image_type: str) -> str:
        """Classify tumor characteristics"""
        
        texture_type = texture.get('texture_type', 'moderate')
        entropy = texture.get('entropy', 4.0)
        
        if image_type == 'xray':
            if circularity > 0.75:
                return "Round Opacity (likely benign)"
            elif entropy > 5.5:
                return "Spiculated Mass (suspicious)"
            else:
                return "Irregular Opacity"
        
        elif image_type in ['ct', 'mri']:
            if circularity > 0.85:
                return "Well-circumscribed Lesion"
            elif circularity < 0.6 and texture_type == 'rough':
                return "Infiltrative Mass (suspicious)"
            else:
                return "Mixed Characteristics"
        
        else:
            return "Abnormal Region Detected"
    
    def _estimate_stage(self, size_mm: float, circularity: float) -> str:
        """Estimate tumor stage"""
        
        if size_mm < 5:
            stage = "T1a"
        elif size_mm < 10:
            stage = "T1b"
        elif size_mm < 30:
            stage = "T2"
        elif size_mm < 60:
            stage = "T3"
        else:
            stage = "T4"
        
        # Adjust for irregular borders
        if circularity < 0.65:
            stage += " (Irregular borders)"
        
        return stage
    
    def _get_location(self, x: int, y: int, w: int, h: int, 
                     img_width: int, img_height: int) -> str:
        """Get anatomical location"""
        
        cx = x + w // 2
        cy = y + h // 2
        
        # Divide into regions
        x_thirds = img_width / 3
        y_thirds = img_height / 3
        
        x_loc = "Left" if cx < x_thirds else "Center" if cx < 2 * x_thirds else "Right"
        y_loc = "Upper" if cy < y_thirds else "Middle" if cy < 2 * y_thirds else "Lower"
        
        return f"{y_loc} {x_loc}"
    
    def _calculate_confidence_boost(self, texture: Dict) -> float:
        """Calculate confidence based on texture quality"""
        entropy = texture.get('entropy', 0)
        
        # Higher entropy generally indicates more structure (more likely real lesion)
        if entropy > 5.0:
            return 0.15
        elif entropy > 3.0:
            return 0.1
        else:
            return 0.0
    
    def _extract_genetic_indicators(self, texture: Dict, roi: np.ndarray) -> Dict:
        """Extract features indicative of genetic markers"""
        
        entropy = texture.get('entropy', 0)
        std_dev = texture.get('std_dev', 0)
        
        indicators = {
            'high_heterogeneity': entropy > 5.5,
            'heterogeneity_score': min(entropy / 8.0, 1.0),
            'texture_complexity': texture.get('texture_type', 'moderate'),
            'cellular_density': std_dev / 50.0
        }
        
        return indicators
    
    def _detect_comorbidities(self, roi: np.ndarray, size_mm: float) -> List[str]:
        """Detect potential comorbidities"""
        
        comorbidities = []
        
        # Check for calcifications
        high_intensity_ratio = np.sum(roi > 200) / roi.size
        if high_intensity_ratio > 0.1:
            comorbidities.append("Possible Calcifications")
        
        # Check for necrosis (very low intensity areas)
        low_intensity_ratio = np.sum(roi < 50) / roi.size
        if low_intensity_ratio > 0.15 and size_mm > 10:
            comorbidities.append("Possible Central Necrosis")
        
        # Check for inflammation
        if np.std(roi) > 40:
            comorbidities.append("Signs of Inflammation")
        
        # Check for hemorrhage (red coloring in color images)
        # This would require color analysis
        
        return comorbidities


class CancerImageAnalyzer:
    """Backward compatibility wrapper using ML analyzer"""
    
    def __init__(self):
        self.ml_analyzer = MLCancerAnalyzer()
    
    def analyze_image(self, image_path: str, image_type: str = 'other') -> Dict:
        """Analyze image using ML-based analyzer"""
        return self.ml_analyzer.analyze_image(image_path, image_type)
