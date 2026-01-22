"""
Real-time Call Views for Video and Phone Consultations
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
import json

from .consultation_models import Consultation
from authentication.models import User


@login_required
def initiate_call(request, consultation_id):
    """Patient initiates a call to doctor"""
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id,
        patient=request.user
    )
    
    # Check if consultation is scheduled for today
    today = timezone.now().date()
    if consultation.scheduled_datetime.date() != today:
        return JsonResponse({'error': 'Consultation not scheduled for today'}, status=400)
    
    # Update consultation status to indicate call started
    consultation.call_status = 'calling'
    consultation.call_initiated_by = request.user
    consultation.call_initiated_at = timezone.now()
    consultation.save()
    
    context = {
        'consultation': consultation,
        'is_video': consultation.mode == 'video',
        'is_phone': consultation.mode == 'phone',
        'room_id': str(consultation.id),
    }
    
    return render(request, 'patient_portal/call/call_interface.html', context)


@login_required
def doctor_call_view(request, consultation_id):
    """Doctor receives and joins the call"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id,
        doctor=request.user
    )
    
    # Update call status
    if consultation.call_status == 'calling':
        consultation.call_status = 'active'
        consultation.started_at = timezone.now()
        consultation.save()
    
    context = {
        'consultation': consultation,
        'is_video': consultation.mode == 'video',
        'is_phone': consultation.mode == 'phone',
        'room_id': str(consultation.id),
    }
    
    return render(request, 'authentication/doctor/call_interface.html', context)


@login_required
def check_incoming_calls(request):
    """Check for incoming calls for doctor"""
    if request.user.user_type != 'doctor':
        return JsonResponse({'calls': []})
    
    # Get consultations with incoming calls
    incoming_calls = Consultation.objects.filter(
        doctor=request.user,
        call_status='calling',
        scheduled_datetime__date=timezone.now().date()
    ).select_related('patient')
    
    calls_data = [{
        'id': str(call.id),
        'patient_name': f"{call.patient.first_name} {call.patient.last_name}",
        'mode': call.mode,
        'initiated_at': call.call_initiated_at.isoformat() if call.call_initiated_at else None,
    } for call in incoming_calls]
    
    return JsonResponse({'calls': calls_data})


@login_required
@require_POST
def end_call(request, consultation_id):
    """End an active call"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id
    )
    
    # Only patient or doctor can end their own call
    if request.user not in [consultation.patient, consultation.doctor]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    consultation.call_status = 'ended'
    consultation.completed_at = timezone.now()
    consultation.status = 'completed'
    consultation.save()
    
    return JsonResponse({'status': 'ended'})


@login_required
def call_status(request, consultation_id):
    """Get current call status and signaling data"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id
    )
    
    # Check if user is part of this consultation
    if request.user not in [consultation.patient, consultation.doctor]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Determine if user is patient or doctor
    is_patient = request.user == consultation.patient
    
    return JsonResponse({
        'status': consultation.call_status,
        'mode': consultation.mode,
        'started_at': consultation.started_at.isoformat() if consultation.started_at else None,
        # Include signaling data for peer connection
        'offer': consultation.patient_offer if is_patient else consultation.patient_offer,
        'answer': consultation.doctor_answer if not is_patient else consultation.doctor_answer,
        'ice_candidates': consultation.doctor_ice_candidates if is_patient else consultation.patient_ice_candidates,
    })


@login_required
@require_POST
def send_offer(request, consultation_id):
    """Patient sends WebRTC offer"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id,
        patient=request.user
    )
    
    data = json.loads(request.body)
    consultation.patient_offer = data.get('offer', '')
    consultation.save()
    
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def send_answer(request, consultation_id):
    """Doctor sends WebRTC answer"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id,
        doctor=request.user
    )
    
    data = json.loads(request.body)
    consultation.doctor_answer = data.get('answer', '')
    consultation.save()
    
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def send_ice_candidate(request, consultation_id):
    """Send ICE candidate for peer connection"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id
    )
    
    if request.user not in [consultation.patient, consultation.doctor]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    data = json.loads(request.body)
    candidate = data.get('candidate', '')
    
    # Determine who is sending
    is_patient = request.user == consultation.patient
    
    if is_patient:
        # Append to patient candidates
        candidates = json.loads(consultation.patient_ice_candidates or '[]')
        candidates.append(candidate)
        consultation.patient_ice_candidates = json.dumps(candidates)
    else:
        # Append to doctor candidates
        candidates = json.loads(consultation.doctor_ice_candidates or '[]')
        candidates.append(candidate)
        consultation.doctor_ice_candidates = json.dumps(candidates)
    
    consultation.save()
    
    return JsonResponse({'status': 'success'})
