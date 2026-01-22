"""
Cancer Image Analyzer
Provides either ML-based or lightweight analysis depending on available libraries
"""

from django.conf import settings
import os

# Check if ML features are enabled
ML_FEATURES_ENABLED = getattr(settings, 'ML_FEATURES_ENABLED', True)

# Check if OpenCV is available
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

if ML_FEATURES_ENABLED and CV2_AVAILABLE:
    try:
        from .ml_analyzer import CancerImageAnalyzer as MLCancerAnalyzer
        from .ml_analyzer import MLCancerAnalyzer as _MLCancerAnalyzer
        ML_AVAILABLE = True
    except ImportError:
        ML_AVAILABLE = False
else:
    ML_AVAILABLE = False


class LightweightCancerAnalyzer:
    """
    Lightweight cancer image analyzer that works without heavy ML libraries.
    Uses basic image analysis and returns placeholder results.
    For full ML analysis, ensure ML_FEATURES_ENABLED=True and install full requirements.
    """
    
    def __init__(self):
        self.device = 'cpu'
        self.initialized = True
    
    def analyze_image(self, image_path: str, image_type: str = 'other') -> dict:
        """
        Perform basic image analysis without ML models.
        Returns a structure compatible with the full analyzer but with placeholder values.
        """
        # Try to get basic image info
        width, height = 800, 600  # default
        
        if CV2_AVAILABLE:
            try:
                img = cv2.imread(image_path)
                if img is not None:
                    height, width = img.shape[:2]
            except:
                pass
        
        return {
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
            'detailed_analysis': {
                'note': 'ML features are disabled. Enable ML_FEATURES_ENABLED for full analysis.',
                'ml_available': False
            },
            'annotated_image': None,
            'model_info': {
                'model_type': 'Lightweight (ML Disabled)',
                'device': 'cpu'
            }
        }


# Export the appropriate analyzer based on availability
if ML_AVAILABLE:
    CancerImageAnalyzer = MLCancerAnalyzer
    MLCancerAnalyzer = _MLCancerAnalyzer
else:
    CancerImageAnalyzer = LightweightCancerAnalyzer
    MLCancerAnalyzer = LightweightCancerAnalyzer

__all__ = ['CancerImageAnalyzer', 'MLCancerAnalyzer']
