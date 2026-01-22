"""
Prescription Views for Doctor and Patient
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .prescription_models import Prescription, PrescriptionMedicine
from .consultation_models import Consultation
from patient_portal.consultation_views import doctor_required, patient_required
import json
import logging

logger = logging.getLogger(__name__)


@login_required
@doctor_required
def create_prescription(request, consultation_id):
    """Create prescription for a completed consultation - multiple prescriptions allowed"""
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id,
        doctor=request.user
    )
    
    if request.method == 'POST':
        # Create prescription
        prescription = Prescription.objects.create(
            consultation=consultation,
            patient=consultation.patient,
            doctor=request.user,
            diagnosis=request.POST.get('diagnosis', ''),
            symptoms=request.POST.get('symptoms', ''),
            doctor_notes=request.POST.get('doctor_notes', ''),
            follow_up_instructions=request.POST.get('follow_up_instructions', '')
        )
        
        # Add medicines
        medicine_data = json.loads(request.POST.get('medicines_json', '[]'))
        for idx, med in enumerate(medicine_data):
            PrescriptionMedicine.objects.create(
                prescription=prescription,
                medicine_name=med['name'],
                dosage=med['dosage'],
                frequency=med['frequency'],
                timing=med['timing'],
                duration_days=int(med['duration']),
                instructions=med.get('instructions', ''),
                order=idx
            )
        
        messages.success(request, 'Prescription created successfully.')
        return redirect('patient_portal:generate_prescription_pdf', prescription_id=prescription.id)
    
    context = {
        'consultation': consultation,
    }
    return render(request, 'patient_portal/prescription/create_prescription.html', context)


@login_required
@doctor_required
def edit_prescription(request, prescription_id):
    """Edit prescription - DISABLED: Prescriptions are immutable once created"""
    prescription = get_object_or_404(
        Prescription,
        id=prescription_id,
        doctor=request.user
    )
    
    messages.error(request, 'Prescriptions cannot be edited once created. Please create a new prescription if needed.')
    return redirect('patient_portal:view_prescription', prescription_id=prescription.id)


@login_required
def generate_prescription_pdf(request, prescription_id):
    """Generate PDF for prescription with blockchain verification"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check permissions
    if request.user not in [prescription.doctor, prescription.patient]:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    from .prescription_pdf import generate_prescription_pdf as create_pdf, generate_qr_code
    from django.urls import reverse
    
    # Step 1: Generate verification URL and QR code
    verification_url = request.build_absolute_uri(
        reverse('patient_portal:verify_prescription', args=[prescription.id])
    )
    qr_code_file = generate_qr_code(verification_url, prescription.id)
    prescription.qr_code = qr_code_file
    prescription.save()
    
    # Step 2: Generate PDF without QR first to get initial hash
    pdf_file, pdf_hash = create_pdf(prescription, include_qr=False)
    
    # Save initial PDF and hash
    prescription.pdf_file = pdf_file
    prescription.pdf_hash = pdf_hash
    prescription.save()
    
    # Step 3: Store on blockchain
    if settings.BLOCKCHAIN_ENABLED:
        from blockchain.blockchain_service import store_prescription_hash
        try:
            result = store_prescription_hash(
                prescription_id=prescription.id,
                pdf_hash=pdf_hash,
                patient_id=prescription.patient.id,
                doctor_id=prescription.doctor.id
            )
            if result and result.get('success'):
                prescription.blockchain_tx_hash = result['transaction_hash']
                prescription.is_verified = True
                prescription.save()
                logger.info(f"Prescription {prescription.id} stored on blockchain: {result['transaction_hash']}")
            else:
                logger.warning(f"Failed to store prescription on blockchain: {result}")
        except Exception as e:
            logger.error(f"Blockchain error: {e}")
    
    # Step 4: Regenerate PDF WITH QR code for download
    pdf_file_with_qr, _ = create_pdf(prescription, include_qr=True)
    prescription.pdf_file = pdf_file_with_qr
    prescription.save()
    
    messages.success(request, 'Prescription PDF generated successfully with blockchain verification.')
    return redirect('patient_portal:view_prescription', prescription_id=prescription.id)


@login_required
def view_prescription(request, prescription_id):
    """View prescription details"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check permissions
    if request.user not in [prescription.doctor, prescription.patient]:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    context = {
        'prescription': prescription,
        'medicines': prescription.medicines.all()
    }
    return render(request, 'patient_portal/prescription/view_prescription.html', context)


@login_required
def download_prescription(request, prescription_id):
    """Download prescription PDF"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check permissions
    if request.user not in [prescription.doctor, prescription.patient]:
        return HttpResponse('Access denied', status=403)
    
    if not prescription.pdf_file:
        messages.error(request, 'PDF not generated yet.')
        return redirect('patient_portal:view_prescription', prescription_id=prescription.id)
    
    response = FileResponse(
        prescription.pdf_file.open('rb'),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}.pdf"'
    return response


def verify_prescription(request, prescription_id):
    """Public verification page for prescription"""
    try:
        prescription = get_object_or_404(Prescription, id=prescription_id)
        
        # Verify hash against blockchain
        is_valid = False
        blockchain_data = None
        
        if prescription.pdf_hash and settings.BLOCKCHAIN_ENABLED:
            from blockchain.blockchain_service import get_blockchain_service
            service = get_blockchain_service()
            
            if service.is_connected():
                blockchain_data = service.verify_prescription_hash(prescription.pdf_hash)
                if blockchain_data and blockchain_data.get('exists'):
                    is_valid = True
                    logger.info(f"Prescription {prescription.id} verified on blockchain")
                else:
                    logger.warning(f"Prescription {prescription.id} not found on blockchain")
            else:
                logger.warning("Blockchain service not connected for verification")
        
        context = {
            'prescription': prescription,
            'is_valid': is_valid,
            'blockchain_data': blockchain_data,
            'patient_name': f"{prescription.patient.first_name} {prescription.patient.last_name}",
            'doctor_name': f"Dr. {prescription.doctor.first_name} {prescription.doctor.last_name}",
            'issued_date': prescription.created_at,
            'blockchain_verified': is_valid,
            'tx_hash': prescription.blockchain_tx_hash
        }
        return render(request, 'patient_portal/prescription/verify_prescription.html', context)
    except Exception as e:
        return render(request, 'patient_portal/prescription/verify_prescription.html', {
            'error': 'Prescription not found or invalid.'
        })
