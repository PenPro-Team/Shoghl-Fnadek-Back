from rest_framework import serializers
from products.models import Product , ProductImage
from urllib.parse import urljoin
from ShoghlFnadek import settings

class ProductImageSerilizer(serializers.ModelSerializer):
    def get_image(self,obj):
        request = self.context.get('request')
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