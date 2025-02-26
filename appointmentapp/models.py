from django.db import models
from django.contrib.auth.models import User
from django_mysql.models import EnumField

class StatusEnum(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    RESCHEDULED = 'rescheduled', 'Rescheduled'

class Appointment(models.Model):
    APPOINTMENT_TYPES = [
        ('new', 'New'),
        ('old', 'Old'),
    ]

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    patient_type = models.CharField(max_length=10, choices=APPOINTMENT_TYPES)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        db_table = 'patient_book_appointment'
    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} on {self.appointment_date} at {self.appointment_time}"


class DoctorAvailabilities(models.Model):
    doctor = models.ForeignKey(User,on_delete=models.CASCADE, related_name= 'schedule')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = EnumField(choices=StatusEnum.choices, default=StatusEnum.SCHEDULED)
    maximum_patient = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table='doctor_availabilities'
        unique_together=('doctor','date','start_time','end_time')
    def __str__(self):
        return f"{self.doctor.username} - {self.date} from {self.start_time} to {self.end_time}"
    
class DoctorSpecializations(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    doctors = models.ManyToManyField(User,related_name="specializations")
    
    class Meta:
        db_table='doctor_specializations'
        
    def __str__(self):
        return self.name