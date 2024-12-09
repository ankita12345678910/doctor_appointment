from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import connection
from .models import Appointment
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

def myView(request):
    user = User.objects.filter(id=1).first()
    return render(request,"user/book_new_appointment.html",{
        'user':user
    })

def create_user(request):
    user_id= User.objects.filter(id=1).first()
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
        'user':user_id
    })