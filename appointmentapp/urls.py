from django.urls import path, include
from django.contrib.auth.views import LoginView,LogoutView
from . import views
from .views import customLoginView

urlpatterns = [
    # Homepage URL
    path("", views.homePage, name='home'),
    path('about/us', views.aboutUs, name='about_us'),
    # path('contact/us', views.contactUs, name='contact_us'),
    # path('services', views.services, name='services'),
    # path('contact', views.contactUs, name='contact_us'),
    # path('test/home/', views.testHome, name='test_home'),



    
    # Common URL
    path('login/', customLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'), 



    # Patients URL
    path("book/new/appointment", views.bookNewAppointment, name="book_appointment"),
    path('cancel/appointment/<id>', views.cancelAppointment, name='cancel_appointment'),
    path('ajax/fetch/time', views.ajaxFetchTime, name='ajax_fetch_time_from_date'),
    path('ajax/fetch/appointment', views.ajaxFetchAppointment, name='ajax_fetch_appointment'),
    path('test/home/', views.testHome, name='test_home'),
    path('book/appointment/', views.bookAppointment, name='book_appointment'),
    path('get-doctors/<int:spec_id>/', views.getDoctorsBySpecialization, name='get_doctors_by_specialization'),
    path('get-doctor-form/<int:doctor_id>/', views.getDoctorForm, name='get_doctor_form'),  



    # Doctor URL
    path('doctor/', include('appointmentapp.doctor_urls')),

    # Admin URL
    path('dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('manage/doctor/specializations/', views.manageDoctorSpecializations, name='manage_doctor_specializations'),
    path('add/specializations/', views.addSpecializations, name='add_specializations'),
]
