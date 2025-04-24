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

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(FarmerProfile)
