from django.urls import path
from . import views

app_name = 'cancer_detection'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_image, name='upload_image'),
    path('analyses/', views.analysis_list, name='analysis_list'),
    path('analyses/<uuid:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('analyses/<uuid:analysis_id>/delete/', views.delete_analysis, name='delete_analysis'),
]

