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
]


