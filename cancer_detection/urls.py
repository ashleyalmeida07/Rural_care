from django.urls import path
from . import views

app_name = 'cancer_detection'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_image, name='upload_image'),
    path('analyses/', views.analysis_list, name='analysis_list'),
    path('analyses/<uuid:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('analyses/<uuid:analysis_id>/delete/', views.delete_analysis, name='delete_analysis'),
    path('analyses/<uuid:analysis_id>/treatment-plan/', views.generate_treatment_plan, name='generate_treatment_plan'),
    path('treatment-plans/', views.treatment_plans_list, name='treatment_plans_list'),
    path('treatment-plans/<uuid:plan_id>/', views.treatment_plan_detail, name='treatment_plan_detail'),
    path('treatment-plans/<uuid:plan_id>/submit-review/', views.submit_treatment_plan_review, name='submit_treatment_plan_review'),
    
    # Histopathology Reports
    path('histopathology/upload/', views.upload_histopathology_report, name='upload_histopathology'),
    path('histopathology/', views.histopathology_reports_list, name='histopathology_list'),
    path('histopathology/<uuid:report_id>/', views.histopathology_report_detail, name='histopathology_detail'),
    
    # Genomic Profiles
    path('genomics/upload/', views.upload_genomic_profile, name='upload_genomic'),
    path('genomics/', views.genomic_profiles_list, name='genomic_list'),
    path('genomics/<uuid:profile_id>/', views.genomic_profile_detail, name='genomic_detail'),
    
    # Comprehensive Treatment Planning
    path('comprehensive-plan/', views.create_comprehensive_plan, name='create_comprehensive_plan'),
    path('treatment-plans/<uuid:plan_id>/visualize/', views.visualize_treatment_pathway, name='visualize_pathway'),
    path('treatment-plans/<uuid:plan_id>/decision-support/', views.decision_support, name='decision_support'),
]


