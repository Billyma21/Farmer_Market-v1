from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from products import views
from products.views import *
from accounts.views import customer_dashboard
from products.views import pickup_views, review_views, dashboard_views, order_views
from products.views.payment_views import payment_options, process_payment, payment_success, payment_cancel, download_invoice
from .views.review_views import get_product_reviews, reply_to_review
from .views.language_views import set_language, get_current_language
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Carte des fermiers
    path('map/', views.map_view, name='map_view'),
    
    # Panier - URLs corrigées
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart_with_id'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart_item'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views.cart_count, name='cart_count'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Commandes
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', order_views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', order_views.cancel_order, name='cancel_order'),
    
    # Dashboard fermier
    path('farmer/dashboard/', login_required(views.farmer_dashboard), name='farmer_dashboard'),
    path('farmer/products/add/', views.add_product, name='add_product'),
    path('farmer/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('farmer/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    # Tableau de bord client
    path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),   

    # Avis
    path('product/<int:product_id>/add-review/', review_views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', review_views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', review_views.delete_review, name='delete_review'),
    path('review/<int:review_id>/reply/', review_views.reply_to_review, name='reply_to_review'),
    path('product/<int:product_id>/reviews/', review_views.get_product_reviews, name='product_reviews'),

    # Côté vendeur
    path('profil_farmer/profile/<int:farmer_id>/', views.farmer_profile, name='farmer_profile'),
    path('profil_farmer/edit_profile/', views.edit_profile, name='edit_profile'),

    # Créneaux horaires et calendrier du fermier
    path('farmer/time-slots/', pickup_views.manage_time_slots, name='manage_time_slots'),
    path('farmer/time-slots/<int:slot_id>/edit/', pickup_views.edit_time_slot, name='edit_time_slot'),
    path('farmer/time-slots/<int:slot_id>/delete/', pickup_views.delete_time_slot, name='delete_time_slot'),
    path('farmer/calendar/', pickup_views.view_pickup_calendar, name='pickup_calendar'),
    path('order/<int:order_id>/schedule-pickup/', pickup_views.schedule_pickup, name='schedule_pickup'),
    
    # Tableau de bord fermier avancé
    path('farmer/sales_report/', dashboard_views.sales_report, name='sales_report'),
    path('farmer/manage_orders/', dashboard_views.manage_orders, name='manage_orders'),
    path('farmer/order/<int:order_id>/', dashboard_views.order_detail, name='dashboard_order_detail'),
    path('farmer/order/<int:order_id>/update_status/', dashboard_views.update_order_status, name='update_order_status'),
    path('farmer/manage_products/', dashboard_views.manage_products, name='manage_products'),
    path('farmer/manage_reviews/', dashboard_views.manage_reviews, name='manage_reviews'),
    path('farmer/sales_report_pdf/', dashboard_views.sales_report_pdf, name='sales_report_pdf'),
    path('dashboard/toggle-product/<int:product_id>/', dashboard_views.toggle_product_status, name='toggle_product_status'),

    # Rapport de vente PDF
    path('sales-report/pdf/', views.sales_report_pdf, name='sales_report_pdf'),

    # Télécharger la facture après paiement
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
    path('download_invoice/<int:order_id>/', download_invoice, name='download_invoice'),

    # API endpoints
    path('api/reviews/<int:product_id>/', get_product_reviews, name='get_product_reviews'),
    path('reviews/<int:review_id>/reply/', reply_to_review, name='reply_to_review'),

    # Changement de langue optimisé
    path('api/set-language/', set_language, name='set_language'),
    path('api/current-language/', get_current_language, name='get_current_language'),

    # API pour la carte
    path('api/farmers/', views.get_farmers_data, name='get_farmers_data'),
    path('api/farmers/search/', views.search_farmers, name='search_farmers'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
