from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend.serializers import user_serializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        token = super().validate(attrs)
        
        data = dict()
        user = user_serializer.UserSerializer(self.user).data
        data['token'] = token
        data['user'] = user
        return data