# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from .models import Product, Category
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages



# Vue de la page d'accueil, qui affiche tous les produits et catégories
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Filtrage par catégorie
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Recherche de produits
    query = request.GET.get('query', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query
    })

# Vue du tableau de bord du fermier, affichant ses propres produits
@login_required
def farmer_dashboard(request):
    if not request.user.is_farmer:
        return redirect('home')

    categories = Category.objects.all()
    selected_category = request.GET.get('category', None)

    if selected_category:
        products = Product.objects.filter(farmer=request.user, category_id=selected_category)
    else:
        products = Product.objects.filter(farmer=request.user)

    out_of_stock = products.filter(stock=0).count()

    return render(request, 'products/farmer_dashboard.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'out_of_stock': out_of_stock,
    })

# # Vue pour ajouter un produit
# @login_required
# def add_product(request):
#     if not request.user.is_farmer:
#         return redirect('home')

#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.farmer = request.user
#             product.save()
#             return redirect('farmer_dashboard')
#     else:
#         form = ProductForm()

#     return render(request, 'products/add_product.html', {'form': form})
# 



# @login_required
# def add_product(request):
#     if not request.user.is_farmer:
#         return redirect('home')

#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.farmer = request.user

#             # Gestion des images
#             if 'image' in request.FILES:
#                 product.image = request.FILES['image']  # Enregistrer l'image téléchargée
#             elif 'image_url' in request.POST:
#                 product.image_url = request.POST['image_url']  # Enregistrer le lien

#             product.save()
#             return redirect('farmer_dashboard')
#     else:
#         form = ProductForm()

#     return render(request, 'products/add_product.html', {'form': form})



@login_required
def add_product(request):
    if not request.user.is_farmer:
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user

            # Gestion des images
            if 'image' in request.FILES:
                product.image = request.FILES['image']  # Enregistrer l'image téléchargée
            elif 'image_url' in request.POST:
                product.image_url = request.POST['image_url']  # Enregistrer l'URL de l'image externe

            product.save()
            return redirect('farmer_dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


# Vue pour éditer un produit existant
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user != product.farmer:
        return HttpResponse("Vous n'êtes pas autorisé à modifier ce produit.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('farmer_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {'form': form})

# Vue des détails d'un produit
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

# Vue pour supprimer un produit
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user != product.farmer:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à supprimer ce produit.")
    
    product.delete()
    return redirect('farmer_dashboard')

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Vérifier si le panier existe déjà dans la session
    cart = request.session.get('cart', {})

    # Si le produit est en stock, l'ajouter au panier
    if product.stock > 0:
        if str(product.id) in cart:
            cart[str(product.id)]['quantity'] += 1  # Augmenter la quantité si le produit est déjà dans le panier
        else:
            cart[str(product.id)] = {'name': product.name, 'price': str(product.price), 'quantity': 1}
        
        # Sauvegarder le panier dans la session
        request.session['cart'] = cart

    return redirect('home')  # Rediriger vers la page d'accueil après l'ajout

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if product.stock > 0:
        if str(product.id) in cart:
            cart[str(product.id)]['quantity'] += 1
        else:
            cart[str(product.id)] = {'name': product.name, 'price': str(product.price), 'quantity': 1}

        request.session['cart'] = cart
        messages.success(request, f"{product.name} a été ajouté à votre panier.")
    else:
        messages.error(request, f"Désolé, {product.name} est en rupture de stock.")

    return redirect('home')