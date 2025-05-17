from django.urls import path
from . import views
urlpatterns = [
    # Homepage URL
    path("", views.homePage, name='home'),
    path('about/us', views.aboutUs, name='about_us'),
    # path('contact/us', views.contactUs, name='contact_us'),
    # path('services', views.services, name='services'),
    # path('contact', views.contactUs, name='contact_us'),
    # path('test/home/', views.testHome, name='test_home'),
    
    path("book/new/appointment", views.bookAppointment, name="book_appointment"),
    path('login/', views.login_view, name='login'),
    path('doctor/dashboard', views.doctor_dashboard, name='doctor_dashboard'),
    path('logout/', views.logout_user, name='logout'),
    path('manage/schedule/<id>', views.manageSchedule, name='manage_schedule'),
    path('cancel/appointment/<id>', views.cancelAppointment, name='cancel_appointment'),
    path('ajax/fetch/time', views.ajaxFetchTime, name='ajax_fetch_time_from_date'),
    path('ajax/fetch/appointment', views.ajaxFetchAppointment, name='ajax_fetch_appointment'),
]
