from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _


from rest_framework import serializers

import user

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""
    
    class Meta: 
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}} 
        
    def create(self, validated_data):
        """Создает пользователя с зашифрованным паролем и возвращает егo"""
        return get_user_model().objects.create_user(**validated_data)    
    
    def update(self, instance, validated_data):
        """Обновляет пользователя, правильно установив пароль и вернув его"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
    

class AuthTokenSerializer(serializers.Serializer):

    """Сериализатор для аунтефикации пользователя"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    ) 

    def validate(self, attrs):
        """Валидация и аунтефикация"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            #Невозможно пройти аунтефикацию с предоставленными учетными данными
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
    