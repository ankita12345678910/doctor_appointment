from django.db import models
from django.contrib.auth.models import User

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
    class Meta: db_table = 'patient_appointment'
    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} on {self.appointment_date} at {self.appointment_time}"
    
class DoctorSchedule(models.Model):
    doctor=models.ForeignKey(User,on_delete=models.CASCADE,related_name='schedule')
    date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    class Meta:
        db_table='doctor_schedule'
        unique_together=('doctor','date','start_time','end_time')
    def __str__(self):
        return f"{self.doctor.username} - {self.date} from {self.start_time} to {self.end_time}"