from django.conf import settings
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import customLoginView
from django.conf.urls.static import static


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
    path('patient/', include('appointmentapp.patient_urls')),

    # Doctor URL
    path('doctor/', include('appointmentapp.doctor_urls')),

    # Admin URL
    path('dashboard/', views.adminDashboard, name='admin_dashboard'), 
    path('manage/doctor/specializations/', views.manageDoctorSpecializations, name='manage_doctor_specializations'),
    path('add/specializations/', views.addSpecializations, name='add_specializations'),
    path('edit/specializations/<int:id>/', views.editSpecialization, name='edit_specializations'),
    path('delete/specializations/<int:id>/', views.deleteSpecialization, name='delete_specializations'),

    path('manage/doctors', views.manageDoctors, name="manage_doctors"),
    path('add/doctors', views.addDoctors, name='add_doctors')
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
