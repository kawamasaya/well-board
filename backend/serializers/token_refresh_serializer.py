from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import User
from backend.serializers.user_serializer import UserSerializer


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        token = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh.payload.get('user_id')
        user = User.objects.get(id=user_id)
        user_data = UserSerializer(user).data
        return {
            'token': token,
            'user': user_data,
        }