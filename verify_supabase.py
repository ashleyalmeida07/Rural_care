"""Comprehensive Supabase Database Verification"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from django.conf import settings
from authentication.models import User, DoctorProfile, PatientProfile
from patient_portal.consultation_models import Consultation, ConsultationRequest, DoctorAvailability
from patient_portal.prescription_models import Prescription, PrescriptionMedicine

print('\n' + '='*80)
print('SUPABASE DATABASE CONNECTION VERIFICATION')
print('='*80)

# Check database configuration
print('\n📊 Database Configuration:')
db_config = settings.DATABASES['default']
print(f'   Engine: {db_config["ENGINE"]}')
if 'postgresql' in db_config['ENGINE']:
    print(f'   ✅ Using PostgreSQL (Supabase)')
    print(f'   Host: {db_config["HOST"]}')
    print(f'   Database: {db_config["NAME"]}')
    print(f'   User: {db_config["USER"]}')
else:
    print(f'   ❌ Using SQLite (Local)')
    print(f'   Path: {db_config["NAME"]}')

print('\n' + '-'*80)
print('DATA SUMMARY FROM DATABASE')
print('-'*80)

# Users
print('\n👥 USERS:')
total_users = User.objects.count()
patients = User.objects.filter(user_type='patient')
doctors = User.objects.filter(user_type='doctor')
print(f'   Total Users: {total_users}')
print(f'   Patients: {patients.count()}')
print(f'   Doctors: {doctors.count()}')

# Doctor Profiles
print('\n👨‍⚕️ DOCTOR PROFILES:')
doctor_profiles = DoctorProfile.objects.all()
print(f'   Total: {doctor_profiles.count()}')
for profile in doctor_profiles[:10]:  # Show first 10
    spec = profile.specialization or 'Not set'
    print(f'   - Dr. {profile.user.first_name} {profile.user.last_name}: {spec}')

# Patient Profiles
print('\n👤 PATIENT PROFILES:')
patient_profiles = PatientProfile.objects.all()
print(f'   Total: {patient_profiles.count()}')
for profile in patient_profiles[:5]:  # Show first 5
    print(f'   - {profile.user.first_name} {profile.user.last_name}')

# Consultations
print('\n📅 CONSULTATIONS:')
consultations = Consultation.objects.all()
print(f'   Total: {consultations.count()}')
for consult in consultations[:5]:
    print(f'   - {consult.patient.first_name} with Dr. {consult.doctor.first_name} - Status: {consult.status}')

# Consultation Requests
print('\n📋 CONSULTATION REQUESTS:')
requests = ConsultationRequest.objects.all()
print(f'   Total: {requests.count()}')

# Doctor Availability
print('\n🗓️ DOCTOR AVAILABILITY:')
availability = DoctorAvailability.objects.all()
print(f'   Total Slots: {availability.count()}')

# Prescriptions
print('\n💊 PRESCRIPTIONS:')
prescriptions = Prescription.objects.all()
print(f'   Total: {prescriptions.count()}')
for rx in prescriptions[:5]:
    medicines_count = rx.medicines.count()
    verified = '✅' if rx.is_verified else '❌'
    print(f'   {verified} Patient: {rx.patient.first_name}, Medicines: {medicines_count}, Verified: {rx.is_verified}')

# Prescription Medicines
print('\n💉 PRESCRIPTION MEDICINES:')
medicines = PrescriptionMedicine.objects.all()
print(f'   Total: {medicines.count()}')

print('\n' + '='*80)
print('VERIFICATION COMPLETE')
print('='*80)

if 'postgresql' in db_config['ENGINE']:
    print('\n✅ SUCCESS: All data is being fetched from Supabase PostgreSQL database!')
    print(f'📊 Total records found: {total_users + doctor_profiles.count() + patient_profiles.count() + consultations.count() + prescriptions.count()}')
else:
    print('\n⚠️  WARNING: Still using local SQLite database!')
    print('   Please check USE_LOCAL_DB setting in .env file')
