from rest_framework import serializers
from django.db.models import Avg
from products.models import Product, Category, Order, OrderItem, FarmerProfile
from products.models import Review
from accounts.models import User

class CategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'product_count']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class FarmerProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les profils de fermiers"""
    farmer = UserSerializer(read_only=True)
    product_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = FarmerProfile
        fields = [
            'id', 'farmer', 'farm_name', 'description', 'address', 
            'phone_number', 'email', 'website', 'agriculture_sector',
            'is_organic_certified', 'certification_details', 'opening_hours',
            'latitude', 'longitude', 'product_count', 'avg_rating'
        ]
    
    def get_product_count(self, obj):
        return obj.farmer.products.filter(is_active=True).count()
    
    def get_avg_rating(self, obj):
        reviews = Review.objects.filter(product__farmer=obj.farmer)
        if reviews.exists():
            return reviews.aggregate(avg=Avg('rating'))['avg']
        return None

class ProductSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les produits"""
    category = CategorySerializer(read_only=True)
    farmer = UserSerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock_quantity',
            'category', 'farmer', 'is_active', 'is_organic',
            'created_at', 'updated_at', 'avg_rating', 'review_count',
            'image_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'avg_rating', 'review_count']
    
    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return reviews.aggregate(avg=Avg('rating'))['avg']
        return None
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

class OrderItemSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les éléments de commande"""
    product = ProductSerializer(read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_cost']
        read_only_fields = ['id', 'price', 'total_cost']
    
    def get_total_cost(self, obj):
        return obj.get_cost()

class OrderSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les commandes"""
    customer = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'created_at', 'updated_at', 'status',
            'status_display', 'pickup_date', 'pickup_time_slot',
            'total_amount', 'notes', 'reference_number',
            'payment_status', 'payment_status_display',
            'payment_method', 'payment_method_display',
            'payment_date', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_amount', 'reference_number']

class ReviewSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les avis"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'title', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'product', 'created_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être comprise entre 1 et 5")
        return value
    
    def validate(self, data):
        # Vérifier qu'un utilisateur ne peut pas laisser plusieurs avis pour le même produit
        user = self.context['request'].user
        product = self.context.get('product')
        
        if product and Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Vous avez déjà laissé un avis pour ce produit")
        
        return data

class ProductCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de produits"""
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'stock_quantity',
            'category', 'is_active', 'is_organic', 'image'
        ]
    
    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)

class OrderCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de commandes"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = ['pickup_date', 'pickup_time_slot', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['customer'] = self.context['request'].user
        
        # Générer un numéro de référence unique
        import uuid
        validated_data['reference_number'] = f"FM-{uuid.uuid4().hex[:8].upper()}"
        
        order = Order.objects.create(**validated_data)
        
        # Créer les éléments de commande
        total_amount = 0
        for item_data in items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                total_amount += order_item.get_cost()
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Produit {product_id} non trouvé")
        
        order.total_amount = total_amount
        order.save()
        
        return order 