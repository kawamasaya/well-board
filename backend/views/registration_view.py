from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers.tenant_request_serializer import TenantRequestSerializer


class TenantRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        テナントリクエストAPI
        
        テナント申請のデータを登録するAPI
        Args:
            request: HTTPリクエストオブジェクト
        """
        serializer = TenantRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            tenant_request = serializer.save()
            
            response_data = {
                'message': 'テナントリクエストが完了しました。承認をお待ちください。',
                'request': {
                    'id': tenant_request.id
                }
            }
            
            return Response(
                response_data, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )


