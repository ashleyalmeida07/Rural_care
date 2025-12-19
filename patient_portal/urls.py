from django.urls import path
from . import views

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
    
    # API Endpoints
    path('api/alerts/count/', views.api_unread_alerts_count, name='api_alerts_count'),
    path('api/symptoms/trend/', views.api_symptom_trend, name='api_symptom_trend'),
]
