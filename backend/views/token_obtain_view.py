from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from backend.serializers.token_obtain_pair_serializer import (
    CustomTokenObtainPairSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        res = Response(data=serializer.validated_data["user"], status=status.HTTP_200_OK)
        
        res.set_cookie(
            "access_token",
            serializer.validated_data["token"]["access"],
            max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
            samesite='Lax',
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"]
        )
        res.set_cookie(
            "refresh_token",
            serializer.validated_data["token"]["refresh"],
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
            samesite='Lax',
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"]
        )
        return res