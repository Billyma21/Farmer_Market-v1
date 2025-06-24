# products/views/__init__.py

<<<<<<< HEAD
from .map_views import *
from .home_views import *
from .farmer_views import *
from .profil_famer import *
from .product_farmer import *
from products.views.home_views import home, product_detail, add_to_cart
from products.views.product_farmer import add_product, edit_product, delete_product
from products.views.farmer_views import farmer_dashboard
from products.views.profil_famer import farmer_profile, edit_profile
from products.views.map_views import map_view
from products.views.cart_views import (
    cart_detail, remove_from_cart, update_cart, 
    checkout, order_confirmation, order_list, order_detail
)
=======
# Import des vues principales
from .home_views import home, product_detail
from .product_views import product_list, add_product, edit_product, delete_product
from .cart_views import view_cart, add_to_cart, update_cart, remove_from_cart, cart_count, clear_cart
from .order_views import checkout, my_orders, order_detail, cancel_order
from .review_views import add_review, edit_review, delete_review, get_product_reviews, reply_to_review
from .dashboard_views import farmer_dashboard, sales_report, manage_orders, order_detail as dashboard_order_detail, update_order_status as dashboard_update_order_status, manage_products, manage_reviews, toggle_product_status, sales_report_pdf
from .pickup_views import manage_time_slots, edit_time_slot, delete_time_slot, view_pickup_calendar, schedule_pickup
from .payment_views import payment_options, process_payment, payment_success, payment_cancel, download_invoice
from .farmer_views import farmer_profile, edit_profile
from .map_views import map_view, get_farmers_data, search_farmers
from .language_views import set_language, get_current_language, ajax_set_language

# Import des services
from products.services import *
>>>>>>> V1.01
