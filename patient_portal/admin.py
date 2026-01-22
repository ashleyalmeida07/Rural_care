from django.contrib import admin
from .models import (
    PatientSymptomLog, PatientTreatmentExplanation,
    PatientSideEffectInfo, PatientAlert, PatientNotificationPreference,
    DoctorAvailability, ConsultationRequest, Consultation
)


@admin.register(PatientSymptomLog)
class PatientSymptomLogAdmin(admin.ModelAdmin):
    list_display = ['patient', 'log_date', 'log_type', 'overall_wellbeing', 'reviewed_by_doctor', 'submitted_at']
    list_filter = ['log_type', 'reviewed_by_doctor', 'log_date']
    search_fields = ['patient__username', 'patient__email']
    readonly_fields = ['id', 'submitted_at']


@admin.register(PatientTreatmentExplanation)
class PatientTreatmentExplanationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'treatment_plan', 'approved_by', 'approved_at', 'created_at']
    list_filter = ['created_at', 'approved_at']
    search_fields = ['patient__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PatientSideEffectInfo)
class PatientSideEffectInfoAdmin(admin.ModelAdmin):
    list_display = ['patient', 'treatment_name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['patient__username', 'treatment_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PatientAlert)
class PatientAlertAdmin(admin.ModelAdmin):
    list_display = ['patient', 'alert_type', 'title', 'channel', 'status', 'is_urgent', 'created_at']
    list_filter = ['alert_type', 'channel', 'status', 'is_urgent', 'created_at']
    search_fields = ['patient__username', 'title']
    readonly_fields = ['id', 'created_at']


@admin.register(PatientNotificationPreference)
class PatientNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['patient', 'enable_in_app', 'enable_sms', 'enable_whatsapp', 'enable_email', 'symptom_reminder_frequency']
    search_fields = ['patient__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'weekday', 'start_time', 'end_time', 'is_available', 'slot_duration']
    list_filter = ['weekday', 'is_available', 'doctor']
    search_fields = ['doctor__username', 'doctor__first_name', 'doctor__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'consultation_type', 'status', 'requested_at']
    list_filter = ['status', 'consultation_type', 'requested_at']
    search_fields = ['patient__username', 'doctor__username', 'reason']
    readonly_fields = ['id', 'requested_at']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'scheduled_datetime', 'mode', 'status', 'duration_minutes']
    list_filter = ['status', 'mode', 'scheduled_datetime']
    search_fields = ['patient__username', 'doctor__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
