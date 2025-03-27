# deal with contacus frontend form as post only DRF API

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from .models import Contactus
from .serializers import ContactusSerializer

class ContactusView(generics.CreateAPIView):
    queryset = Contactus.objects.all()
    serializer_class = ContactusSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

