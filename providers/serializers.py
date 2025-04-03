from rest_framework import serializers
from .models import Provider, Order, OrderItem, Payment

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

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_id', 'order_date']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        payment_data = validated_data.pop('payment', None)
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        if payment_data:
            Payment.objects.create(order=order, **payment_data)
        
        return order
