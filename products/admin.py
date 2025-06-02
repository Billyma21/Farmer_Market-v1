from django.contrib import admin
from products.models import Category, Product, FarmerProfile
from products.models.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'created_at', 'status', 'payment_status', 'total_price']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['id', 'customer__username', 'contact_email', 'shipping_address']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ['id']
    fieldsets = (
        ('Informations de base', {
            'fields': ('id', 'customer', 'created_at', 'updated_at')
        }),
        ('Statut', {
            'fields': ('status', 'payment_status')
        }),
        ('Livraison', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_zip_code', 'shipping_country', 'tracking_number')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'payment_id', 'total_price')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['name', 'category', 'price', 'stock']
    fk_name = 'farmer'

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'address', 'phone_number', 'production_method', 'visits_allowed']
    list_filter = ['production_method', 'visits_allowed']
    search_fields = ['farmer__username', 'address', 'description']
    readonly_fields = ['google_maps_link']
    fieldsets = (
        ('Informations de base', {
            'fields': ('farmer', 'description', 'farm_images')
        }),
        ('Localisation', {
            'fields': ('full_address', 'address', 'latitude', 'longitude', 'google_maps_link')
        }),
        ('Contact', {
            'fields': ('phone_number', 'website')
        }),
        ('Production', {
            'fields': ('agriculture_sector', 'production_method', 'certifications')
        }),
        ('Services', {
            'fields': ('services', 'opening_hours', 'visits_allowed', 'additional_info')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Géocoder l'adresse si elle est modifiée."""
        if 'full_address' in form.changed_data and obj.full_address:
            obj.geocode_address()
        super().save_model(request, obj, form, change)

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'sales_count', 'farmer']
    list_filter = ['category', 'farmer']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'image')
        }),
        ('Commerce', {
            'fields': ('category', 'price', 'stock', 'sales_count')
        }),
        ('Relation', {
            'fields': ('farmer',)
        }),
    )
