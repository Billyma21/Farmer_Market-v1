from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
import tempfile
from products.models import Product
from products.models import Order, OrderItem, Review, PickupAppointment
from products.services import ReviewService, OrderService

@login_required
def farmer_dashboard(request):
    """Tableau de bord pour les fermiers avec statistiques de vente"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Périodes pour les statistiques
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    # Produits du fermier
    products = Product.objects.filter(farmer=request.user)
    
    # Commandes avec des produits du fermier
    orders_with_farmer_products = Order.objects.filter(
        items__product__farmer=request.user
    ).distinct()
    
    # Statistiques de vente
    total_sales = OrderItem.objects.filter(
        product__farmer=request.user,
        order__status__in=['completed', 'ready']
    ).aggregate(
        total=Sum(F('price') * F('quantity')),
        count=Count('id')
    )
    
    # Ventes par période
    sales_today = OrderItem.objects.filter(
        product__farmer=request.user,
        order__status__in=['completed', 'ready'],
        order__created_at__date=today
    ).aggregate(
        total=Sum(F('price') * F('quantity')),
        count=Count('id')
    )
    
    sales_week = OrderItem.objects.filter(
        product__farmer=request.user,
        order__status__in=['completed', 'ready'],
        order__created_at__date__gte=start_of_week
    ).aggregate(
        total=Sum(F('price') * F('quantity')),
        count=Count('id')
    )
    
    sales_month = OrderItem.objects.filter(
        product__farmer=request.user,
        order__status__in=['completed', 'ready'],
        order__created_at__date__gte=start_of_month
    ).aggregate(
        total=Sum(F('price') * F('quantity')),
        count=Count('id')
    )
    
    # Top produits
    top_products = OrderItem.objects.filter(
        product__farmer=request.user,
    ).values(
        'product__id', 
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_sold')[:5]
    
    # Commandes récentes
    recent_orders = orders_with_farmer_products.order_by('-created_at')[:10]
    
    # Statistiques des avis
    avg_rating = ReviewService.get_farmer_average_rating(request.user)
    
    recent_reviews = Review.objects.filter(
        product__farmer=request.user
    ).select_related(
        'user', 'product'
    ).order_by('-created_at')[:5]
    
    # Rendez-vous de retrait à venir
    upcoming_pickups = PickupAppointment.objects.filter(
        availability_slot__farmer=request.user,
        pickup_date__gte=today
    ).select_related(
        'order', 'order__customer', 'availability_slot'
    ).order_by('pickup_date', 'availability_slot__start_time')[:10]
    
    # Commandes à préparer (confirmées)
    orders_to_prepare = orders_with_farmer_products.filter(status='confirmed').count()
    
    # Commandes prêtes
    orders_ready = orders_with_farmer_products.filter(status='ready').count()
    
    # Retraits aujourd'hui
    pickups_today = PickupAppointment.objects.filter(
        availability_slot__farmer=request.user,
        pickup_date=today
    ).count()
    
    # Produits avec stock faible
    low_stock_threshold = 5
    low_stock_products = products.filter(stock__lte=low_stock_threshold).count()
    
    context = {
        'products_count': products.count(),
        'total_sales': total_sales,
        'sales_today': sales_today,
        'sales_week': sales_week,
        'sales_month': sales_month,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'avg_rating': avg_rating,
        'recent_reviews': recent_reviews,
        'upcoming_pickups': upcoming_pickups,
        'orders_to_prepare': orders_to_prepare,
        'orders_ready': orders_ready,
        'pickups_today': pickups_today,
        'low_stock_products': low_stock_products,
        'today': today,
        'start_of_week': start_of_week
    }
    
    return render(request, 'products/dashboard/farmer_dashboard.html', context)

@login_required
def manage_orders(request):
    """Gestion détaillée des commandes pour les fermiers"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Récupération des paramètres de filtrage
    status = request.GET.get('status', '')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    search = request.GET.get('search', '')
    
    # Construction de la requête de base
    orders = Order.objects.filter(
        items__product__farmer=request.user
    ).distinct().select_related('customer').prefetch_related('items', 'items__product')
    
    # Filtrage par statut
    if status:
        orders = orders.filter(status=status)
    
    # Filtrage par date
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    # Recherche par ID ou client
    if search:
        orders = orders.filter(
            Q(id__icontains=search) | 
            Q(customer__username__icontains=search) |
            Q(customer__email__icontains=search) |
            Q(reference_number__icontains=search)
        )
    
    # Liste des statuts pour le filtre
    status_choices = Order._meta.get_field('status').choices
    
    context = {
        'orders': orders.order_by('-created_at'),
        'status_choices': status_choices,
        'current_status': status,
        'date_from': date_from_str,
        'date_to': date_to_str,
        'search': search
    }
    
    return render(request, 'products/dashboard/manage_orders.html', context)

@login_required
def order_detail(request, order_id):
    """Détail d'une commande pour les fermiers"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Récupérer la commande et vérifier qu'elle contient des produits du fermier
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que la commande contient des produits du fermier
    order_items = order.items.filter(product__farmer=request.user)
    if not order_items.exists():
        messages.error(request, "Cette commande ne contient aucun de vos produits.")
        return redirect('manage_orders')
    
    # Calculer le total des articles de la commande concernant ce fermier
    order_items_total = sum(item.price * item.quantity for item in order_items)
    
    # Récupérer le rendez-vous de retrait si existant
    try:
        pickup = PickupAppointment.objects.get(order=order)
    except PickupAppointment.DoesNotExist:
        pickup = None
    
    context = {
        'order': order,
        'order_items': order_items,
        'order_items_total': order_items_total,
        'pickup': pickup,
        'status_choices': Order._meta.get_field('status').choices
    }
    
    return render(request, 'products/dashboard/order_detail.html', context)

@login_required
def update_order_status(request, order_id):
    """Mettre à jour le statut d'une commande"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour effectuer cette action.")
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que la commande contient des produits du fermier
    if not order.items.filter(product__farmer=request.user).exists():
        messages.error(request, "Cette commande ne contient aucun de vos produits.")
        return redirect('manage_orders')
    
    # Récupérer le nouveau statut
    new_status = request.GET.get('status') or request.POST.get('status')
    
    if new_status and new_status in dict(Order._meta.get_field('status').choices):
        success = OrderService.update_order_status(order, new_status)
        
        if success:
            messages.success(request, f"Le statut de la commande #{order.id} a été mis à jour avec succès.")
        else:
            messages.error(request, f"Impossible de mettre à jour le statut de la commande #{order.id}.")
    else:
        messages.error(request, "Statut invalide.")
    
    # Rediriger vers la page de détail ou la liste des commandes
    if request.GET.get('redirect_to') == 'detail':
        return redirect('order_detail', order_id=order.id)
    return redirect('manage_orders')

@login_required
def manage_products(request):
    """Gestion des produits du fermier"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Paramètres de filtrage
    filter_param = request.GET.get('filter', '')
    category_id = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    # Produits de base du fermier
    products = Product.objects.filter(farmer=request.user)
    
    # Application des filtres
    if filter_param == 'low_stock':
        low_stock_threshold = 5
        products = products.filter(stock__lte=low_stock_threshold)
    
    if filter_param == 'out_of_stock':
        products = products.filter(stock=0)
    
    if filter_param == 'active':
        products = products.filter(is_active=True)
    
    if filter_param == 'inactive':
        products = products.filter(is_active=False)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Récupérer les catégories pour le filtre
    from products.models import Category
    categories = Category.objects.all()
    
    context = {
        'products': products.order_by('-created_at'),
        'categories': categories,
        'filter': filter_param,
        'category_id': category_id,
        'search': search
    }
    
    return render(request, 'products/dashboard/manage_products.html', context)

@login_required
def toggle_product_status(request, product_id):
    """Active ou désactive un produit"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour effectuer cette action.")
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, farmer=request.user)
    
    if request.method == 'POST':
        # Inverser le statut du produit
        product.is_active = not product.is_active
        product.save()
        
        status_text = "activé" if product.is_active else "désactivé"
        messages.success(request, f"Le produit '{product.name}' a été {status_text} avec succès.")
    
    return redirect('manage_products')

@login_required
def manage_reviews(request):
    """Gestion des avis reçus sur les produits du fermier"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Paramètres de filtrage
    product_id = request.GET.get('product', '')
    rating = request.GET.get('rating', '')
    sort = request.GET.get('sort', '-created_at')
    
    # Avis sur les produits du fermier
    reviews = Review.objects.filter(
        product__farmer=request.user
    ).select_related('product', 'user')
    
    # Application des filtres
    if product_id:
        reviews = reviews.filter(product_id=product_id)
    
    if rating:
        reviews = reviews.filter(rating=rating)
    
    # Tri des avis
    if sort in ['-created_at', 'created_at', '-rating', 'rating']:
        reviews = reviews.order_by(sort)
    else:
        reviews = reviews.order_by('-created_at')
    
    # Produits du fermier pour le filtre
    products = Product.objects.filter(farmer=request.user)
    
    context = {
        'reviews': reviews,
        'products': products,
        'product_id': product_id,
        'rating': rating,
        'sort': sort
    }
    
    return render(request, 'products/dashboard/manage_reviews.html', context)

@login_required
def sales_report(request):
    """Rapport détaillé des ventes pour les fermiers"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Récupération des paramètres de filtrage
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    product_id = request.GET.get('product')
    
    # Dates par défaut
    today = timezone.now().date()
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = today - timedelta(days=30)
    else:
        date_from = today - timedelta(days=30)
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_to = today
    else:
        date_to = today
    
    # Filtrer les commandes
    query = OrderItem.objects.filter(
        product__farmer=request.user,
        order__created_at__date__range=[date_from, date_to],
        order__status__in=['completed', 'processing', 'ready']
    )
    
    if product_id:
        query = query.filter(product_id=product_id)
    
    # Statistiques de ventes
    order_items = query.select_related('order', 'product')
    orders = Order.objects.filter(items__in=order_items).distinct().order_by('-created_at')
    
    # Totaux
    sales_stats = query.aggregate(
        total_sales=Sum(F('price') * F('quantity')),
        total_products=Sum('quantity')
    )
    
    # Données pour le graphique
    sales_by_date = query.values('order__created_at__date').annotate(
        total=Sum(F('price') * F('quantity'))
    ).order_by('order__created_at__date')
    
    dates = [item['order__created_at__date'].strftime('%d/%m/%Y') for item in sales_by_date]
    values = [float(item['total']) for item in sales_by_date]
    
    sales_data = {
        'labels': dates,
        'values': values
    }
    
    # Liste des produits pour le filtre
    products = Product.objects.filter(farmer=request.user).order_by('name')
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'product_id': int(product_id) if product_id and product_id.isdigit() else None,
        'orders': orders,
        'products': products,
        'total_sales': sales_stats.get('total_sales') or 0,
        'total_orders': orders.count(),
        'total_products': sales_stats.get('total_products') or 0,
        'sales_data': json.dumps(sales_data)
    }
    
    return render(request, 'products/dashboard/sales_report.html', context)

@login_required
def sales_report_pdf(request):
    """Génère un rapport de ventes au format PDF"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Récupération des paramètres de filtrage
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    product_id = request.GET.get('product')
    
    # Dates par défaut
    today = timezone.now().date()
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = today - timedelta(days=30)
    else:
        date_from = today - timedelta(days=30)
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_to = today
    else:
        date_to = today
    
    # Filtrer les commandes
    query = OrderItem.objects.filter(
        product__farmer=request.user,
        order__created_at__date__range=[date_from, date_to],
        order__status__in=['completed', 'processing', 'ready']
    )
    
    if product_id:
        query = query.filter(product_id=product_id)
        product = Product.objects.get(id=product_id)
    else:
        product = None
    
    # Statistiques de ventes
    order_items = query.select_related('order', 'product')
    orders = Order.objects.filter(items__in=order_items).distinct().order_by('-created_at')
    
    # Totaux
    sales_stats = query.aggregate(
        total_sales=Sum(F('price') * F('quantity')),
        total_products=Sum('quantity')
    )
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'product': product,
        'orders': orders,
        'total_sales': sales_stats.get('total_sales') or 0,
        'total_orders': orders.count(),
        'total_products': sales_stats.get('total_products') or 0,
        'now': timezone.now()
    }
    
    # Utilisation de wkhtmltopdf si disponible
    if PDFTemplateResponse:
        response = PDFTemplateResponse(
            request=request,
            template='products/dashboard/sales_report_pdf.html',
            filename="rapport_ventes.pdf",
            context=context,
            show_content_in_browser=True,
            cmd_options={'margin-top': 10, 'margin-bottom': 10}
        )
        return response
    else:
        # Méthode alternative si wkhtmltopdf n'est pas disponible
        html_template = get_template('products/dashboard/sales_report_pdf.html')
        html = html_template.render(context)
        
        response = HttpResponse(html, content_type='text/html')
        return response 