# Refactor DoctorKYC table schema

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_rename_medicalrecord_fields'),
    ]

    operations = [
        # Drop old constraints and columns, keep data where possible
        migrations.RemoveField(
            model_name='doctorkyc',
            name='nationality',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='personal_email',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='mobile_number',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='residential_address',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='city',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='state',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='postal_code',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='country',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='license_number_verified',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='license_issuing_authority',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='license_issue_date',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='license_expiry_date',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='license_document',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='medical_degree',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='medical_university',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='graduation_year',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='degree_certificate',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='current_hospital',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='designation',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='department_specialty',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='years_of_practice',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='employment_document',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='identity_document_type',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='identity_document_number',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='identity_document_file',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='address_proof_file',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='rejection_reason',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='admin_notes',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='submitted_at',
        ),
        migrations.RemoveField(
            model_name='doctorkyc',
            name='verified_by',
        ),
        # Add new fields
        migrations.AddField(
            model_name='doctorkyc',
            name='id_type',
            field=models.CharField(choices=[('aadhar', 'Aadhar'), ('pan', 'PAN'), ('passport', 'Passport')], default='pan', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='id_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='id_document',
            field=models.FileField(default='', upload_to='doctor_kyc/id_documents/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='registration_number',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='registration_council',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='registration_document',
            field=models.FileField(default='', upload_to='doctor_kyc/registration_documents/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='degree_document',
            field=models.FileField(default='', upload_to='doctor_kyc/degree_documents/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='address_proof_document',
            field=models.FileField(default='', upload_to='doctor_kyc/address_proofs/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='bank_account_holder',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='bank_ifsc_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='verification_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doctorkyc',
            name='verified_by_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_doctors', to='authentication.user'),
        ),
    ]
