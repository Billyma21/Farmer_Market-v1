from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from products.models import Product, Category, Order, OrderItem, FarmerProfile
from products.models import Review
from accounts.models import User
from products.serializers import (
    ProductSerializer, CategorySerializer, OrderSerializer, 
    OrderItemSerializer, ReviewSerializer, UserSerializer,
    FarmerProfileSerializer
)
from markt_farme.logging_filters import log_audit_event, log_order_event, log_payment_event

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    """API ViewSet pour les produits"""
    queryset = Product.objects.filter(is_active=True).select_related('category', 'farmer')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'farmer', 'price', 'is_organic']
    search_fields = ['name', 'description', 'category__name', 'farmer__username']
    ordering_fields = ['name', 'price', 'created_at', 'rating']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        product = serializer.save(farmer=self.request.user)
        log_audit_event(
            user=self.request.user,
            action='product_created',
            details=f'Product created: {product.name} (ID: {product.id})',
            ip=self.request.audit_info['ip']
        )
    
    def perform_update(self, serializer):
        product = serializer.save()
        log_audit_event(
            user=self.request.user,
            action='product_updated',
            details=f'Product updated: {product.name} (ID: {product.id})',
            ip=self.request.audit_info['ip']
        )
    
    def perform_destroy(self, instance):
        product_name = instance.name
        product_id = instance.id
        instance.delete()
        log_audit_event(
            user=self.request.user,
            action='product_deleted',
            details=f'Product deleted: {product_name} (ID: {product_id})',
            ip=self.request.audit_info['ip']
        )
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        """Ajouter un avis à un produit"""
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                product=product
            )
            log_audit_event(
                user=request.user,
                action='review_added',
                details=f'Review added to product {product.name} (ID: {product.id})',
                ip=request.audit_info['ip']
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True)
    def reviews(self, request, pk=None):
        """Obtenir tous les avis d'un produit"""
        product = self.get_object()
        reviews = Review.objects.filter(product=product).select_related('user')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def featured(self, request):
        """Obtenir les produits vedettes"""
        featured_products = Product.objects.filter(
            is_active=True
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count')[:10]
        
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def organic(self, request):
        """Obtenir les produits bio"""
        organic_products = Product.objects.filter(
            is_active=True,
            is_organic=True
        )
        serializer = self.get_serializer(organic_products, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet pour les catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True)
    def products(self, request, pk=None):
        """Obtenir tous les produits d'une catégorie"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    """API ViewSet pour les commandes"""
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_farmer:
            # Les fermiers voient les commandes de leurs produits
            return Order.objects.filter(
                items__product__farmer=self.request.user
            ).distinct().select_related('customer')
        else:
            # Les clients voient leurs propres commandes
            return Order.objects.filter(
                customer=self.request.user
            ).select_related('customer')
    
    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        log_order_event(
            user=self.request.user,
            action='order_created',
            details=f'Order created: #{order.id} - Total: {order.total_amount}€',
            ip=self.request.audit_info['ip']
        )
    
    def perform_update(self, serializer):
        order = serializer.save()
        log_order_event(
            user=self.request.user,
            action='order_updated',
            details=f'Order updated: #{order.id} - Status: {order.status}',
            ip=self.request.audit_info['ip']
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler une commande"""
        order = self.get_object()
        
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()
            
            log_order_event(
                user=request.user,
                action='order_cancelled',
                details=f'Order cancelled: #{order.id}',
                ip=request.audit_info['ip']
            )
            
            return Response({'message': 'Commande annulée avec succès'})
        else:
            return Response(
                {'error': 'Cette commande ne peut plus être annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Traiter le paiement d'une commande"""
        order = self.get_object()
        payment_method = request.data.get('payment_method')
        
        if payment_method not in ['card', 'transfer', 'onsite']:
            return Response(
                {'error': 'Méthode de paiement invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_method = payment_method
        order.payment_status = 'processing'
        order.save()
        
        log_payment_event(
            user=request.user,
            action='payment_initiated',
            details=f'Payment initiated for order #{order.id} - Method: {payment_method}',
            ip=request.audit_info['ip']
        )
        
        return Response({'message': 'Paiement initié avec succès'})
    
    @action(detail=False)
    def statistics(self, request):
        """Obtenir les statistiques des commandes"""
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_orders = queryset.count()
        total_revenue = queryset.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Commandes par statut
        orders_by_status = queryset.values('status').annotate(
            count=Count('id')
        )
        
        # Commandes des 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_orders = queryset.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        return Response({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'orders_by_status': list(orders_by_status),
            'recent_orders': recent_orders
        })

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet pour les utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)
    
    @action(detail=True)
    def profile(self, request, pk=None):
        """Obtenir le profil d'un utilisateur"""
        user = self.get_object()
        if hasattr(user, 'profile'):
            serializer = FarmerProfileSerializer(user.profile)
            return Response(serializer.data)
        return Response({'error': 'Profil non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True)
    def orders(self, request, pk=None):
        """Obtenir les commandes d'un utilisateur"""
        user = self.get_object()
        orders = Order.objects.filter(customer=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class FarmerProfileViewSet(viewsets.ModelViewSet):
    """API ViewSet pour les profils de fermiers"""
    queryset = FarmerProfile.objects.all()
    serializer_class = FarmerProfileSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_organic_certified', 'agriculture_sector']
    search_fields = ['farm_name', 'description', 'address']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=True)
    def products(self, request, pk=None):
        """Obtenir les produits d'un fermier"""
        farmer_profile = self.get_object()
        products = Product.objects.filter(
            farmer=farmer_profile.farmer,
            is_active=True
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def reviews(self, request, pk=None):
        """Obtenir les avis des produits d'un fermier"""
        farmer_profile = self.get_object()
        reviews = Review.objects.filter(
            product__farmer=farmer_profile.farmer
        ).select_related('user', 'product')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data) 