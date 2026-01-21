# Generated manually to fix id column type mismatch

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_fix_doctorkyc_schema'),
    ]

    operations = [
        # Step 1: Drop foreign key constraint on verified_by if exists (references to users table)
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Drop the old verified_by column (character varying) if it exists
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'doctor_kyc' AND column_name = 'verified_by' AND data_type = 'character varying') THEN
                    ALTER TABLE doctor_kyc DROP COLUMN verified_by;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 2: Alter the id column from bigint to uuid
        migrations.RunSQL(
            sql="""
            -- Create extension if not exists
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            
            -- First, we need to create a new uuid column
            ALTER TABLE doctor_kyc ADD COLUMN new_id uuid DEFAULT uuid_generate_v4();
            
            -- Update the new_id with generated UUIDs for existing rows
            UPDATE doctor_kyc SET new_id = uuid_generate_v4() WHERE new_id IS NULL;
            
            -- Drop the old primary key constraint
            ALTER TABLE doctor_kyc DROP CONSTRAINT IF EXISTS doctor_kyc_pkey;
            
            -- Drop the old id column
            ALTER TABLE doctor_kyc DROP COLUMN id;
            
            -- Rename new_id to id
            ALTER TABLE doctor_kyc RENAME COLUMN new_id TO id;
            
            -- Set the new id as primary key
            ALTER TABLE doctor_kyc ADD PRIMARY KEY (id);
            
            -- Remove the default (Django will handle UUID generation)
            ALTER TABLE doctor_kyc ALTER COLUMN id DROP DEFAULT;
            """,
            reverse_sql="""
            -- This is a destructive change, reverse would need careful consideration
            -- For now, just leave it as a placeholder
            SELECT 1;
            """,
        ),
    ]
