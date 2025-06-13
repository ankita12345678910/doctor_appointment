from django.urls import path
from . import views

urlpatterns = [
    path('doctor/dashboard', views.doctorDashboard, name='doctor_dashboard'),
    path('manage/schedule/<id>', views.manageSchedule, name='manage_schedule'),
]