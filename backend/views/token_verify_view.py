from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers.token_verify_serializer import CustomTokenVerifySerializer


class CustomTokenVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.COOKIES.get("access_token")

        if access_token is None:
            return Response({"detail": "Access_token is missing."}, status=status.HTTP_400_BAD_REQUEST)

        # トークンを検証
        serializer = CustomTokenVerifySerializer(data={"token": access_token})
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)