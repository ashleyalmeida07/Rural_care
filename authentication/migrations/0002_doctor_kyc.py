# Generated migration for DoctorKYC model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorKYC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=20)),
                ('nationality', models.CharField(max_length=100)),
                ('personal_email', models.EmailField(max_length=254)),
                ('mobile_number', models.CharField(max_length=20)),
                ('residential_address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('license_number_verified', models.CharField(max_length=100)),
                ('license_issuing_authority', models.CharField(max_length=200)),
                ('license_issue_date', models.DateField()),
                ('license_expiry_date', models.DateField()),
                ('license_document', models.FileField(blank=True, null=True, upload_to='kyc/licenses/')),
                ('medical_degree', models.CharField(max_length=200)),
                ('medical_university', models.CharField(max_length=200)),
                ('graduation_year', models.IntegerField()),
                ('degree_certificate', models.FileField(blank=True, null=True, upload_to='kyc/degrees/')),
                ('current_hospital', models.CharField(blank=True, max_length=200, null=True)),
                ('designation', models.CharField(max_length=100)),
                ('department_specialty', models.CharField(max_length=100)),
                ('years_of_practice', models.IntegerField()),
                ('employment_document', models.FileField(blank=True, null=True, upload_to='kyc/employment/')),
                ('identity_document_type', models.CharField(choices=[('passport', 'Passport'), ('aadhaar', 'Aadhaar'), ('national_id', 'National ID'), ('driving_license', 'Driving License')], max_length=50)),
                ('identity_document_number', models.CharField(max_length=100)),
                ('identity_document_file', models.FileField(blank=True, null=True, upload_to='kyc/identity/')),
                ('address_proof_type', models.CharField(choices=[('utility_bill', 'Utility Bill'), ('rental_agreement', 'Rental Agreement'), ('property_deed', 'Property Deed'), ('bank_statement', 'Bank Statement')], max_length=50)),
                ('address_proof_file', models.FileField(blank=True, null=True, upload_to='kyc/address_proof/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('incomplete', 'Incomplete')], default='incomplete', max_length=20)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('verified_by', models.CharField(blank=True, max_length=200, null=True)),
                ('doctor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kyc', to='authentication.doctorprofile')),
            ],
            options={
                'verbose_name': 'Doctor KYC',
                'verbose_name_plural': 'Doctor KYCs',
                'db_table': 'doctor_kyc',
            },
        ),
    ]
