from rest_framework import serializers
from .models import Provider, Order, OrderItem, Payment, Product
from django.db import transaction

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'name', 'price', 'quantity', 'image']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['amount', 'shipping_cost', 'payment_method', 'proof_image', 'status']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment = PaymentSerializer(required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id', 'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'notes', 'status', 'status_display',
            'order_date', 'total_amount', 'shipping_cost', 'items', 'payment'
        ]
        read_only_fields = ['order_id', 'order_date']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        payment_data = validated_data.pop('payment', None)
        user = self.context['request'].user if 'request' in self.context else None
        
        # Create order first
        order = Order.objects.create(user=user, **validated_data)
        
        # Create order items and update product quantities
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
            # Update product quantity immediately
            try:
                product = Product.objects.select_for_update().get(id=item_data['product_id'])
                if product.quantity >= item_data['quantity']:
                    product.quantity -= item_data['quantity']
                    product.save()
                    print(f"Updated quantity for product {product.id}: {product.quantity}")
                else:
                    raise ValueError(f"Insufficient stock for product {product.title}")
            except Product.DoesNotExist:
                print(f"Product {item_data['product_id']} not found")
                continue
            
        if payment_data:
            Payment.objects.create(order=order, **payment_data)
        
        return order
