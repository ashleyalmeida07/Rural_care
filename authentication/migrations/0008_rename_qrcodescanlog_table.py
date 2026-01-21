# Rename QRCodeScanLog table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_patientqrcode_qrcodescanlog'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE authentication_qrcodescanlog RENAME TO qr_code_scan_logs;",
            reverse_sql="ALTER TABLE qr_code_scan_logs RENAME TO authentication_qrcodescanlog;",
        ),
    ]
