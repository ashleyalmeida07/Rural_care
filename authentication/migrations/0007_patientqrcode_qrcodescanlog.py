# Generated migration for QR code models - CORRECTED

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_delete_old_qr_tables'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientQRCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('encrypted_token', models.CharField(db_index=True, max_length=255, unique=True)),
                ('qr_code_image', models.ImageField(upload_to='patient_qr_codes/', blank=True, null=True)),
                ('qr_code_url', models.URLField(blank=True, max_length=500, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')], default='active', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('regenerated_at', models.DateTimeField(auto_now=True, blank=True, null=True)),
                ('last_scanned_at', models.DateTimeField(blank=True, null=True)),
                ('last_scanned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scanned_patient_qr_codes', to=settings.AUTH_USER_MODEL)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='qr_code', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Patient QR Code',
                'verbose_name_plural': 'Patient QR Codes',
                'ordering': ['-created_at'],
                'db_table': 'patient_qr_codes',
            },
        ),
        migrations.CreateModel(
            name='QRCodeScanLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scan_timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('access_granted', models.BooleanField(default=True)),
                ('denial_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qr_scan_logs_as_patient', to=settings.AUTH_USER_MODEL)),
                ('qr_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scan_logs', to='authentication.patientqrcode')),
                ('scanned_by', models.ForeignKey(limit_choices_to={'user_type': 'doctor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='qr_scans_performed', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'QR Code Scan Log',
                'verbose_name_plural': 'QR Code Scan Logs',
                'ordering': ['-scan_timestamp'],
            },
        ),
    ]
