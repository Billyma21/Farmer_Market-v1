# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register_farmer/', views.register_farmer, name='register_farmer'),
    path('register_customer/', views.register_customer, name='register_customer'),
]
