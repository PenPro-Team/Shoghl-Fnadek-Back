from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProviderViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
