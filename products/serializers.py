from rest_framework import serializers
from products.models import Product , ProductImage
from urllib.parse import urljoin
from ShoghlFnadek import settings

class ProductImageSerializer(serializers.ModelSerializer):
    def get_image(self,obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return urljoin(settings.MEDIA_URL, str(obj.image))
        return None
    
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True , read_only = True)
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return urljoin(settings.MEDIA_URL, str(obj.image))
        return None

    def to_internal_value(self, data):
        request = self.context.get('request')
        internal_value = super().to_internal_value(data)
        if 'request' in self.context:
            if 'image' in request.FILES:
                internal_value['image'] = request.FILES['image']
            images_data = self.context['request'].FILES.getlist('images')
            internal_value['images'] = [{'image': image} for image in images_data]
        return internal_value
    
    def create(self , validated_data):
        images_data = validated_data.pop("images", [])
        main_image = validated_data.pop("image",None)
        product = Product.objects.create(**validated_data)
        if main_image:
            product.image = main_image
            product.save()
        for image_data in images_data:
            ProductImage.objects.create(product = product , image = image_data['image'])
        return product

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    
