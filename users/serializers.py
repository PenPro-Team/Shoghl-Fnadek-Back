from rest_framework import serializers
from urllib.parse import urljoin
from django.conf import settings
from .models import User

class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return urljoin(settings.MEDIA_URL, str(obj.image))
        return None

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'image']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False, 'allow_blank': True,'write_only': True},
        }

    def create(self, validated_data):
        if 'username' not in validated_data or not validated_data['username']:
            email = validated_data.get('email', '')
            if email:
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                validated_data['username'] = username
        
        user = User.objects.create_user(**validated_data)
        return user
            
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user