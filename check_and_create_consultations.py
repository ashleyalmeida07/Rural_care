import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from authentication.models import User
from patient_portal.consultation_models import ConsultationRequest, Consultation, DoctorAvailability
from django.utils import timezone
from datetime import timedelta

# Check existing data
print("=" * 60)
print("DATABASE STATUS CHECK")
print("=" * 60)
print(f"Total Doctors: {User.objects.filter(user_type='doctor').count()}")
print(f"Total Patients: {User.objects.filter(user_type='patient').count()}")
print(f"Total Consultation Requests: {ConsultationRequest.objects.count()}")
print(f"Total Consultations: {Consultation.objects.count()}")
print(f"Total Doctor Availability Slots: {DoctorAvailability.objects.count()}")
print("=" * 60)

# Get users
doctors = User.objects.filter(user_type='doctor')
patients = User.objects.filter(user_type='patient')

if doctors.exists():
    print(f"\nSample Doctor: {doctors.first().email} ({doctors.first().first_name} {doctors.first().last_name})")
if patients.exists():
    print(f"Sample Patient: {patients.first().email} ({patients.first().first_name} {patients.first().last_name})")

# Create sample data if needed
if doctors.exists() and patients.exists() and Consultation.objects.count() == 0:
    print("\n" + "=" * 60)
    print("CREATING SAMPLE CONSULTATION DATA")
    print("=" * 60)
    
    doctor = doctors.first()
    patient = patients.first()
    
    # Create a consultation request
    request = ConsultationRequest.objects.create(
        patient=patient,
        doctor=doctor,
        consultation_type='general',
        reason='Sample consultation for testing',
        status='scheduled'
    )
    print(f"✓ Created Consultation Request: {request.id}")
    
    # Create a consultation
    consultation = Consultation.objects.create(
        request=request,
        patient=patient,
        doctor=doctor,
        scheduled_datetime=timezone.now() + timedelta(hours=2),
        duration_minutes=30,
        mode='video',
        status='scheduled'
    )
    print(f"✓ Created Consultation: {consultation.id}")
    
    # Create another past consultation
    past_request = ConsultationRequest.objects.create(
        patient=patient,
        doctor=doctor,
        consultation_type='follow_up',
        reason='Follow-up consultation',
        status='completed'
    )
    
    past_consultation = Consultation.objects.create(
        request=past_request,
        patient=patient,
        doctor=doctor,
        scheduled_datetime=timezone.now() - timedelta(days=2),
        duration_minutes=30,
        mode='video',
        status='completed',
        completed_at=timezone.now() - timedelta(days=2)
    )
    print(f"✓ Created Past Consultation: {past_consultation.id}")
    
    print("\n" + "=" * 60)
    print("FINAL COUNT")
    print("=" * 60)
    print(f"Total Consultation Requests: {ConsultationRequest.objects.count()}")
    print(f"Total Consultations: {Consultation.objects.count()}")
    print(f"Doctor's Consultations: {Consultation.objects.filter(doctor=doctor).count()}")
    print("=" * 60)
else:
    if not doctors.exists():
        print("\n⚠ No doctors found in database. Please create a doctor account first.")
    if not patients.exists():
        print("\n⚠ No patients found in database. Please create a patient account first.")
    if Consultation.objects.count() > 0:
        print(f"\n✓ Database already has {Consultation.objects.count()} consultations")
