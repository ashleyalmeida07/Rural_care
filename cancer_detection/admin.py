from django.contrib import admin
from .models import CancerImageAnalysis


@admin.register(CancerImageAnalysis)
class CancerImageAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image_type', 'tumor_detected', 'tumor_type', 'tumor_stage', 'created_at')
    list_filter = ('image_type', 'tumor_detected', 'tumor_stage', 'created_at')
    search_fields = ('user__username', 'user__email', 'tumor_type', 'tumor_location')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Image Information', {
            'fields': ('user', 'image', 'image_type', 'original_filename')
        }),
        ('Analysis Results', {
            'fields': (
                'tumor_detected', 'tumor_type', 'tumor_stage', 
                'tumor_size_mm', 'tumor_location',
                'detection_confidence', 'stage_confidence'
            )
        }),
        ('Advanced Analysis', {
            'fields': ('genetic_profile', 'comorbidities', 'analysis_data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
