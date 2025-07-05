from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class TokenDeleteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        res = Response(status=status.HTTP_200_OK)
        res.delete_cookie('access_token')
        res.delete_cookie('refresh_token')

        return res