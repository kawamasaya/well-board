import logging
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.tokens import TokenError, UntypedToken

from backend.models import User
from backend.serializers import user_serializer


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        validation = super().validate(attrs)

        if not validation:
            try:
                token = UntypedToken(attrs["token"])
                user_id = token.payload["user_id"]
                user = User.objects.get(id=user_id)
                user_data = user_serializer.UserSerializer(user).data
            except TokenError as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Token verification failed: {e}")
                raise serializers.ValidationError("Invalid token")
                
        return {
            'token': attrs["token"],
            'user': user_data
        }