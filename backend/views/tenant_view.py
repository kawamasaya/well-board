from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from backend.models import Tenant
from backend.serializers.tenant_serializer import TenantSerializer


@extend_schema(tags=["tenant"])
class TenantViewSet(ModelViewSet):
    """
    テナント管理API ViewSet
    
    マルチテナントシステムの組織単位の管理機能を提供。
        
    Features:
        - テナント情報の CRUD 操作
        - 組織設定の管理
        - domain_settings の JSON 管理
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer