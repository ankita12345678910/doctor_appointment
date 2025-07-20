from django.urls import path
from . import views

urlpatterns = [
    path("book/new/appointment", views.bookNewAppointment, name="book_appointment"),
    path('cancel/appointment/<id>', views.cancelAppointment, name='cancel_appointment'),
    path('ajax/fetch/time', views.ajaxFetchTime, name='ajax_fetch_time_from_date'),
    path('ajax/fetch/appointment', views.ajaxFetchAppointment, name='ajax_fetch_appointment'),
    path('book/appointment/', views.bookAppointment, name='book_appointment'),
    path('get-doctors/<int:spec_id>/', views.getDoctorsBySpecialization, name='get_doctors_by_specialization'),
    path('get-doctor-form/<int:doctor_id>/', views.getDoctorForm, name='get_doctor_form'),  
]