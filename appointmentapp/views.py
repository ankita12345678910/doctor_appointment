from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import connection
from .models import PatientBookAppointment
from .models import DoctorAvailabilities, DoctorSpecializations, UserDetails
import uuid
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import transaction

# Homepage actions


def homePage(request):
    return render(request, "home/homepage.html")


def aboutUs(request):
    return render(request, "home/about_us.html")


def testHome(request):
    return render(request, "home/test_home.html")

# doctor actions
# ________________________________________________________________________________


@login_required
def doctor_dashboard(request):
    return render(request, 'doctor/doctor_dashboard.html')


def manageSchedule(request, id=None):

    if id == str(-1):
        title = "Add New Schedule"
        button_text = "Add"
        schedule = None
    else:
        title = "Edit Schedule"
        button_text = "Update"
        schedules = DoctorAvailabilities.objects.raw(
            "SELECT * FROM doctor_schedule WHERE id=%s AND doctor_id=%s", [id, request.user.id])
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
                schedule = DoctorAvailabilities.objects.create(
                    date=schedule_date,
                    start_time=start_time,
                    end_time=end_time,
                    doctor=request.user
                )
            # Redirect to a relevant page after saving
            return redirect('doctor_dashboard')

    return render(request, 'doctor/manage_schedule.html', {
        'id': id,
        'title': title,
        'schedule': schedule,
        'button_text': button_text
    })

# patient actions
# ________________________________________________________________________________


def book_appointment(request):
    specializations = DoctorSpecializations.objects.filter(status='active')

    if request.method == 'POST':
        with transaction.atomic():
            patient_id = request.POST.get('patient_id')

            if patient_id:
                # Look up existing patient by patient_id
                user_details = get_object_or_404(
                    UserDetails, patient_id=patient_id)
                user = user_details.user
            else:
                # Create a new patient
                first_name = request.POST.get('patient_first_name')
                last_name = request.POST.get('patient_last_name')
                email = request.POST.get('email')
                phone_number = request.POST.get('mobile_number')
                address = request.POST.get('address')
                gender = request.POST.get('gender')
                guardian_name = request.POST.get('guardian_name')

                if email and phone_number:
                    generated_patient_id = 'P' + uuid.uuid4().hex[:6].upper()

                    # Create user
                    user = User.objects.create_user(
                        username=email,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=phone_number
                    )

                    # Create related user details
                    UserDetails.objects.create(
                        user=user,
                        role='role_patient',
                        phone_number=phone_number,
                        address=address,
                        gender=gender,
                        guardian_name=guardian_name,
                        patient_id=generated_patient_id,
                    )

                    patient_id = generated_patient_id

            # Get form fields
            doctor_id = request.POST.get('doctor_id')  # from hidden input
            patient_type = request.POST.get('patient_type')
            appointment_date = datetime.strptime(
                request.POST.get('appointment_date'), '%m/%d/%Y').date()
            appointment_time = datetime.strptime(
                request.POST.get('appointment_time'), '%H:%M').time()
            doctor = get_object_or_404(User, id=doctor_id)

            # Save appointment
            PatientBookAppointment.objects.create(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                patient_type=patient_type,
                patient=user,
                doctor=doctor
            )

            return render(request, 'user/appointment_confirmation.html', {
                'patient_id': patient_id,
                'patient_name': f"{user.first_name} {user.last_name}",
                'appointment_time': appointment_time.strftime('%I:%M %p'),
                'appointment_date': appointment_date.strftime('%m/%d/%Y'),
            })

    return render(request, 'user/book_appointment.html', {
        'specializations': specializations
    })


def ajaxFetchTime(request):
    appointment_date = request.GET.get('appointment_date')
    doctor_id = request.GET.get('doctor_id')
    if appointment_date:
        try:
            date_obj = datetime.strptime(appointment_date, '%m/%d/%Y')
            schedule = DoctorAvailabilities.objects.filter(
                doctor_id=doctor_id, date=date_obj).first()
            if schedule:
                # Convert the DoctorAvailabilities object into a dictionary
                schedule_data = {
                    'id': schedule.id,
                    'doctor_id': schedule.doctor_id,
                    'date': schedule.date.strftime('%m/%d/%Y'),
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                }

                response_data = {
                    'status': 'success',
                    'schedule': schedule_data,
                }
            else:
                response_data = {
                    'status': 'error',
                    'message': 'No schedule found for the given doctor and date'
                }
        except ValueError:
            response_data = {
                'status': 'error',
                'message': 'Invalid date format'
            }
    else:
        response_data = {
            'status': 'error',
            'message': 'No appointment date provided'
        }

    return JsonResponse(response_data)


def cancelAppointment(request, id=None):
    return render(request, 'user/cancel_appointment.html')


def ajaxFetchAppointment(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile_number')
        appointment_date_str = request.POST.get('appointment_date')
        appointment_date = datetime.strptime(
            appointment_date_str, '%m/%d/%Y').date()

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    u.id AS user_id,
                    u.patient_id, 
                    CONCAT(u.first_name, ' ', u.last_name) AS fullname, 
                    u.phone_number AS mobile, 
                    pa.appointment_date, 
                    pa.appointment_time 
                FROM auth_user u 
                INNER JOIN patient_book_appointment pa 
                ON pa.patient_id = u.id 
                WHERE u.phone_number = %s 
                AND pa.appointment_date = %s
            ''', [mobile, appointment_date])

            appointments = cursor.fetchall()
            # print(set(appointments))
            data = []
            for appointment in appointments:
                data.append({
                    'patient_id': appointment[1],
                    'fullname': appointment[2],
                    'mobile': appointment[3],
                    'appointment_date': appointment[4].strftime('%Y-%m-%d'),
                    'appointment_time': appointment[5],
                })
            return JsonResponse(data, status=200, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)


def bookNewAppointment(request):
    specializations = DoctorSpecializations.objects.filter(status='active')
    return render(request, 'user/book_appointment.html', {'specializations': specializations})


def get_doctors_by_specialization(request, spec_id):
    try:
        spec = DoctorSpecializations.objects.get(id=spec_id, status='active')
        doctors = spec.doctors.filter(
            details__role='role_doctor').select_related('details')

        html = render(request, 'partials/doctor_cards.html',
                      {'doctors': doctors}).content.decode('utf-8')
        return JsonResponse({'html': html})

    except DoctorSpecializations.DoesNotExist:
        return JsonResponse({'html': '<p>Specialization not found.</p>'}, status=404)


def get_doctor_form(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id)

    doctor_schedule = DoctorAvailabilities.objects.filter(
        doctor=doctor).order_by('date')

    return render(request, 'partials/appointment_form.html', {
        'doctor': doctor,
        'doctor_schedule': doctor_schedule,
    })
