# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterFarmerForm, RegisterCustomerForm
from .models import User

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_farmer:
                return redirect('farmer_dashboard')  # Rediriger fermier vers son tableau de bord
            return redirect('home')  # Rediriger client vers la page d'accueil
        else:
            messages.error(request, "Identifiants invalides")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_farmer(request):
    if request.method == 'POST':
        form = RegisterFarmerForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_farmer = True  # Marquer l'utilisateur comme fermier
            user.save()
            login(request, user)  # Connexion automatique après l'inscription
            return redirect('farmer_dashboard')  # Redirection vers le tableau de bord du fermier
    else:
        form = RegisterFarmerForm()
    return render(request, 'accounts/register_farmer.html', {'form': form})

def register_customer(request):
    if request.method == 'POST':
        form = RegisterCustomerForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_customer = True  # Marquer l'utilisateur comme client
            user.save()
            login(request, user)  # Connexion automatique après l'inscription
            return redirect('home')  # Redirection vers la page d'accueil
    else:
        form = RegisterCustomerForm()
    return render(request, 'accounts/register_customer.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirection vers la page d'accueil après la déconnexion
