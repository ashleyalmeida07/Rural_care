"""Check which doctors have profiles"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from authentication.models import User

doctors = User.objects.filter(user_type='doctor', is_active=True)
print(f'\n📊 Total Active Doctors: {doctors.count()}\n')

for d in doctors:
    try:
        profile = d.doctor_profile
        has_profile = True
        spec = profile.specialization or 'Not set'
    except:
        has_profile = False
        spec = 'N/A'
    
    print(f'{"✅" if has_profile else "❌"} {d.first_name} {d.last_name}')
    print(f'   Email: {d.email}')
    print(f'   Profile: {has_profile}')
    print(f'   Specialization: {spec}')
    print()
