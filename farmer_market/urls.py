"""
URL configuration for farmer_market project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import register_farmer, register_customer, login_view, logout_view, customer_dashboard
from products.views.views import home, user_products
from products.views.product_views import add_product, product_detail, edit_product, delete_product, category_list
from products.views.map_views import map_view
from products.views.farmer_views import farmer_dashboard, farmer_profile, edit_profile, upload_farm_image
from cart.views import add_to_cart, view_cart, remove_from_cart, checkout, order_confirmation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Authentification
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/farmer/', register_farmer, name='register_farmer'),
    path('register/customer/', register_customer, name='register_customer'),
    
    # Tableau de bord client
    path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),
    
    # Produits
    path('products/', user_products, name='user_products'),
    path('products/add/', add_product, name='add_product'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('products/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('categories/', category_list, name='category_list'),
    
    # Carte
    path('map/', map_view, name='map_view'),
    
    # Profil Fermier
    path('farmer_dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('profile/<int:farmer_id>/', farmer_profile, name='farmer_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/upload_image/', upload_farm_image, name='upload_farm_image'),
    
    # Panier
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 