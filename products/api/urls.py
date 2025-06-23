from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, OrderViewSet, 
    UserViewSet, FarmerProfileViewSet
)
from products.views.map_views import get_farmers_data, search_farmers

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet, basename='user')
router.register(r'farmers', FarmerProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('farmers/', get_farmers_data, name='get_farmers_data'),
    path('farmers/search/', search_farmers, name='search_farmers'),
] 