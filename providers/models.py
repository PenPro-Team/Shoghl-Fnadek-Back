from django.db import models
import uuid
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class Provider(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    experience = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Customer Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True, null=True)
    
    # Order Details
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )

    @transaction.atomic
    def update_product_quantities(self, restore=False):
        print(f"Updating quantities for order {self.order_id} - Restore: {restore}")
        for item in self.items.all():
            try:
                product = Product.objects.select_for_update().get(id=item.product_id)
                old_quantity = product.quantity
                print(f"Product {product.id} current quantity: {old_quantity}")
                
                if restore:
                    product.quantity += item.quantity
                    print(f"Restoring {item.quantity} units to product {product.id}")
                else:
                    if product.quantity >= item.quantity:
                        product.quantity -= item.quantity
                        print(f"Reducing {item.quantity} units from product {product.id}")
                    else:
                        error_msg = f"Insufficient stock for product {product.title}"
                        print(error_msg)
                        raise ValueError(error_msg)
                
                print(f"Saving product {product.id} with new quantity: {product.quantity}")
                product.save()
            except Product.DoesNotExist:
                print(f"Product {item.product_id} not found")
                continue
            except Exception as e:
                print(f"Error updating product {item.product_id}: {str(e)}")
                raise

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, update_fields, **kwargs):
    print(f"Signal triggered for order {instance.order_id}")
    try:
        if not created:
            # Get the instance directly from database to get pre-save state
            with transaction.atomic():
                previous_instance = Order.objects.select_for_update().get(id=instance.id)
                previous_status = previous_instance.status
                print(f"Previous status from DB: {previous_status}, New status: {instance.status}")

                if previous_status != instance.status:
                    if instance.status == 'canceled' and previous_status in ['pending', 'confirmed']:
                        print(f"Order {instance.order_id} canceled - restoring quantities")
                        instance.update_product_quantities(restore=True)
                    elif previous_status == 'canceled' and instance.status in ['pending', 'confirmed']:
                        print(f"Order {instance.order_id} reactivated - reducing quantities")
                        instance.update_product_quantities()

    except Exception as e:
        print(f"Error in signal handler: {str(e)}")
        raise

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.CharField(max_length=255)

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('vodafone-cash', 'Vodafone Cash'),
        # Add other payment methods as needed
    ]
    
    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    proof_image = models.ImageField(upload_to='payment_proofs/')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
