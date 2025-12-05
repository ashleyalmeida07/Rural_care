# Generated migration for cancer_detection app

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CancerImageAnalysis',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='cancer_images/%Y/%m/%d/')),
                ('image_type', models.CharField(choices=[('xray', 'X-Ray Scan'), ('ct', 'CT Scan'), ('mri', 'MRI Scan'), ('tumor', 'Tumor Image'), ('biopsy', 'Biopsy Image'), ('ultrasound', 'Ultrasound'), ('other', 'Other')], default='other', max_length=20)),
                ('original_filename', models.CharField(max_length=255)),
                ('tumor_detected', models.BooleanField(default=False)),
                ('tumor_type', models.CharField(blank=True, max_length=100, null=True)),
                ('tumor_stage', models.CharField(blank=True, max_length=50, null=True)),
                ('tumor_size_mm', models.FloatField(blank=True, null=True)),
                ('tumor_location', models.CharField(blank=True, max_length=200, null=True)),
                ('genetic_profile', models.JSONField(blank=True, default=dict)),
                ('comorbidities', models.JSONField(blank=True, default=list)),
                ('analysis_data', models.JSONField(blank=True, default=dict)),
                ('detection_confidence', models.FloatField(default=0.0)),
                ('stage_confidence', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cancer_analyses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cancer_image_analyses',
                'ordering': ['-created_at'],
            },
        ),
    ]
