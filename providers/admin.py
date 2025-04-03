from django.contrib import admin
from .models import Provider, Order, OrderItem, Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'first_name', 'email', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_id', 'email', 'first_name', 'last_name']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_id', 'name', 'quantity', 'price']
    list_filter = ['order']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method']

admin.site.register(Provider)
