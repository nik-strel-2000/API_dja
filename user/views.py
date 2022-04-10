from rest_framework import generics , authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings 

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Создание нового пользователя в сиситеме"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Создание нового токена аунтефикации для пользоватея"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Управление (просмотр и изменение) авторизованным пользователем"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    