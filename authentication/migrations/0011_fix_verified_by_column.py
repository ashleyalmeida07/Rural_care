# Fix verified_by_id double suffix

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_refactor_doctorkyc_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE doctor_kyc RENAME COLUMN verified_by_id_id TO verified_by_id;",
            reverse_sql="ALTER TABLE doctor_kyc RENAME COLUMN verified_by_id TO verified_by_id_id;",
        ),
    ]
