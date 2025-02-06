from django.urls import path
from . import views
urlpatterns = [
    path("book/new/appointment", views.bookAppointment,name="book_appointment"),
    path("home/", views.homePage,name='home'),
    path('login/', views.login_view, name='login'),
    path('doctor/dashboard', views.doctor_dashboard, name='doctor_dashboard'),
    path('logout/', views.logout_user, name='logout'),
    path('manage/schedule/<id>', views.manageSchedule, name='manage_schedule'),
    path('cancel/appointment/<id>', views.cancelAppointment, name='cancel_appointment'),
    path('ajax/fetch/time', views.ajaxFetchTime, name='ajax_fetch_time_from_date'),
    path('ajax/fetch/appointment', views.ajaxFetchAppointment, name='ajax_fetch_appointment'),
]