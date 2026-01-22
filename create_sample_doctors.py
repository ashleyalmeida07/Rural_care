"""Create sample doctors for testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from authentication.models import User, DoctorProfile
from django.contrib.auth.hashers import make_password

# Sample doctors data
sample_doctors = [
    {
        'username': 'dr_sarah_patel',
        'email': 'sarah.patel@ruralcare.com',
        'first_name': 'Sarah',
        'last_name': 'Patel',
        'specialization': 'medical_oncology',
        'license': 'MH-ONC-2023-45678',
        'hospital': 'RuralCare Cancer Institute',
        'phone': '+91-9876543211',
        'experience': 12,
        'degree': 'MBBS, MD (Oncology), DM (Medical Oncology)',
        'bio': 'Specialized in chemotherapy and targeted therapy for solid tumors. Over 12 years of experience in medical oncology.',
    },
    {
        'username': 'dr_rajesh_kumar',
        'email': 'rajesh.kumar@ruralcare.com',
        'first_name': 'Rajesh',
        'last_name': 'Kumar',
        'specialization': 'surgical_oncology',
        'license': 'MH-SURG-2022-34567',
        'hospital': 'RuralCare Medical Center',
        'phone': '+91-9876543212',
        'experience': 15,
        'degree': 'MBBS, MS (Surgery), MCh (Surgical Oncology)',
        'bio': 'Expert in oncological surgeries including breast, gastrointestinal, and head & neck cancer surgeries.',
    },
    {
        'username': 'dr_priya_sharma',
        'email': 'priya.sharma@ruralcare.com',
        'first_name': 'Priya',
        'last_name': 'Sharma',
        'specialization': 'radiation_oncology',
        'license': 'MH-RAD-2021-23456',
        'hospital': 'RuralCare Radiation Center',
        'phone': '+91-9876543213',
        'experience': 10,
        'degree': 'MBBS, MD (Radiation Oncology)',
        'bio': 'Specializes in advanced radiation therapy techniques including IMRT, IGRT, and stereotactic radiotherapy.',
    },
    {
        'username': 'dr_amit_desai',
        'email': 'amit.desai@ruralcare.com',
        'first_name': 'Amit',
        'last_name': 'Desai',
        'specialization': 'hematology',
        'license': 'MH-HEM-2020-12345',
        'hospital': 'RuralCare Medical Center',
        'phone': '+91-9876543214',
        'experience': 8,
        'degree': 'MBBS, MD (Internal Medicine), DM (Hematology)',
        'bio': 'Expert in blood cancers, bone marrow transplants, and hematological disorders.',
    },
    {
        'username': 'dr_kavita_reddy',
        'email': 'kavita.reddy@ruralcare.com',
        'first_name': 'Kavita',
        'last_name': 'Reddy',
        'specialization': 'pediatric_oncology',
        'license': 'MH-PED-2022-56789',
        'hospital': 'RuralCare Children\'s Hospital',
        'phone': '+91-9876543215',
        'experience': 9,
        'degree': 'MBBS, MD (Pediatrics), DM (Pediatric Oncology)',
        'bio': 'Dedicated to treating childhood cancers with compassionate care and latest treatment protocols.',
    },
]

print('\n🏥 Creating Sample Doctors...\n')

for doc_data in sample_doctors:
    # Check if user already exists
    if User.objects.filter(email=doc_data['email']).exists():
        print(f'⏭️  Skipping {doc_data["first_name"]} {doc_data["last_name"]} - already exists')
        continue
    
    # Create user
    user = User.objects.create(
        username=doc_data['username'],
        email=doc_data['email'],
        first_name=doc_data['first_name'],
        last_name=doc_data['last_name'],
        user_type='doctor',
        is_active=True,
        password=make_password('Doctor@123')  # Default password
    )
    
    # Create doctor profile
    profile = DoctorProfile.objects.create(
        user=user,
        specialization=doc_data['specialization'],
        license_number=doc_data['license'],
        hospital_affiliation=doc_data['hospital'],
        hospital_phone=doc_data['phone'],
        years_of_experience=doc_data['experience'],
        medical_degree=doc_data['degree'],
        bio=doc_data['bio'],
        is_verified=True,
        profile_completed=True,
        city='Mumbai',
        state='Maharashtra',
        country='India',
    )
    
    print(f'✅ Created: Dr. {doc_data["first_name"]} {doc_data["last_name"]} - {dict(DoctorProfile.SPECIALIZATION_CHOICES).get(doc_data["specialization"])}')
    print(f'   Email: {doc_data["email"]}')
    print(f'   Password: Doctor@123')
    print()

print('\n✅ Sample doctors created successfully!')
print('\n💡 Default password for all doctors: Doctor@123')
print('🔍 Doctors can now be found on the patient portal.')
