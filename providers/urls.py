from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ProviderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'providers', ProviderViewSet, basename='provider')

urlpatterns = [
    path('orders/my-orders/', OrderViewSet.as_view({'get': 'my_orders'})),
    path('', include(router.urls)),
]
