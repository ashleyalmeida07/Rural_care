from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from datetime import datetime
from .models import CancerImageAnalysis, PersonalizedTreatmentPlan
from .opencv_analyzer import CancerImageAnalyzer
from .treatment_planner import TreatmentPlanningEngine
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


@login_required
def generate_treatment_plan(request, analysis_id):
    """Generate AI-powered personalized treatment plan from cancer analysis"""
    analysis = get_object_or_404(CancerImageAnalysis, id=analysis_id, user=request.user)
    
    if request.method == 'POST':
        try:
            # Get additional patient information from form
            patient_age = int(request.POST.get('age', 50))
            performance_status = int(request.POST.get('performance_status', 1))
            comorbidities = request.POST.getlist('comorbidities')
            genetic_mutations = request.POST.getlist('mutations')
            
            # Prepare patient data for treatment planning engine
            patient_data = {
                'age': patient_age,
                'performance_status': performance_status,
                'comorbidities': comorbidities,
                'lab_values': {
                    'ejection_fraction': float(request.POST.get('ejection_fraction', 55)),
                    'creatinine': float(request.POST.get('creatinine', 1.0)),
                    'gfr': float(request.POST.get('gfr', 90)),
                    'bilirubin': float(request.POST.get('bilirubin', 0.7)),
                    'hemoglobin': float(request.POST.get('hemoglobin', 12.0)),
                    'wbc': float(request.POST.get('wbc', 7.0)),
                    'platelets': float(request.POST.get('platelets', 200)),
                }
            }
            
            # Prepare tumor data
            tumor_data = {
                'cancer_type': analysis.tumor_type or request.POST.get('cancer_type', 'unknown'),
                'stage': analysis.tumor_stage or request.POST.get('stage', '1'),
                'grade': request.POST.get('grade', 'unknown'),
                'size_mm': analysis.tumor_size_mm or float(request.POST.get('size_mm', 0)),
                'location': analysis.tumor_location or request.POST.get('location', 'unknown'),
                'lymph_node_involvement': request.POST.get('lymph_node_involvement', 'false').lower() == 'true',
                'metastasis': request.POST.get('metastasis', 'false').lower() == 'true',
                'metastasis_sites': request.POST.getlist('metastasis_sites'),
            }
            
            # Prepare genetic data
            genetic_data = {
                'mutations': {mutation: True for mutation in genetic_mutations},
                'biomarkers': analysis.genetic_profile.get('biomarkers', {}),
                'pd_l1_status': request.POST.get('pd_l1_status', 'unknown'),
                'msi_status': request.POST.get('msi_status', 'unknown'),
                'tumor_mutational_burden': request.POST.get('tmb', 'unknown'),
                'immune_infiltration': request.POST.get('immune_infiltration', 'unknown'),
            }
            
            # Generate treatment plan using AI engine
            engine = TreatmentPlanningEngine()
            
            patient_profile = engine.analyze_patient_profile(patient_data)
            tumor_analysis = engine.analyze_tumor_characteristics(tumor_data)
            genetic_profile = engine.analyze_genetic_profile(genetic_data)
            
            treatment_plan = engine.generate_treatment_plan(patient_profile, tumor_analysis, genetic_profile)
            pathway = engine.generate_patient_pathway(treatment_plan)
            
            # Save treatment plan to database
            plan = PersonalizedTreatmentPlan.objects.create(
                patient=request.user,
                analysis=analysis,
                plan_name=f"{tumor_data['cancer_type'].title()} Stage {tumor_data['stage']} - {datetime.now().strftime('%Y-%m-%d')}",
                cancer_type=tumor_data['cancer_type'],
                cancer_stage=tumor_data['stage'],
                patient_profile=patient_profile,
                tumor_analysis=tumor_analysis,
                genetic_profile=genetic_profile,
                primary_treatments=treatment_plan.get('primary_treatment', []),
                adjuvant_treatments=treatment_plan.get('adjuvant_treatment', []),
                targeted_therapies=genetic_profile.get('targeted_therapy_eligible', []),
                side_effects=treatment_plan.get('side_effects', []),
                predicted_5yr_survival=treatment_plan.get('outcome_predictions', {}).get('predicted_5yr_survival'),
                remission_probability=treatment_plan.get('outcome_predictions', {}).get('response_probability'),
                quality_of_life_score=treatment_plan.get('outcome_predictions', {}).get('quality_of_life_impact'),
                monitoring_plan=treatment_plan.get('monitoring_recommendations', {}),
                treatment_pathway=pathway,
                clinical_trials=treatment_plan.get('clinical_trials', []),
                contraindications=engine.contraindications,
                special_considerations=request.POST.get('special_considerations', ''),
                status='draft'
            )
            
            messages.success(request, 'Personalized treatment plan generated successfully!')
            return redirect('cancer_detection:treatment_plan_detail', plan_id=plan.id)
        
        except Exception as e:
            messages.error(request, f'Error generating treatment plan: {str(e)}')
            return redirect('cancer_detection:analysis_detail', analysis_id=analysis_id)
    
    # Get patient's medical profile if available
    try:
        patient_profile = request.user.patient_profile
    except:
        patient_profile = None
    
    # Common comorbidities list
    comorbidities_list = [
        'Diabetes',
        'Hypertension',
        'Cardiovascular Disease',
        'Chronic Kidney Disease',
        'Chronic Liver Disease',
        'Chronic Pulmonary Disease',
        'History of Other Cancers',
        'HIV/AIDS',
        'Autoimmune Disorder',
    ]
    
    # Common mutations for cancer
    mutations_list = [
        'EGFR',
        'ALK',
        'ROS1',
        'HER2',
        'BRAF V600E',
        'KRAS G12C',
        'TP53',
        'BRCA1',
        'BRCA2',
        'MSI-H',
        'TMB-H',
        'PD-L1+',
    ]
    
    context = {
        'analysis': analysis,
        'patient_profile': patient_profile,
        'comorbidities_list': comorbidities_list,
        'mutations_list': mutations_list,
    }
    
    return render(request, 'cancer_detection/generate_treatment_plan.html', context)


@login_required
def treatment_plan_detail(request, plan_id):
    """View detailed personalized treatment plan"""
    plan = get_object_or_404(PersonalizedTreatmentPlan, id=plan_id, patient=request.user)
    
    # Format lab values keys with spaces instead of underscores for display
    patient_profile = plan.patient_profile.copy() if isinstance(plan.patient_profile, dict) else plan.patient_profile
    if isinstance(patient_profile, dict) and 'lab_values' in patient_profile:
        formatted_lab_values = {}
        for key, value in patient_profile['lab_values'].items():
            formatted_key = key.replace('_', ' ').title()
            formatted_lab_values[formatted_key] = value
        patient_profile['lab_values'] = formatted_lab_values
    
    context = {
        'plan': plan,
        'patient_profile': patient_profile,
        'tumor_analysis': plan.tumor_analysis,
        'genetic_profile': plan.genetic_profile,
        'treatment_pathway': plan.treatment_pathway,
        'monitoring_plan': plan.monitoring_plan,
        'clinical_trials': plan.clinical_trials,
    }
    
    return render(request, 'cancer_detection/treatment_plan_detail.html', context)


@login_required
def treatment_plans_list(request):
    """List all treatment plans for current patient"""
    plans = PersonalizedTreatmentPlan.objects.filter(patient=request.user)
    
    # Pagination
    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_plans': plans.count(),
        'active_plans': plans.filter(status='active').count(),
        'pending_review': plans.filter(status='pending_review').count(),
    }
    
    return render(request, 'cancer_detection/treatment_plans_list.html', context)


@login_required
@require_POST
def submit_treatment_plan_review(request, plan_id):
    """Submit treatment plan for oncologist review"""
    plan = get_object_or_404(PersonalizedTreatmentPlan, id=plan_id, patient=request.user)
    
    if plan.status == 'draft':
        plan.status = 'pending_review'
        plan.save()
        messages.success(request, 'Treatment plan submitted for oncologist review.')
    else:
        messages.warning(request, 'Only draft plans can be submitted for review.')
    
    return redirect('cancer_detection:treatment_plan_detail', plan_id=plan.id)
