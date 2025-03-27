from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny , IsAdminUser , IsAuthenticated , IsAuthenticatedOrReadOnly
from products.models import Product , ProductImage
from products.serializers import ProductImageSerializer , ProductSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


# Create your views here.
class ProductPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class ProductView(APIView):
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator
    
    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, id=None):
        if id:
            product = get_object_or_404(Product, id=id)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)
        
        products = Product.objects.all()
        
        search = request.GET.get('search', '').strip()
        min_price = request.GET.get('minprice', '').strip()
        max_price = request.GET.get('maxprice', '').strip()
        
        filter_query = Q()
        if search:
            filter_query &= (Q(title__icontains=search) | Q(description__icontains=search))
        if min_price:
            try:
                min_price = float(min_price)
                if min_price < 0:
                    return Response({'error': 'Price cannot be negative'}, status=400)
                filter_query &= Q(price__gte=min_price)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid price format'}, status=400)
        if max_price:
            try:
                max_price = float(max_price)
                if max_price < 0:
                    return Response({'error': 'Price cannot be negative'}, status=400)
                filter_query &= Q(price__lte=max_price)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid price format'}, status=400)
        
        products = products.filter(filter_query)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
       
    def post(self , request):
        serializer = ProductSerializer(data=request.data , context={'request' : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def put(self , request , id=None):
        if not id:
            id = request.data.get('id')
        if id:
            product = get_object_or_404(Product , id = id )
            if 'images' in request.FILES:
                product.images.all().delete()
            serializer = ProductSerializer(product , data = request.data , context={'request' : request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data , status=status.HTTP_200_OK)
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors':"Missing ID"} , status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self , request , id=None):
        if not id:
            id = request.data.get('id')
        if id:
            product = get_object_or_404(Product , id = id)
            serializer = ProductSerializer(product , data = request.data , partial=True, context={'request' : request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data , status=status.HTTP_200_OK)
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors':"Missing ID"} , status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request , id=None):
        if not id:
            id = request.data.get('id')
        if id:
            product = get_object_or_404(Product , id = id)
            product.delete()
            return Response({'message':'Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'errors':"Missing ID"} , status=status.HTTP_400_BAD_REQUEST)

