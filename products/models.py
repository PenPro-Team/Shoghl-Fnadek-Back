from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(db_index=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.0 , db_index=True)
    quantity = models.PositiveIntegerField()
    image = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.title}: {self.quantity} in stock , {self.price} per one "
    
    class Meta:
        ordering = ['title'] 
    
class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="images")
    image=models.ImageField()

    def __str__(self):
        return f"{self.id} - Image For {self.product}"
    