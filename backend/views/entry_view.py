from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from backend.models import Entry
from backend.permissions import IsOwnerOrAdmin
from backend.serializers.entry_serializer import EntryDetailSerializer, EntrySerializer


@extend_schema(tags=["entry"])
class EntryViewSet(ModelViewSet):
    """
    エントリー管理API ViewSet
    
    ユーザーのモチベーション・ストレス記録の CRUD 操作を提供。
    ロール別のアクセス制御とAI自動スコア計算機能を含む。
    
    Permissions:
        - 一般ユーザー: 自分のエントリーのみアクセス
        - 管理者: テナント内全エントリーアクセス可能
        
    Features:
        - 日次エントリー作成
        - AWS Bedrock による自動スコア計算
        - チーム固有質問への回答記録
        
    Security:
        - 作成時にuser・tenantを自動設定
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = EntrySerializer

    def get_queryset(self):
        # 自分のデータのみ
        return Entry.objects.filter(user=self.request.user, tenant=self.request.user.tenant).order_by('-reported_at').select_related('user', 'team')
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return EntryDetailSerializer
        return EntrySerializer
    
    def perform_create(self, serializer):
        # チーム作成時に現在のユーザーのテナントを自動設定
        serializer.save(user=self.request.user, tenant=self.request.user.tenant)
    