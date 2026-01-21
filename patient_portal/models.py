from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

User = get_user_model()


class PatientSymptomLog(models.Model):
    """
    Patient-reported symptoms logged daily or weekly.
    Cannot be edited after submission.
    """
    
    SEVERITY_CHOICES = [
        (1, 'Very Mild'),
        (2, 'Mild'),
        (3, 'Moderate'),
        (4, 'Severe'),
        (5, 'Very Severe'),
    ]
    
    FREQUENCY_CHOICES = [
        ('rarely', 'Rarely'),
        ('sometimes', 'Sometimes'),
        ('often', 'Often'),
        ('always', 'Always'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='symptom_logs')
    treatment_plan = models.ForeignKey('cancer_detection.PersonalizedTreatmentPlan',
                                        on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='patient_symptom_logs')
    
    # Log date
    log_date = models.DateField(default=timezone.now)
    log_type = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly')], default='daily')
    
    # Common oncology symptoms (severity 1-5)
    fatigue = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    pain = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    pain_location = models.CharField(max_length=200, null=True, blank=True)
    nausea = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    vomiting = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    appetite_loss = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    weight_change = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Lost 2 kg"
    sleep_problems = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    shortness_of_breath = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    diarrhea = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    constipation = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    mouth_sores = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    skin_changes = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    numbness_tingling = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    fever = models.BooleanField(default=False)
    fever_temperature = models.FloatField(null=True, blank=True)  # in Celsius
    
    # Emotional/Mental symptoms
    anxiety = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    depression = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    confusion = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    
    # Hair loss (specific tracking)
    hair_loss = models.CharField(max_length=50, choices=[
        ('none', 'None'),
        ('minimal', 'Minimal'),
        ('moderate', 'Moderate'),
        ('significant', 'Significant'),
        ('complete', 'Complete'),
    ], null=True, blank=True)
    
    # Overall wellbeing
    overall_wellbeing = models.IntegerField(choices=[
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Very Good'),
    ], null=True, blank=True)
    
    # Activity level
    activity_level = models.CharField(max_length=50, choices=[
        ('bedridden', 'Bedridden'),
        ('mostly_rest', 'Mostly Resting'),
        ('limited', 'Limited Activity'),
        ('normal', 'Normal Activity'),
    ], null=True, blank=True)
    
    # Additional notes
    additional_symptoms = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    # Submission tracking
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=True)  # Once submitted, cannot edit
    
    # Doctor review status
    reviewed_by_doctor = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    doctor_response = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'patient_symptom_logs'
        ordering = ['-log_date', '-submitted_at']
        verbose_name = 'Patient Symptom Log'
        verbose_name_plural = 'Patient Symptom Logs'
    
    def __str__(self):
        return f"Symptom Log: {self.patient.username} - {self.log_date}"
    
    def get_severe_symptoms(self):
        """Returns list of symptoms with severity >= 4"""
        severe = []
        symptom_fields = [
            'fatigue', 'pain', 'nausea', 'vomiting', 'appetite_loss',
            'sleep_problems', 'shortness_of_breath', 'diarrhea', 'constipation',
            'mouth_sores', 'skin_changes', 'numbness_tingling', 'anxiety',
            'depression', 'confusion'
        ]
        for field in symptom_fields:
            value = getattr(self, field)
            if value and value >= 4:
                severe.append({'symptom': field.replace('_', ' ').title(), 'severity': value})
        return severe


class PatientTreatmentExplanation(models.Model):
    """
    Patient-friendly treatment explanation derived from approved treatment plan.
    Simple language, step-by-step journey.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treatment_explanations')
    treatment_plan = models.OneToOneField('cancer_detection.PersonalizedTreatmentPlan',
                                           on_delete=models.CASCADE, related_name='patient_explanation')
    
    # Simple language summary
    treatment_summary = models.TextField()  # Plain language overview
    
    # Why this treatment was chosen
    why_this_treatment = models.TextField(null=True, blank=True)
    
    # Expected benefits
    expected_benefits = models.JSONField(default=list)
    # Example: ["Shrink the tumor", "Prevent spread", "Improve quality of life"]
    
    # Step-by-step treatment journey
    treatment_steps = models.JSONField(default=list)
    # Example: [
    #   {"step": 1, "title": "Initial Tests", "description": "Blood tests and scans", "duration": "1-2 weeks"},
    #   {"step": 2, "title": "Start Chemotherapy", "description": "...", "duration": "3 months"},
    # ]
    
    # Timeline
    estimated_duration = models.CharField(max_length=100, null=True, blank=True)
    key_milestones = models.JSONField(default=list, blank=True)
    
    # What to expect
    what_to_expect = models.JSONField(default=list, blank=True)
    # Example: ["Regular hospital visits", "Blood tests every week", "Some side effects"]
    
    # Questions to ask doctor
    suggested_questions = models.JSONField(default=list, blank=True)
    
    # Last updated by doctor
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='approved_explanations')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_treatment_explanations'
        ordering = ['-created_at']
        verbose_name = 'Patient Treatment Explanation'
        verbose_name_plural = 'Patient Treatment Explanations'
    
    def __str__(self):
        return f"Explanation: {self.patient.username} - {self.treatment_plan.cancer_type}"


class PatientSideEffectInfo(models.Model):
    """
    Patient-friendly side effect information.
    Simple labels, no CTCAE grades or probabilities.
    """
    
    SEVERITY_LABEL_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='side_effect_info')
    treatment_plan = models.ForeignKey('cancer_detection.PersonalizedTreatmentPlan',
                                        on_delete=models.CASCADE, related_name='patient_side_effects')
    
    # Drug/Treatment name
    treatment_name = models.CharField(max_length=200)
    
    # Common side effects with simple severity labels
    common_side_effects = models.JSONField(default=list)
    # Example: [
    #   {"effect": "Tiredness", "severity": "moderate", "description": "You may feel more tired than usual"},
    #   {"effect": "Nausea", "severity": "low", "description": "Some stomach upset is normal"},
    # ]
    
    # What is normal
    what_is_normal = models.JSONField(default=list, blank=True)
    # Example: ["Feeling tired for a few days after treatment", "Mild nausea"]
    
    # When to contact doctor
    when_to_contact_doctor = models.JSONField(default=list, blank=True)
    # Example: ["Fever over 38°C", "Severe vomiting", "Unusual bleeding"]
    
    # Self-care tips
    self_care_tips = models.JSONField(default=list, blank=True)
    
    # Emergency signs
    emergency_signs = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_side_effect_info'
        ordering = ['-created_at']
        verbose_name = 'Patient Side Effect Info'
        verbose_name_plural = 'Patient Side Effect Info'
    
    def __str__(self):
        return f"Side Effects: {self.treatment_name} - {self.patient.username}"


class PatientAlert(models.Model):
    """
    Patient alerts and reminders.
    Supports multiple notification channels.
    """
    
    ALERT_TYPE_CHOICES = [
        ('symptom_reminder', 'Symptom Log Reminder'),
        ('doctor_review', 'Doctor Reviewed Symptoms'),
        ('appointment', 'Appointment Reminder'),
        ('medication', 'Medication Reminder'),
        ('reassurance', 'Reassurance Message'),
        ('general', 'General Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('in_app', 'In-App Notification'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Channel and status
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='in_app')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    related_symptom_log = models.ForeignKey(PatientSymptomLog, on_delete=models.SET_NULL,
                                             null=True, blank=True, related_name='alerts')
    
    # Priority
    is_urgent = models.BooleanField(default=False)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_alerts'
        ordering = ['-created_at']
        verbose_name = 'Patient Alert'
        verbose_name_plural = 'Patient Alerts'
    
    def __str__(self):
        return f"Alert: {self.title} - {self.patient.username}"
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_read(self):
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()


class PatientNotificationPreference(models.Model):
    """
    Patient notification preferences for different channels.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Channel preferences
    enable_in_app = models.BooleanField(default=True)
    enable_sms = models.BooleanField(default=False)
    enable_whatsapp = models.BooleanField(default=False)
    enable_email = models.BooleanField(default=True)
    
    # Contact information
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Reminder preferences
    symptom_reminder_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('none', 'No Reminders'),
    ], default='daily')
    reminder_time = models.TimeField(null=True, blank=True)  # Preferred reminder time
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_notification_preferences'
        verbose_name = 'Patient Notification Preference'
        verbose_name_plural = 'Patient Notification Preferences'
    
    def __str__(self):
        return f"Preferences: {self.patient.username}"
