"""
OpenCV-based Cancer Detection Analyzer
Uses traditional computer vision techniques for image analysis
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import math


class CancerImageAnalyzer:
    """Analyzes medical images using OpenCV for cancer detection"""
    
    def __init__(self):
        self.min_tumor_area = 100  # Minimum area in pixels to consider as potential tumor
        self.max_tumor_area = 1000000  # Maximum area threshold
    
    def analyze_image(self, image_path: str, image_type: str = 'other') -> Dict:
        """
        Main analysis function that processes the image and returns comprehensive results
        
        Args:
            image_path: Path to the image file
            image_type: Type of medical image (xray, ct, mri, tumor, etc.)
        
        Returns:
            Dictionary containing all analysis results
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        original_shape = img.shape
        height, width = original_shape[:2]
        
        # Preprocess image
        processed_img = self._preprocess_image(img, image_type)
        
        # Detect potential tumor regions
        tumor_regions = self._detect_tumor_regions(processed_img)
        
        # Analyze detected regions
        analysis_results = {
            'image_info': {
                'original_size': {'width': width, 'height': height},
                'image_type': image_type,
            },
            'tumor_detected': len(tumor_regions) > 0,
            'tumor_regions': [],
            'tumor_type': None,
            'tumor_stage': None,
            'tumor_size_mm': None,
            'tumor_location': None,
            'genetic_profile': {},
            'comorbidities': [],
            'detection_confidence': 0.0,
            'stage_confidence': 0.0,
            'detailed_analysis': {}
        }
        
        if tumor_regions:
            # Analyze each detected region
            for idx, region in enumerate(tumor_regions):
                region_analysis = self._analyze_region(region, processed_img, img)
                analysis_results['tumor_regions'].append(region_analysis)
            
            # Determine overall tumor characteristics
            primary_region = max(analysis_results['tumor_regions'], 
                               key=lambda x: x.get('area', 0))
            
            analysis_results['tumor_type'] = self._classify_tumor_type(primary_region, image_type)
            analysis_results['tumor_stage'] = self._determine_stage(primary_region)
            analysis_results['tumor_size_mm'] = primary_region.get('estimated_size_mm', 0)
            analysis_results['tumor_location'] = self._determine_location(primary_region, width, height)
            analysis_results['genetic_profile'] = self._analyze_genetic_indicators(primary_region)
            analysis_results['comorbidities'] = self._detect_comorbidities(primary_region, processed_img)
            analysis_results['detection_confidence'] = self._calculate_confidence(primary_region)
            analysis_results['stage_confidence'] = self._calculate_stage_confidence(primary_region)
            analysis_results['detailed_analysis'] = primary_region
        
        return analysis_results
    
    def _preprocess_image(self, img: np.ndarray, image_type: str) -> np.ndarray:
        """Preprocess image based on type"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply different preprocessing based on image type
        if image_type in ['xray', 'ct']:
            # Enhance contrast for X-ray and CT scans
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            # Apply Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
        elif image_type == 'mri':
            # For MRI, apply bilateral filter to preserve edges
            gray = cv2.bilateralFilter(gray, 9, 75, 75)
        else:
            # General preprocessing
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return gray
    
    def _detect_tumor_regions(self, img: np.ndarray) -> List[Dict]:
        """Detect potential tumor regions using various techniques"""
        regions = []
        
        # Method 1: Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Method 2: Otsu's thresholding
        _, otsu_thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Method 3: Canny edge detection
        edges = cv2.Canny(img, 50, 150)
        
        # Combine methods
        combined = cv2.bitwise_or(adaptive_thresh, otsu_thresh)
        combined = cv2.bitwise_or(combined, edges)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_tumor_area < area < self.max_tumor_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                regions.append({
                    'contour': contour,
                    'area': area,
                    'bbox': (x, y, w, h),
                    'mask': np.zeros(img.shape, dtype=np.uint8)
                })
        
        # Sort by area (largest first)
        regions.sort(key=lambda x: x['area'], reverse=True)
        
        # Return top 5 regions
        return regions[:5]
    
    def _analyze_region(self, region: Dict, processed_img: np.ndarray, original_img: np.ndarray) -> Dict:
        """Perform detailed analysis on a detected region"""
        contour = region['contour']
        x, y, w, h = region['bbox']
        
        # Extract region of interest
        roi = processed_img[y:y+h, x:x+w]
        roi_color = original_img[y:y+h, x:x+w] if len(original_img.shape) == 3 else None
        
        # Calculate geometric features
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Circularity (4π*area/perimeter²)
        circularity = (4 * math.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        
        # Aspect ratio
        aspect_ratio = float(w) / h if h > 0 else 0
        
        # Extent (ratio of contour area to bounding box area)
        extent = area / (w * h) if (w * h) > 0 else 0
        
        # Solidity (ratio of contour area to convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Texture analysis using Local Binary Pattern (LBP-like)
        texture_features = self._analyze_texture(roi)
        
        # Color analysis (if color image)
        color_features = self._analyze_color(roi_color) if roi_color is not None else {}
        
        # Intensity analysis
        intensity_stats = self._analyze_intensity(roi)
        
        # Estimate size in mm (assuming average pixel size)
        # This is a rough estimate - in real scenarios, DICOM metadata would provide this
        pixel_to_mm = 0.1  # Default assumption: 0.1mm per pixel
        estimated_size_mm = math.sqrt(area) * pixel_to_mm
        
        return {
            'area': area,
            'perimeter': perimeter,
            'circularity': circularity,
            'aspect_ratio': aspect_ratio,
            'extent': extent,
            'solidity': solidity,
            'texture_features': texture_features,
            'color_features': color_features,
            'intensity_stats': intensity_stats,
            'estimated_size_mm': estimated_size_mm,
            'bbox': region['bbox'],
            'center': (x + w//2, y + h//2)
        }
    
    def _analyze_texture(self, roi: np.ndarray) -> Dict:
        """Analyze texture features of the region"""
        if roi.size == 0:
            return {}
        
        # Calculate gradient magnitude (texture indicator)
        grad_x = cv2.Sobel(roi, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(roi, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate standard deviation (texture roughness)
        std_dev = np.std(roi)
        mean_gradient = np.mean(gradient_magnitude)
        
        # Calculate entropy (texture complexity)
        hist, _ = np.histogram(roi.flatten(), bins=256, range=(0, 256))
        hist = hist[hist > 0]  # Remove zeros
        prob = hist / hist.sum()
        entropy = -np.sum(prob * np.log2(prob))
        
        return {
            'std_dev': float(std_dev),
            'mean_gradient': float(mean_gradient),
            'entropy': float(entropy),
            'texture_type': 'smooth' if std_dev < 20 else 'moderate' if std_dev < 40 else 'rough'
        }
    
    def _analyze_color(self, roi: np.ndarray) -> Dict:
        """Analyze color features (for color images)"""
        if roi is None or roi.size == 0:
            return {}
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Calculate mean values
        mean_h = np.mean(hsv[:, :, 0])
        mean_s = np.mean(hsv[:, :, 1])
        mean_v = np.mean(hsv[:, :, 2])
        
        # Calculate color variance
        var_h = np.var(hsv[:, :, 0])
        var_s = np.var(hsv[:, :, 1])
        var_v = np.var(hsv[:, :, 2])
        
        return {
            'mean_hue': float(mean_h),
            'mean_saturation': float(mean_s),
            'mean_value': float(mean_v),
            'color_variance': {
                'hue': float(var_h),
                'saturation': float(var_s),
                'value': float(var_v)
            }
        }
    
    def _analyze_intensity(self, roi: np.ndarray) -> Dict:
        """Analyze intensity statistics"""
        if roi.size == 0:
            return {}
        
        mean_intensity = np.mean(roi)
        std_intensity = np.std(roi)
        min_intensity = np.min(roi)
        max_intensity = np.max(roi)
        
        return {
            'mean': float(mean_intensity),
            'std': float(std_intensity),
            'min': float(min_intensity),
            'max': float(max_intensity),
            'range': float(max_intensity - min_intensity)
        }
    
    def _classify_tumor_type(self, region: Dict, image_type: str) -> str:
        """Classify tumor type based on features"""
        circularity = region.get('circularity', 0)
        aspect_ratio = region.get('aspect_ratio', 1)
        texture = region.get('texture_features', {})
        texture_type = texture.get('texture_type', 'moderate')
        solidity = region.get('solidity', 0)
        
        # Rule-based classification
        if image_type == 'xray':
            if circularity > 0.7 and solidity > 0.9:
                return "Benign Nodule (likely)"
            elif circularity < 0.5 and texture_type == 'rough':
                return "Malignant Mass (suspicious)"
            else:
                return "Uncertain - Requires Further Analysis"
        
        elif image_type in ['ct', 'mri']:
            if aspect_ratio > 2.0 or aspect_ratio < 0.5:
                return "Irregular Mass (suspicious)"
            elif circularity > 0.8 and solidity > 0.95:
                return "Well-defined Lesion (possibly benign)"
            else:
                return "Complex Lesion - Further Evaluation Needed"
        
        elif image_type == 'tumor':
            if texture_type == 'rough' and solidity < 0.85:
                return "Infiltrative Tumor (suspicious)"
            elif circularity > 0.75:
                return "Encapsulated Tumor (possibly benign)"
            else:
                return "Mixed Characteristics - Biopsy Recommended"
        
        else:
            # General classification
            if circularity > 0.8:
                return "Round/Spherical Lesion"
            elif aspect_ratio > 1.5:
                return "Elongated Lesion"
            else:
                return "Irregular Lesion"
    
    def _determine_stage(self, region: Dict) -> str:
        """Determine tumor stage based on size and characteristics"""
        size_mm = region.get('estimated_size_mm', 0)
        area = region.get('area', 0)
        circularity = region.get('circularity', 0)
        solidity = region.get('solidity', 0)
        
        # Stage determination based on size (TNM staging simplified)
        if size_mm < 5:
            stage = "T1 (Early Stage)"
        elif size_mm < 20:
            stage = "T2 (Early-Mid Stage)"
        elif size_mm < 50:
            stage = "T3 (Mid Stage)"
        else:
            stage = "T4 (Advanced Stage)"
        
        # Adjust based on shape irregularity
        if circularity < 0.5 or solidity < 0.7:
            stage += " - Irregular Borders (Higher Risk)"
        
        return stage
    
    def _determine_location(self, region: Dict, img_width: int, img_height: int) -> str:
        """Determine approximate location in image"""
        center_x, center_y = region.get('center', (0, 0))
        
        # Divide image into regions
        x_region = "Left" if center_x < img_width / 3 else "Center" if center_x < 2 * img_width / 3 else "Right"
        y_region = "Upper" if center_y < img_height / 3 else "Middle" if center_y < 2 * img_height / 3 else "Lower"
        
        return f"{y_region} {x_region} Region"
    
    def _analyze_genetic_indicators(self, region: Dict) -> Dict:
        """Analyze features that might indicate genetic markers"""
        texture = region.get('texture_features', {})
        intensity = region.get('intensity_stats', {})
        
        indicators = {}
        
        # High entropy might indicate genetic heterogeneity
        entropy = texture.get('entropy', 0)
        if entropy > 6.0:
            indicators['high_heterogeneity'] = True
            indicators['heterogeneity_score'] = min(entropy / 8.0, 1.0)
        else:
            indicators['high_heterogeneity'] = False
            indicators['heterogeneity_score'] = entropy / 8.0
        
        # Irregular borders might indicate aggressive behavior
        circularity = region.get('circularity', 0)
        if circularity < 0.6:
            indicators['irregular_borders'] = True
            indicators['aggression_risk'] = 1.0 - circularity
        else:
            indicators['irregular_borders'] = False
            indicators['aggression_risk'] = 0.0
        
        # Texture patterns
        std_dev = texture.get('std_dev', 0)
        if std_dev > 40:
            indicators['texture_complexity'] = 'high'
        elif std_dev > 20:
            indicators['texture_complexity'] = 'moderate'
        else:
            indicators['texture_complexity'] = 'low'
        
        return indicators
    
    def _detect_comorbidities(self, region: Dict, processed_img: np.ndarray) -> List[str]:
        """Detect potential comorbidities based on image characteristics"""
        comorbidities = []
        
        # Analyze surrounding tissue
        x, y, w, h = region.get('bbox', (0, 0, 0, 0))
        
        # Check for calcifications (bright spots)
        intensity = region.get('intensity_stats', {})
        max_intensity = intensity.get('max', 0)
        if max_intensity > 200:
            comorbidities.append("Possible Calcifications Detected")
        
        # Check for inflammation (texture changes in surrounding area)
        texture = region.get('texture_features', {})
        if texture.get('texture_type') == 'rough':
            comorbidities.append("Inflammatory Changes Possible")
        
        # Check for vascular involvement (linear structures)
        # This is simplified - real analysis would use more sophisticated methods
        circularity = region.get('circularity', 0)
        if circularity < 0.5:
            comorbidities.append("Possible Vascular Involvement")
        
        return comorbidities
    
    def _calculate_confidence(self, region: Dict) -> float:
        """Calculate detection confidence score"""
        area = region.get('area', 0)
        circularity = region.get('circularity', 0)
        solidity = region.get('solidity', 0)
        texture = region.get('texture_features', {})
        
        # Base confidence on area (larger = more confident if within reasonable range)
        area_score = min(area / 10000, 1.0) if area < 100000 else 0.8
        
        # Shape consistency
        shape_score = (circularity + solidity) / 2
        
        # Texture clarity
        std_dev = texture.get('std_dev', 0)
        texture_score = 1.0 - min(abs(std_dev - 30) / 50, 1.0)  # Optimal around 30
        
        # Combined confidence
        confidence = (area_score * 0.4 + shape_score * 0.3 + texture_score * 0.3)
        
        return min(confidence, 1.0)
    
    def _calculate_stage_confidence(self, region: Dict) -> float:
        """Calculate confidence in stage determination"""
        size_mm = region.get('estimated_size_mm', 0)
        
        # Higher confidence for larger, well-defined tumors
        if size_mm > 10:
            return 0.8
        elif size_mm > 5:
            return 0.6
        else:
            return 0.4

