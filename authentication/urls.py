from django.urls import path
from . import views
from . import qr_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('auth/callback/', views.auth_callback, name='auth_callback'),
    path('logout/', views.logout_view, name='logout'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),
    # KYC Routes
    path('doctor/kyc/status/', views.kyc_status, name='kyc_status'),
    path('doctor/kyc/form/', views.kyc_form, name='kyc_form'),
    path('doctor/kyc/preview/', views.kyc_preview, name='kyc_preview'),
    
    # Medical Records
    path('patient/medical-records/', views.medical_records_list, name='medical_records_list'),
    path('patient/medical-records/upload/', views.upload_medical_record, name='upload_medical_record'),
    path('patient/medical-records/<uuid:record_id>/', views.medical_record_detail, name='medical_record_detail'),
    path('patient/medical-records/<uuid:record_id>/delete/', views.delete_medical_record, name='delete_medical_record'),
    
    # QR Code Routes
    path('patient/qr-code/', qr_views.patient_qr_dashboard, name='patient_qr_dashboard'),
    path('patient/qr-code/regenerate/', qr_views.regenerate_qr_code, name='regenerate_qr_code'),
    path('patient/qr-code/disable/', qr_views.disable_qr_code, name='disable_qr_code'),
    path('patient/qr-code/enable/', qr_views.enable_qr_code, name='enable_qr_code'),
    path('patient/qr-code/analytics/<uuid:patient_id>/', qr_views.qr_scan_analytics, name='qr_scan_analytics'),
    path('doctor/qr-scanner/', qr_views.doctor_qr_scanner, name='doctor_qr_scanner'),
    path('doctor/qr-scanner/scan/', qr_views.scan_qr_code, name='scan_qr_code'),
    path('doctor/patient/<uuid:patient_id>/profile/', qr_views.scanned_patient_profile, name='scanned_patient_profile'),
]