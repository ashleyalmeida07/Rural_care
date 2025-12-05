from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class CancerImageAnalysis(models.Model):
    """Model to store uploaded images and their analysis results"""
    
    IMAGE_TYPE_CHOICES = [
        ('xray', 'X-Ray Scan'),
        ('ct', 'CT Scan'),
        ('mri', 'MRI Scan'),
        ('tumor', 'Tumor Image'),
        ('biopsy', 'Biopsy Image'),
        ('ultrasound', 'Ultrasound'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cancer_analyses')
    image = models.ImageField(upload_to='cancer_images/%Y/%m/%d/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='other')
    original_filename = models.CharField(max_length=255)
    
    # Analysis Results
    tumor_detected = models.BooleanField(default=False)
    tumor_type = models.CharField(max_length=100, null=True, blank=True)
    tumor_stage = models.CharField(max_length=50, null=True, blank=True)
    tumor_size_mm = models.FloatField(null=True, blank=True)
    tumor_location = models.CharField(max_length=200, null=True, blank=True)
    
    # Genetic Profile Indicators
    genetic_profile = models.JSONField(default=dict, blank=True)
    
    # Comorbidities
    comorbidities = models.JSONField(default=list, blank=True)
    
    # Detailed Analysis Data
    analysis_data = models.JSONField(default=dict, blank=True)  # Stores all OpenCV analysis results
    
    # Confidence scores
    detection_confidence = models.FloatField(default=0.0)
    stage_confidence = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'cancer_image_analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis {self.id} - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
