from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.db import connection
from .models import Appointment
from .models import DoctorSchedule
import uuid
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required

def homePage(request):
    return render(request,"home/index.html")

def login_view(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        role='doctor'
        doctor_user=User.objects.raw('Select * from auth_user where role=%s and username=%s',[role,email])[0]
        user=authenticate(request,username=email,password=password)
        if doctor_user is not None and user is not None:
            login(request, user)
            return redirect('doctor_dashboard')
        else:
            error="Only a doctor can login"
            return render(request, 'login/login.html', {'error': error})
       
    return render(request,"login.html")

@login_required 
def doctor_dashboard(request):
    return render(request, 'doctor/doctor_dashboard.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def myView(request):
    user = User.objects.filter(id=1).first()
    return render(request,"user/book_new_appointment.html",{
        'user':user
    })

def bookAppointment(request):
    user_id= User.objects.filter(id=1).first()
    doctor_schedule=DoctorSchedule.objects.filter(doctor_id=user_id)
    if request.method == 'POST':
        patient_id=request.POST.get('patient_id')
        if patient_id:
            user=User.objects.raw('Select * from auth_user where patient_id=%s',[patient_id])[0]
        else:
            first_name = request.POST.get('patient_first_name')
            last_name = request.POST.get('patient_last_name')
            email = request.POST.get('email')
            role = 'patient'
            phone_number = request.POST.get('mobile_number')
            address = request.POST.get('address')
            gender = request.POST.get('gender')
            guardian_name = request.POST.get('guardian_name')
        
            if email and phone_number:
                patient_id = 'P' + uuid.uuid4().hex[:6].upper() 
                user = User.objects.create_user(
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=phone_number
                )
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE auth_user
                    SET role = %s,
                        phone_number = %s,
                        address = %s,
                        gender = %s,
                        guardian_name = %s,
                        patient_id = %s
                    WHERE id = %s
                """, [role, phone_number, address, gender, guardian_name, patient_id, user.id])

        doctor_id = request.POST.get('doctor') 
        patient_type = request.POST.get('patient_type')     
        appointment_date = datetime.strptime(request.POST.get('appointment_date'), '%m/%d/%Y').date()
        appointment_time = datetime.strptime(request.POST.get('appointment_time') ,'%I:%M %p').time()
        doctor =  User.objects.get(id=doctor_id)
        appointment=Appointment.objects.create(
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        patient_type=patient_type,
        patient=user,
        doctor=doctor   
        )
        return render(request, 'user/book_new_appointment.html')
    return render(request, 'user/book_new_appointment.html',{
        'doctor': user_id,
        'doctor_schedule': doctor_schedule,
    })

def manageSchedule(request, id=None):
    
    if id == str(-1):
        title = "Add New Schedule"
        button_text = "Add"
        schedule = None
    else:
        title = "Edit Schedule"
        button_text = "Update"
        # Using raw SQL query
        schedules = DoctorSchedule.objects.raw("SELECT * FROM doctor_schedule WHERE id=%s AND doctor_id=%s", [id, request.user.id])
        schedule = schedules[0] if schedules else None

    if request.method == 'POST':
        schedule_date = request.POST.get('date')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')
        if schedule_date and start_time and end_time:
            if schedule:
                # Update existing schedule
                schedule.date = schedule_date
                schedule.start_time = start_time
                schedule.end_time = end_time
                schedule.save()
            else:
                # Create new schedule
                schedule = DoctorSchedule.objects.create(
                    date=schedule_date,
                    start_time=start_time,
                    end_time=end_time,
                    doctor=request.user
                )
            return redirect('doctor_dashboard')  # Redirect to a relevant page after saving

    return render(request, 'doctor/manage_schedule.html', {
        'id': id,
        'title': title,
        'schedule': schedule,
        'button_text': button_text
    })
