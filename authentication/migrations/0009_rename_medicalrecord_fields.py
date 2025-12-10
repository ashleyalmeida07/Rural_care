# Rename MedicalRecord columns

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_rename_qrcodescanlog_table'),
    ]

    operations = [
        # Rename record_type to document_type
        migrations.RenameField(
            model_name='medicalrecord',
            old_name='record_type',
            new_name='document_type',
        ),
        # Rename file to document_file
        migrations.RenameField(
            model_name='medicalrecord',
            old_name='file',
            new_name='document_file',
        ),
        # Drop description column if it exists (it's not in the new model)
        migrations.RemoveField(
            model_name='medicalrecord',
            name='description',
        ),
    ]
