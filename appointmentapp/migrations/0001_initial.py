from django.db import migrations

def rename_and_add_fields(apps, schema_editor):
    # Rename 'username' to 'patient_id' in the auth_user table
    schema_editor.execute("""
        ALTER TABLE auth_user RENAME COLUMN username TO patient_id;
    """)

    # Rename 'date_joined' to 'created_at' in the auth_user table
    schema_editor.execute("""
        ALTER TABLE auth_user RENAME COLUMN date_joined TO created_at;
    """)

    # Add new fields to the auth_user table
    schema_editor.execute("""
        ALTER TABLE auth_user ADD COLUMN role VARCHAR(255) NULL;
        ALTER TABLE auth_user ADD COLUMN phone_number VARCHAR(255) NULL;
        ALTER TABLE auth_user ADD COLUMN address TEXT NULL;
        ALTER TABLE auth_user ADD COLUMN gender VARCHAR(50) NULL;
        ALTER TABLE auth_user ADD COLUMN guardian_name VARCHAR(255) NULL;
    """)

    # Add unique constraint for the patient_id field (which was previously 'username')
    schema_editor.execute("""
        CREATE UNIQUE INDEX idx_patient_id ON auth_user (patient_id);
    """)

def reverse_rename_and_add_fields(apps, schema_editor):
    # Rollback changes by reversing the above SQL operations

    # Remove the unique index on 'patient_id'
    schema_editor.execute("""
        DROP INDEX IF EXISTS idx_patient_id;
    """)

    # Remove new columns
    schema_editor.execute("""
        ALTER TABLE auth_user DROP COLUMN role;
        ALTER TABLE auth_user DROP COLUMN phone_number;
        ALTER TABLE auth_user DROP COLUMN address;
        ALTER TABLE auth_user DROP COLUMN gender;
        ALTER TABLE auth_user DROP COLUMN guardian_name;
    """)

    # Rename 'patient_id' back to 'username'
    schema_editor.execute("""
        ALTER TABLE auth_user RENAME COLUMN patient_id TO username;
    """)

    # Rename 'created_at' back to 'date_joined'
    schema_editor.execute("""
        ALTER TABLE auth_user RENAME COLUMN created_at TO date_joined;
    """)

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),  # Ensure this is the correct dependency
    ]

    operations = [
        migrations.RunPython(rename_and_add_fields, reverse_code=reverse_rename_and_add_fields, atomic=False),
    ]

