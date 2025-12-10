# Delete old tables if they exist

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_alter_medicalrecord_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS authentication_patientqrcode CASCADE;",
            reverse_sql="",
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS authentication_qrcodescanlog CASCADE;",
            reverse_sql="",
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS patient_qr_codes CASCADE;",
            reverse_sql="",
        ),
    ]
