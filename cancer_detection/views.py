from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import CancerImageAnalysis
from .opencv_analyzer import CancerImageAnalyzer
import os
import json

# All views in this module require authentication
# Unauthenticated users will be redirected to LOGIN_URL (patient_login)


@login_required
def upload_image(request):
    """View for uploading cancer images"""
    if request.method == 'POST':
        if 'image' not in request.FILES:
            messages.error(request, 'Please select an image file.')
            return redirect('cancer_detection:upload_image')
        
        image_file = request.FILES['image']
        image_type = request.POST.get('image_type', 'other')
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        file_ext = os.path.splitext(image_file.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            messages.error(request, f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}')
            return redirect('cancer_detection:upload_image')
        
        # Create analysis record
        analysis = CancerImageAnalysis.objects.create(
            user=request.user,
            image=image_file,
            image_type=image_type,
            original_filename=image_file.name
        )
        
        # Perform analysis
        try:
            analyzer = CancerImageAnalyzer()
            # Ensure the file is saved before accessing path
            if not analysis.image:
                raise ValueError("Image file not saved properly")
            image_path = analysis.image.path
            results = analyzer.analyze_image(image_path, image_type)
            
            # Update analysis with results
            analysis.tumor_detected = results.get('tumor_detected', False)
            analysis.tumor_type = results.get('tumor_type')
            analysis.tumor_stage = results.get('tumor_stage')
            analysis.tumor_size_mm = results.get('tumor_size_mm')
            analysis.tumor_location = results.get('tumor_location')
            analysis.genetic_profile = results.get('genetic_profile', {})
            analysis.comorbidities = results.get('comorbidities', [])
            analysis.analysis_data = results.get('detailed_analysis', {})
            analysis.detection_confidence = results.get('detection_confidence', 0.0)
            analysis.stage_confidence = results.get('stage_confidence', 0.0)
            analysis.save()
            
            messages.success(request, 'Image analyzed successfully!')
            return redirect('cancer_detection:analysis_detail', analysis_id=analysis.id)
            
        except Exception as e:
            messages.error(request, f'Error analyzing image: {str(e)}')
            analysis.delete()  # Delete the record if analysis fails
            return redirect('cancer_detection:upload_image')
    
    return render(request, 'cancer_detection/upload_image.html', {
        'image_types': CancerImageAnalysis.IMAGE_TYPE_CHOICES
    })


@login_required
def analysis_list(request):
    """List all analyses for the current user"""
    analyses = CancerImageAnalysis.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(analyses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cancer_detection/analysis_list.html', {
        'page_obj': page_obj
    })


@login_required
def analysis_detail(request, analysis_id):
    """View detailed analysis results"""
    analysis = get_object_or_404(CancerImageAnalysis, id=analysis_id, user=request.user)
    
    # Format analysis data for display
    context = {
        'analysis': analysis,
        'genetic_profile': analysis.genetic_profile or {},
        'comorbidities': analysis.comorbidities or [],
        'detailed_analysis': analysis.analysis_data or {},
    }
    
    return render(request, 'cancer_detection/analysis_detail.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_analysis(request, analysis_id):
    """Delete an analysis"""
    analysis = get_object_or_404(CancerImageAnalysis, id=analysis_id, user=request.user)
    
    # Delete the image file
    if analysis.image:
        try:
            os.remove(analysis.image.path)
        except:
            pass
    
    analysis.delete()
    messages.success(request, 'Analysis deleted successfully.')
    return JsonResponse({'success': True})


@login_required
def dashboard(request):
    """Cancer detection dashboard"""
    # Get statistics
    total_analyses = CancerImageAnalysis.objects.filter(user=request.user).count()
    detected_cases = CancerImageAnalysis.objects.filter(user=request.user, tumor_detected=True).count()
    recent_analyses = CancerImageAnalysis.objects.filter(user=request.user)[:5]
    
    context = {
        'total_analyses': total_analyses,
        'detected_cases': detected_cases,
        'recent_analyses': recent_analyses,
    }
    
    return render(request, 'cancer_detection/dashboard.html', context)
