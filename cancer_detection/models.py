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


class PersonalizedTreatmentPlan(models.Model):
    """
    Model for storing AI-generated personalized cancer treatment plans.
    Integrates patient profile, tumor analysis, genetic profile, and treatment recommendations.
    """
    
    PLAN_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Oncologist Review'),
        ('approved', 'Approved by Oncologist'),
        ('active', 'Active/In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treatment_plans')
    analysis = models.ForeignKey(CancerImageAnalysis, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='treatment_plans')
    
    # Plan Identification
    plan_name = models.CharField(max_length=200, null=True, blank=True)
    cancer_type = models.CharField(max_length=100)
    cancer_stage = models.CharField(max_length=50)
    
    # Patient Profile Data
    patient_profile = models.JSONField(default=dict)  # Age, comorbidities, performance status, etc.
    
    # Tumor Characteristics
    tumor_analysis = models.JSONField(default=dict)  # Size, grade, location, metastasis, etc.
    
    # Genetic & Biomarker Profile
    genetic_profile = models.JSONField(default=dict)  # Mutations, biomarkers, immunoprofile
    
    # Treatment Recommendations
    primary_treatments = models.JSONField(default=list)  # Primary treatment modalities
    adjuvant_treatments = models.JSONField(default=list)  # Adjuvant therapy options
    targeted_therapies = models.JSONField(default=list)  # Targeted therapy eligibility
    side_effects = models.JSONField(default=list)  # Expected side effects
    
    # Outcome Predictions
    predicted_5yr_survival = models.FloatField(null=True, blank=True)  # 5-year survival estimate
    remission_probability = models.FloatField(null=True, blank=True)  # % chance of remission
    quality_of_life_score = models.IntegerField(null=True, blank=True)  # QOL impact (0-100)
    
    # Monitoring & Follow-up
    monitoring_plan = models.JSONField(default=dict)  # Surveillance schedule
    expected_milestones = models.JSONField(default=list)  # Key treatment milestones
    
    # Patient Journey & Decision Support
    treatment_pathway = models.JSONField(default=dict)  # Phases, timeline, decision points
    clinical_trials = models.JSONField(default=list)  # Relevant clinical trial options
    
    # Contraindications & Considerations
    contraindications = models.JSONField(default=list)  # Drugs/treatments to avoid
    special_considerations = models.TextField(null=True, blank=True)  # Additional notes
    
    # Status & Review
    status = models.CharField(max_length=20, choices=PLAN_STATUS_CHOICES, default='draft')
    oncologist_notes = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='reviewed_plans')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review_date = models.DateTimeField(null=True, blank=True)
    activated_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'personalized_treatment_plans'
        ordering = ['-created_at']
        verbose_name = 'Personalized Treatment Plan'
        verbose_name_plural = 'Personalized Treatment Plans'
    
    def __str__(self):
        return f"Treatment Plan - {self.patient.username} - {self.cancer_type} Stage {self.cancer_stage}"
    
    @property
    def is_pending_review(self):
        return self.status == 'pending_review'
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_active(self):
        return self.status == 'active'
