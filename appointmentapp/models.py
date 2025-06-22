from django.db import models
from django.contrib.auth.models import User
from django_mysql.models import EnumField


class StatusEnum(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    RESCHEDULED = 'rescheduled', 'Rescheduled'


class PatientBookAppointment(models.Model):
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    patient_type = EnumField(choices=[
        ('new', 'New'),
        ('old', 'Old')
    ], default='new')
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    is_deleted = models.BooleanField(default=False)

    # Rescheduled time/date
    reschedule_time = models.TimeField(null=True, blank=True)
    reschedule_date = models.DateField(null=True, blank=True)

    # Prescription file (PDF, image, etc.)
    prescription_file = models.FileField(
        upload_to='prescriptions/', null=True, blank=True)

    # Appointment status
    status = EnumField(choices=StatusEnum.choices, default='scheduled')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_book_appointment'
        unique_together = ('appointment_date', 'appointment_time', 'patient', 'doctor')

    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} on {self.appointment_date} at {self.appointment_time} status {self.status}"


class DoctorAvailabilities(models.Model):
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='schedule')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = EnumField(choices=StatusEnum.choices,
                       default=StatusEnum.SCHEDULED)
    maximum_patient = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slot_duration = models.PositiveIntegerField(default=15)
    class Meta:
        db_table = 'doctor_availabilities'
        unique_together = ('doctor', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.doctor.username} - {self.date} from {self.start_time} to {self.end_time}"


class DoctorSpecializations(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    doctors = models.ManyToManyField(User, related_name="specializations")
    serviceLogo = models.ImageField(
        upload_to='specializations/', null=True, blank=True)
    status = EnumField(choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deleted', 'Deleted'),
    ], default='active')

    class Meta:
        db_table = 'doctor_specializations'

    def __str__(self):
        return self.name


class UserDetails(models.Model):
    ROLE_CHOICES = [
        ('role_doctor', 'Role_Doctor'),
        ('role_patient', 'Role_Patient'),
        ('role_admin', 'Role_Admin'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='details')
    role = EnumField(choices=ROLE_CHOICES, default='role_patient')
    phone_number = models.TextField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    guardian_name = models.CharField(max_length=255, null=True)
    gender = EnumField(choices=[
        ('female', 'Female'),
        ('male', 'Male'),
        ('others', 'Others'),
    ], null=True, blank=True)

    status = EnumField(choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deleted', 'Deleted'),
    ], default='active')

    profile_pic = models.ImageField(
        upload_to='profile/', null=True, blank=True)
    patient_id = models.CharField(max_length=255, null=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    qualification = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_details'

    def __str__(self):
        return f"User: {self.user.username}, Role: {self.role}, Phone: {self.phone_number}"


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_contact'

    def __str__(self):
        return f"{self.name} - {self.email}"
