from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('auth/callback/', views.auth_callback, name='auth_callback'),
    path('logout/', views.logout_view, name='logout'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    # KYC Routes
    path('doctor/kyc/status/', views.kyc_status, name='kyc_status'),
    path('doctor/kyc/form/', views.kyc_form, name='kyc_form'),
    path('doctor/kyc/preview/', views.kyc_preview, name='kyc_preview'),
]