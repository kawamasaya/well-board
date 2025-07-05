from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from backend.models import Team
from backend.permissions import IsAdminOrManager, IsTenantUser
from backend.serializers.team_serializer import TeamDetailSerializer, TeamSerializer


@extend_schema(
    parameters=[
            OpenApiParameter('tenants_pk', int, OpenApiParameter.PATH),
    ],
    tags=["team"])
class TeamViewSet(ModelViewSet):
    """
    チーム管理API ViewSet
    
    マルチテナント対応のチームCRUD操作を提供。
    チーム固有の質問設定と管理者アサインメント機能を含む。
        
    Features:
        - テナント内チームのみ表示
        - チーム固有の質問項目管理
        - チーム管理者の設定
    """
    permission_classes = [IsAuthenticated, IsTenantUser]
    serializer_class = TeamSerializer

    def get_permissions(self):
        """
        アクションに応じて異なる権限を適用
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # チーム作成・削除は管理者のみ
            permission_classes = [IsAuthenticated, IsAdminOrManager]
        else:
            # 一覧・詳細表示はテナントユーザーなら可能
            permission_classes = [IsAuthenticated, IsTenantUser]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TeamDetailSerializer
        return TeamSerializer
    
    def get_queryset(self):
        # 現在のテナントに属するチームのみ表示
        return Team.objects.filter(
            tenant=self.request.user.tenant
        ).prefetch_related('managers')
    
    def perform_create(self, serializer):
        # チーム作成時に現在のユーザーのテナントを自動設定
        serializer.save(tenant=self.request.user.tenant)