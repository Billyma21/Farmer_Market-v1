# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from accounts.forms import RegisterFarmerForm, RegisterCustomerForm
from accounts.models import User
from products.models import Order, OrderItem, Review

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_farmer:
                return redirect('farmer_dashboard')  # Rediriger fermier vers son tableau de bord
            else:
                return redirect('customer_dashboard')  # Rediriger client vers son tableau de bord
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

@login_required
def customer_dashboard(request):
    """Tableau de bord pour les clients avec leurs commandes et informations"""
    if not request.user.is_customer:
        messages.error(request, "Vous devez être un client pour accéder à cette page.")
        return redirect('home')
    
    # Périodes pour les statistiques
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Commandes du client
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    recent_orders = orders[:5]
    
    # Statistiques
    total_spent = OrderItem.objects.filter(
        order__customer=request.user,
        order__status__in=['completed', 'ready']
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )
    
    # Commandes ce mois-ci
    orders_this_month = Order.objects.filter(
        customer=request.user,
        created_at__date__gte=start_of_month
    ).count()
    
    # Commandes en attente
    pending_orders = Order.objects.filter(
        customer=request.user,
        status__in=['pending', 'confirmed']
    ).count()
    
    # Produits favoris (les plus commandés)
    favorite_products = OrderItem.objects.filter(
        order__customer=request.user
    ).values(
        'product__id', 
        'product__name',
        'product__farmer__username'
    ).annotate(
        total_ordered=Sum('quantity')
    ).order_by('-total_ordered')[:5]
    
    # Avis récents
    recent_reviews = Review.objects.filter(
        user=request.user
    ).select_related('product').order_by('-created_at')[:3]
    
    context = {
        'orders': orders,
        'recent_orders': recent_orders,
        'total_spent': total_spent,
        'orders_this_month': orders_this_month,
        'pending_orders': pending_orders,
        'favorite_products': favorite_products,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, 'accounts/customer_dashboard.html', context)
