# Generated by Django 5.1.3 on 2025-02-24 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("appointmentapp", "0009_doctorschedule_created_at_and_more"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="doctorschedule",
            table="doctor_availabilities",
        ),
    ]
