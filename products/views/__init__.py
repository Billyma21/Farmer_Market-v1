# products/views/__init__.py

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
