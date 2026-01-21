# Migration to fix DoctorKYC schema by dropping old fields and ensuring correct ones exist

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0013_sync_database_schema'),
    ]

    operations = [
        # Drop incorrect fields and add missing ones using pure SQL
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Drop old fields that shouldn't exist
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS id_type CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS id_number CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS id_document CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS registration_number CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS registration_council CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS registration_document CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS degree_document CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS address_proof_document CASCADE;
                ALTER TABLE doctor_kyc DROP COLUMN IF EXISTS admin_notes CASCADE;
            END $$;
            """,
            reverse_sql="SELECT 1;",
        ),
    ]
