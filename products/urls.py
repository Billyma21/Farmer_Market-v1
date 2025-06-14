# products/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from products import views


urlpatterns = [
    path('', views.home, name='home'),
    # path('farmer_dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
 
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Système de panier et commandes
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),

    #Map openstreet-map
    path('map/', views.map_view, name='map_view'),
    
    #cote vendeur
    
    # path('farmer_dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    # path('farmer/profile/<int:farmer_id>/', views.farmer_profile, name='farmer_profile'),
    # path('farmer/farmer_profile/', views.edit_profile, name='farmer_profile'),
    path('profil_farmer/profile/<int:farmer_id>/', views.farmer_profile, name='farmer_profile'),
    path('profil_farmer/edit_profile/', views.edit_profile, name='edit_profile'),
    
    
    # Tableau de bord du fermier
    path('farmer_dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    
    # Profil fermier (afficher le profil)

    # Modifier le profil fermier
    # path('farmer/edit_profile/', views.edit_profile, name='edit_profile'),

    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    
    
    # suppression de produit

    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),

    
    
    ]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
