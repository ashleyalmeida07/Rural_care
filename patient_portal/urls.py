from django.urls import path
from . import views
from . import consultation_views
from . import call_views

app_name = 'patient_portal'

urlpatterns = [
    # Overview/Dashboard
    path('', views.patient_overview, name='overview'),
    
    # Confidence View (Simplified)
    path('confidence/', views.patient_confidence_view, name='confidence_view'),
    
    # Treatment Explanations
    path('treatment/', views.treatment_explanation_list, name='treatment_explanation_list'),
    path('treatment/<uuid:explanation_id>/', views.treatment_explanation_detail, name='treatment_explanation_detail'),
    
    # Side Effects
    path('side-effects/', views.side_effects_list, name='side_effects_list'),
    path('side-effects/<uuid:info_id>/', views.side_effects_detail, name='side_effects_detail'),
    
    # Symptom Logging
    path('symptoms/', views.symptom_log_list, name='symptom_log_list'),
    path('symptoms/log/', views.symptom_log_create, name='symptom_log_create'),
    path('symptoms/<uuid:log_id>/', views.symptom_log_detail, name='symptom_log_detail'),
    
    # Alerts & Reminders
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alerts/<uuid:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    path('alerts/mark-all-read/', views.mark_all_alerts_read, name='mark_all_alerts_read'),
    
    # Notification Preferences
    path('notifications/', views.notification_preferences, name='notification_preferences'),
    
    # Consultations
    path('consultations/doctors/', consultation_views.available_doctors, name='available_doctors'),
    path('consultations/doctor/<uuid:doctor_id>/', consultation_views.doctor_profile_view, name='doctor_profile_view'),
    path('consultations/request/<uuid:doctor_id>/', consultation_views.request_consultation, name='request_consultation'),
    path('consultations/requests/', consultation_views.consultation_requests, name='consultation_requests'),
    path('consultations/accept/<uuid:request_id>/', consultation_views.accept_suggested_time, name='accept_suggested_time'),
    path('consultations/my/', consultation_views.my_consultations, name='my_consultations'),
    path('consultations/cancel/<uuid:consultation_id>/', consultation_views.cancel_consultation, name='cancel_consultation'),
    
    # Call functionality
    path('call/<uuid:consultation_id>/start/', call_views.initiate_call, name='initiate_call'),
    path('call/<uuid:consultation_id>/join/', call_views.doctor_call_view, name='doctor_call_view'),
    path('call/<uuid:consultation_id>/status/', call_views.call_status, name='call_status'),
    path('call/<uuid:consultation_id>/end/', call_views.end_call, name='end_call'),
    
    # API Endpoints
    path('api/alerts/count/', views.api_unread_alerts_count, name='api_alerts_count'),
    path('api/symptoms/trend/', views.api_symptom_trend, name='api_symptom_trend'),
    path('api/incoming-calls/', call_views.check_incoming_calls, name='api_incoming_calls'),
]
