from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import connection
from .models import PatientBookAppointment, DoctorAvailabilities, DoctorSpecializations, UserDetails
import uuid
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib import messages


# Homepage actions
def homePage(request):
    return render(request, "home/homepage.html")


def aboutUs(request):
    return render(request, "home/about_us.html")


def testHome(request):
    return render(request, "home/test_home.html")


# login Actions
class customLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        try:
            role = user.details.role
        except UserDetails.DoesNotExist:
            role = None

        if role == 'role_doctor':
            return reverse_lazy('doctor_dashboard')
        elif role == 'role_admin':
            return reverse_lazy('admin_dashboard')
        else:
            # or raise an error / send to default page
            return reverse_lazy('home')


# doctor actions
@login_required
def doctorDashboard(request):
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
@csrf_exempt
def bookAppointment(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user = None  # Initialize user
                patient_id = request.POST.get('patient_id')

                if patient_id:
                    user_details = get_object_or_404(
                        UserDetails, patient_id=patient_id)
                    user = user_details.user
                else:
                    first_name = request.POST.get('patient_first_name')
                    last_name = request.POST.get('patient_last_name')
                    email = request.POST.get('email')
                    phone_number = request.POST.get('mobile_number')
                    address = request.POST.get('address')
                    gender = request.POST.get('gender')
                    guardian_name = request.POST.get('guardian_name')

                    # Validate essential fields
                    if not all([first_name, last_name, email, phone_number, address, gender, guardian_name]):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Please fill in all required fields.'
                        })

                    generated_patient_id = 'P' + uuid.uuid4().hex[:6].upper()
                    user = User.objects.create_user(
                        username=email,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=phone_number
                    )

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

                if not user:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'User creation failed. Please check the form and try again.'
                    })

                doctor_id = request.POST.get('doctor_id')
                patient_type = request.POST.get('patient_type')
                appointment_date_str = request.POST.get('appointment_date')
                appointment_time_str = request.POST.get('appointment_time')

                # Validate appointment fields
                if not all([doctor_id, patient_type, appointment_date_str, appointment_time_str]):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Appointment date, time, doctor, and patient type are required.'
                    })

                appointment_date = datetime.strptime(
                    appointment_date_str, '%m/%d/%Y').date()
                appointment_time = datetime.strptime(
                    appointment_time_str, '%H:%M').time()
                doctor = get_object_or_404(User, id=doctor_id)

                PatientBookAppointment.objects.create(
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    patient_type=patient_type,
                    patient=user,
                    doctor=doctor
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Appointment booked successfully!',
                    'patient_id': patient_id,
                    'patient_name': f"{user.first_name} {user.last_name}"
                })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        specializations = DoctorSpecializations.objects.filter(status='active')
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


def getDoctorsBySpecialization(request, spec_id):
    try:
        spec = DoctorSpecializations.objects.get(id=spec_id, status='active')
        doctors = spec.doctors.filter(
            details__role='role_doctor').select_related('details')

        html = render(request, 'partials/doctor_cards.html',
                      {'doctors': doctors}).content.decode('utf-8')
        return JsonResponse({'html': html})

    except DoctorSpecializations.DoesNotExist:
        return JsonResponse({'html': '<p>Specialization not found.</p>'}, status=404)


def getDoctorForm(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id)

    doctor_schedule = DoctorAvailabilities.objects.filter(
        doctor=doctor).order_by('date')

    return render(request, 'partials/appointment_form.html', {
        'doctor': doctor,
        'doctor_schedule': doctor_schedule,
    })


# Admin Actions
@login_required
def adminDashboard(request):
    return render(request, 'admin/admin_dashboard.html', {
        'title': 'Dashboard',
    })


@login_required
def manageDoctorSpecializations(request):
    try:
        specializations = DoctorSpecializations.objects.filter(
            status='Active').order_by('-created_at')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return render(request, 'admin/manage_doctor_specializations.html', {
        'title': 'Manage Specializations',
        'specializations': specializations
    })


@login_required
@require_POST
def addSpecializations(request):
    try:
        if request.method == 'POST':
            DoctorSpecializations.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                serviceLogo=request.FILES.get(
                    'logo')  # handle file upload here
            )
            messages.success(request, 'Specialization added successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_doctor_specializations')


@login_required
@require_POST
def editSpecialization(request, id):
    try:
        specialization = get_object_or_404(DoctorSpecializations, id=id)

        if request.method == 'POST':
            specialization.name = request.POST.get('name')
            specialization.description = request.POST.get('description')

            if 'logo' in request.FILES:
                specialization.serviceLogo = request.FILES.get('logo')
            specialization.save()
            messages.success(request, 'Specialization Updated SUccessfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_doctor_specializations')


@require_POST
@login_required
def deleteSpecialization(request, id):
    try:
        if request.method == 'POST':
            specialization = get_object_or_404(DoctorSpecializations, id=id)
            specialization.status = 'Deleted'
            specialization.save()
            messages.success(request, 'Specialization Removed Successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_doctor_specializations')


@login_required
def manageDoctors(request):
    try:
        specializations = DoctorSpecializations.objects.filter(
            status='Active').order_by('-created_at')
        doctors = User.objects.filter(details__status='Active', is_active=True).select_related(
            'details')  # Use lowercase related model name
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return render(request, 'admin/manage_doctors.html', {
        'title': 'Manage Doctors',
        'specializations': specializations if specializations else "",
        'doctors': doctors,
    })


@login_required
@require_POST
def addDoctors(request):
    try:
        if request.method == 'POST':
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("first_name")
            email = request.POST.get("email")
            password = request.POST.get("phone_number")

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return render(request, "admin/manage_doctors.html", {"error": "Email already registered!"})

            # Create User object
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=make_password(password),  # Hash the password
            )

            # Create UserProfile object
            UserDetails.objects.create(
                user=user,
                role='Role_Doctor',  # EnumField stores the selected role
                gender=request.POST.get('gender'),
                address=request.POST.get('address'),
                phone_number=request.POST.get('phone_number'),
                status='Active',
            )
            messages.success(request, 'Doctors Added Successfully!')
        else:
            messages.success(request, 'Something went Wrong')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('manage_doctors')


@login_required
@require_POST
def deleteDoctor(request, id):
    try:
        doctor = get_object_or_404(User, id=id)
        # Update the status in the related UserDetails model
        if hasattr(doctor, 'details'):
            doctor.details.status = 'Deleted'
            doctor.details.save()
            messages.success(request, 'Specialization Removed Successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('manage_doctors')
