from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from products.models import Product
from .models import Provider, Order, Payment
from .serializers import ProviderSerializer, OrderSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        print(f"User requesting orders: {request.user.id}")
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        print(f"Found {orders.count()} orders")
        serializer = self.get_serializer(orders, many=True)
        print("Serialized data:", serializer.data)
        return Response({
            'count': orders.count(),
            'results': serializer.data
        })

    def get_queryset(self):
        print(f"Action: {self.action}")
        if self.action == 'my_orders':
            return Order.objects.filter(user=self.request.user).order_by('-order_date')
        return Order.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print(f"Number of orders in database: {queryset.count()}")
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })

    def create(self, request, *args, **kwargs):
        try:
            print("Received request data:", request.data)
            print("Received files:", request.FILES)

            # Validate email first
            email = request.data.get('email', '')
            try:
                validate_email(email)
            except ValidationError:
                return Response(
                    {'error': 'Please provide a valid email address'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle flat form data format
            try:
                items_data = json.loads(request.data.get('items', '[]'))
                print("Parsed items data:", items_data)
            except json.JSONDecodeError as e:
                print("JSON decode error:", str(e))
                return Response(
                    {'error': 'Invalid JSON format in items field'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate required fields with better error messages
            required_fields = {
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'phone': 'Phone Number',
                'address': 'Address',
                'city': 'City'
            }
            missing_fields = []
            invalid_fields = []
            
            for field_key, field_name in required_fields.items():
                value = request.data.get(field_key, '').strip()
                if not value:
                    missing_fields.append(field_name)
                elif len(value) < 2:  # Basic validation for minimum length
                    invalid_fields.append(f"{field_name} is too short")

            if missing_fields:
                return Response(
                    {'error': f'Please provide: {", ".join(missing_fields)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if invalid_fields:
                return Response(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch product details for each item
            complete_items = []
            for item in items_data:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    print(f"Found product: {product.id}")
                    # Adjust these field names according to your Product model
                    complete_items.append({
                        'product_id': product.id,
                        'name': getattr(product, 'title', str(product)),  # Use 'title' if that's your field name
                        'price': str(getattr(product, 'price', '0')),
                        'quantity': item['quantity'],
                        'image': str(getattr(product, 'image', ''))  # Handle case where image might not exist
                    })
                except Product.DoesNotExist:
                    print(f"Product not found: {item['product_id']}")
                    return Response(
                        {'error': f'Product with id {item["product_id"]} not found'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except Exception as e:
                    print(f"Error processing product {item['product_id']}: {str(e)}")
                    return Response(
                        {'error': f'Error processing product {item["product_id"]}: {str(e)}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Prepare order data
            order_data = {
                'first_name': request.data.get('first_name', '').strip(),
                'last_name': request.data.get('last_name', '').strip(),
                'email': email.strip(),
                'phone': request.data.get('phone', '').strip(),
                'address': request.data.get('address', '').strip(),
                'city': request.data.get('city', '').strip(),
                'notes': request.data.get('notes', '').strip(),
                'total_amount': str(request.data.get('total_amount', '0')),
                'shipping_cost': str(request.data.get('shipping_cost', '0')),
                'status': 'pending',
                'items': complete_items
            }

            print("Prepared order_data:", order_data)
            serializer = self.get_serializer(data=order_data, context={'request': request})
            
            if not serializer.is_valid():
                print("Validation errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            order = serializer.save()
            print(f"Order created with ID: {order.order_id}")

            # Create payment record if proof is provided
            if 'payment_proof' in request.FILES:
                try:
                    payment = Payment.objects.create(
                        order=order,
                        amount=order_data['total_amount'],
                        shipping_cost=order_data['shipping_cost'],
                        payment_method=request.data.get('payment_method', 'vodafone-cash'),
                        proof_image=request.FILES['payment_proof'],
                        status='pending'
                    )
                    print(f"Payment created for order: {payment.id}")
                except Exception as e:
                    print(f"Error creating payment: {str(e)}")
                    # Delete the order if payment creation fails
                    order.delete()
                    raise

            # Include order_id in response
            response_data = serializer.data
            response_data['order_id'] = order.order_id  # Assuming order_id is a field in your Order model
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error processing order: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        try:
            serializer.save()
        except ValueError as e:
            raise serializers.ValidationError(str(e))
