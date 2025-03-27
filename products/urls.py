from django.urls import path
from products.views import ProductView

urlpatterns = [
    path('', ProductView.as_view(), name='products'),
    path('<int:id>', ProductView.as_view(), name='product-detail'),
]