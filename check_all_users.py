"""Check all users in the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from authentication.models import User

print('\n📊 ALL USERS IN DATABASE:\n')
print(f'Total Users: {User.objects.count()}\n')

patients = User.objects.filter(user_type='patient')
doctors = User.objects.filter(user_type='doctor')

print(f'👤 Patients: {patients.count()}')
for p in patients:
    print(f'   - {p.first_name} {p.last_name} ({p.email}) - Active: {p.is_active}')

print(f'\n👨‍⚕️ Doctors: {doctors.count()}')
for d in doctors:
    print(f'   - {d.first_name} {d.last_name} ({p.email}) - Active: {d.is_active}')

print('\n💡 If you need more doctors, they need to be registered in the system first!')
