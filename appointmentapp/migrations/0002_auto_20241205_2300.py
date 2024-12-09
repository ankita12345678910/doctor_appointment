from django.db import migrations


def rename_patient_id_to_username(apps, schema_editor):
    # Get the User model from the historical state
    User = apps.get_model('auth', 'User')
    db_alias = schema_editor.connection.alias

    # Rename `patient_id` back to `username`
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE auth_user
            CHANGE patient_id username VARCHAR(150) NOT NULL UNIQUE;
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('appointmentapp', '0001_initial'),  # Adjust this to the last migration
    ]

    operations = [
        migrations.RunPython(rename_patient_id_to_username),
    ]
