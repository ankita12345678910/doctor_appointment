# Generated by Django 5.1.3 on 2025-02-24 18:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("appointmentapp", "0010_alter_doctorschedule_table"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DoctorSchedule",
            new_name="DoctorAvailabilities",
        ),
    ]
