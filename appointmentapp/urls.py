from django.urls import path
from . import views
urlpatterns = [
    path("book/new/appointment", views.create_user,name="book_appointment"),
    path("create/user", views.myView),
    path("home/", views.homePage,name='home'),
    path('login/', views.login_view, name='login'),
    path('doctor/dashboard', views.doctor_dashboard, name='doctor_dashboard'),
]