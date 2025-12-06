from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    supabase_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    class Meta:
        db_table = 'users'


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    current_medications = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Patient Profile - {self.user.username}"
    
    class Meta:
        db_table = 'patient_profiles'


class DoctorProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('general_medicine', 'General Medicine'),
        ('internal_medicine', 'Internal Medicine'),
        ('family_medicine', 'Family Medicine'),
        ('pediatrics', 'Pediatrics'),
        ('surgery', 'General Surgery'),
        ('orthopedics', 'Orthopedics'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('psychiatry', 'Psychiatry'),
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT (Ear, Nose & Throat)'),
        ('gynecology', 'Gynecology & Obstetrics'),
        ('urology', 'Urology'),
        ('nephrology', 'Nephrology'),
        ('gastroenterology', 'Gastroenterology'),
        ('pulmonology', 'Pulmonology'),
        ('endocrinology', 'Endocrinology'),
        ('rheumatology', 'Rheumatology'),
        ('oncology', 'Oncology'),
        ('surgical_oncology', 'Surgical Oncology'),
        ('radiation_oncology', 'Radiation Oncology'),
        ('medical_oncology', 'Medical Oncology'),
        ('pediatric_oncology', 'Pediatric Oncology'),
        ('hematology', 'Hematology'),
        ('radiology', 'Radiology'),
        ('pathology', 'Pathology'),
        ('anesthesiology', 'Anesthesiology'),
        ('emergency_medicine', 'Emergency Medicine'),
        ('critical_care', 'Critical Care Medicine'),
        ('plastic_surgery', 'Plastic Surgery'),
        ('neurosurgery', 'Neurosurgery'),
        ('cardiothoracic_surgery', 'Cardiothoracic Surgery'),
        ('vascular_surgery', 'Vascular Surgery'),
        ('transplant_surgery', 'Transplant Surgery'),
        ('infectious_disease', 'Infectious Disease'),
        ('allergy_immunology', 'Allergy & Immunology'),
        ('geriatrics', 'Geriatrics'),
        ('sports_medicine', 'Sports Medicine'),
        ('physical_medicine', 'Physical Medicine & Rehabilitation'),
        ('occupational_medicine', 'Occupational Medicine'),
        ('preventive_medicine', 'Preventive Medicine'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Basic Information
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Professional Information
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES, null=True, blank=True)
    license_number = models.CharField(max_length=50, unique=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    
    # Qualifications
    medical_degree = models.CharField(max_length=200, null=True, blank=True, help_text="e.g., MBBS, MD, DM")
    additional_qualifications = models.TextField(null=True, blank=True, help_text="Other certifications or qualifications")
    
    # Work Information
    hospital_affiliation = models.CharField(max_length=200, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    
    # Location Information
    clinic_address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, default='India')
    
    # Professional Details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bio = models.TextField(null=True, blank=True, help_text="Brief description about yourself and expertise")
    languages_spoken = models.CharField(max_length=200, null=True, blank=True, help_text="Comma-separated languages")
    
    # Verification & Status
    is_verified = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"Dr. {self.user.username} - {self.specialization}"
    
    class Meta:
        db_table = 'doctor_profiles'


class DoctorKYC(models.Model):
    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('incomplete', 'Incomplete'),
    ]
    
    doctor = models.OneToOneField(DoctorProfile, on_delete=models.CASCADE, related_name='kyc')
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    nationality = models.CharField(max_length=100)
    
    # Contact Information
    personal_email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    residential_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Medical License Information
    license_number_verified = models.CharField(max_length=100)
    license_issuing_authority = models.CharField(max_length=200)
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()
    license_document = models.FileField(upload_to='kyc/licenses/', null=True, blank=True)
    
    # Educational Qualification
    medical_degree = models.CharField(max_length=200)
    medical_university = models.CharField(max_length=200)
    graduation_year = models.IntegerField()
    degree_certificate = models.FileField(upload_to='kyc/degrees/', null=True, blank=True)
    
    # Professional Information
    current_hospital = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=100)
    department_specialty = models.CharField(max_length=100)
    years_of_practice = models.IntegerField()
    employment_document = models.FileField(upload_to='kyc/employment/', null=True, blank=True)
    
    # Identification Documents
    identity_document_type = models.CharField(max_length=50, choices=[('passport', 'Passport'), ('aadhaar', 'Aadhaar'), ('national_id', 'National ID'), ('driving_license', 'Driving License')])
    identity_document_number = models.CharField(max_length=100)
    identity_document_file = models.FileField(upload_to='kyc/identity/', null=True, blank=True)
    
    # Address Verification
    address_proof_type = models.CharField(max_length=50, choices=[('utility_bill', 'Utility Bill'), ('rental_agreement', 'Rental Agreement'), ('property_deed', 'Property Deed'), ('bank_statement', 'Bank Statement')])
    address_proof_file = models.FileField(upload_to='kyc/address_proof/', null=True, blank=True)
    
    # KYC Status
    status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='incomplete')
    rejection_reason = models.TextField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"KYC - Dr. {self.doctor.user.username} ({self.status})"
    
    class Meta:
        db_table = 'doctor_kyc'
        verbose_name = 'Doctor KYC'
        verbose_name_plural = 'Doctor KYCs'


class MedicalRecord(models.Model):
    """Model for storing patient medical records with OCR capabilities"""
    RECORD_TYPE_CHOICES = [
        ('lab_report', 'Laboratory Report'),
        ('radiology', 'Radiology Report'),
        ('pathology', 'Pathology Report'),
        ('biopsy', 'Biopsy Report'),
        ('blood_test', 'Blood Test'),
        ('genetic_test', 'Genetic Test'),
        ('prescription', 'Prescription'),
        ('discharge_summary', 'Discharge Summary'),
        ('consultation', 'Consultation Notes'),
        ('other', 'Other'),
    ]
    
    OCR_STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    
    # Record Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES, default='other')
    file = models.FileField(upload_to='medical_records/%Y/%m/%d/')
    file_size = models.IntegerField(null=True, blank=True)
    
    # OCR Related Fields
    extracted_text = models.TextField(blank=True, null=True)
    extracted_data = models.JSONField(blank=True, null=True)  # Structured data extracted from OCR
    ocr_status = models.CharField(max_length=20, choices=OCR_STATUS_CHOICES, default='processing')
    ocr_confidence = models.FloatField(null=True, blank=True)  # OCR confidence score (0-100)
    
    # Metadata
    report_date = models.DateField(null=True, blank=True)
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.patient.username}"
    
    class Meta:
        db_table = 'medical_records'
        ordering = ['-created_at']
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
