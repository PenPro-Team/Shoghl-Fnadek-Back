from django.contrib import admin
from django.urls import path
from .views import ContactusView

urlpatterns = [
    path('', ContactusView.as_view(), name='contact_us'),
]
