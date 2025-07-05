from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from backend.models import User
from backend.models.user import UserRole
from backend.permissions import IsAdminOrManager, IsOwnerOrAdmin, IsTenantUser
from backend.serializers.user_serializer import UserDetailSerializer, UserSerializer


@extend_schema(
        parameters=[
            OpenApiParameter('tenants_pk', int, OpenApiParameter.PATH),
        ],
        tags=["user"],
    )
class UserViewSet(ModelViewSet):
    """
    ユーザー管理API ViewSet
    
    マルチテナント対応のユーザーCRUD操作を提供。
    ロール別の権限制御とテナント分離を実装。
        
    Features:
        - テナント内ユーザーのみ表示（SUPERUSER除外）
        - ロール変更権限のチェック
        
    Security:
        - 自分より上位ロールへの変更不可
        - SUPERUSERロール設定不可
    """
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        アクションに応じて異なる権限を適用
        """
        if self.action in ['create', 'destroy']:
            # ユーザー作成・削除はマネージャーまたは管理者のみ
            permission_classes = [IsAuthenticated, IsAdminOrManager]
        elif self.action in ['update', 'partial_update']:
            # ユーザー更新は所有者または管理者のみ
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            # 一覧・詳細表示はテナントユーザーなら可能
            permission_classes = [IsAuthenticated, IsTenantUser]
        
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return UserDetailSerializer
        return UserSerializer
            
    def get_queryset(self):
        # テナント内の全ユーザー表示（SUPERUSER除く）
        return User.objects.filter(
            tenant=self.request.user.tenant
        ).exclude(role=UserRole.SUPERUSER.value).prefetch_related('teams')
    
    
    def can_change_role(self, user, new_role):
        """
        ユーザーロール変更の権限チェック
        
        セキュリティ上重要な制約を適用して、不正なロール変更を防ぐ。
        
        Args:
            user: 操作を実行するユーザー
            new_role (int): 設定しようとする新しいロール値
            
        Returns:
            tuple: (bool, str|None)
                - bool: 変更可能かどうか
                - str: エラーメッセージ（エラー時のみ）
                
        Security Rules:
            1. 自分より上位のロールには設定不可
            2. SUPERUSERロールは設定不可
            
        Role Hierarchy:
            SUPERUSER(1) > ADMIN(2) > MANAGER(3) > USER(4)
        """
        
        # 自分より上位のロールには設定できない
        if int(new_role) < user.role:
            return False, "自分より上位のロールに設定することはできません。"
        
        # SUPERUSERロールはSUPERUSERのみ設定可能
        if int(new_role) == UserRole.SUPERUSER.value:
            return False, "スーパーユーザーロールは設定できません。"
        
        return True, None
    
    def can_create_user_with_role(self, user, role):
        """
        ユーザー作成時のロール設定権限チェック
        
        新規ユーザー作成時に設定可能なロールを制限する。
        
        Args:
            user: 操作を実行するユーザー
            role (int): 設定しようとするロール値
            
        Returns:
            tuple: (bool, str|None)
                - bool: 作成可能かどうか
                - str: エラーメッセージ（エラー時のみ）
                
        Security Rules:
            1. 管理者以外は管理者ロールでユーザー作成不可
            2. SUPERUSERロールでの作成は不可
            
        Role Requirements:
            - ADMIN作成: ADMIN権限以上が必要
            - SUPERUSER作成: 不可（システムレベルで制限）
        """
        # 管理者以外は管理者ロールでユーザー作成不可
        if int(role) == UserRole.ADMIN.value and user.role < UserRole.ADMIN.value:
            return False, "管理者権限が必要です。"
        
        # SUPERUSERロールはSUPERUSERのみ設定可能
        if int(role) == UserRole.SUPERUSER.value:
            return False, "スーパーユーザーで作成する権限がありません。"
        
        return True, None
    
    def perform_update(self, serializer):
        # ロール変更のチェック
        if 'role' in self.request.data:
            new_role = self.request.data['role']
            can_change, error_msg = self.can_change_role(self.request.user, new_role)
            if not can_change:
                raise ValidationError({'error': error_msg})
        
        serializer.save()
    
    def perform_create(self, serializer):
        # ロール設定のチェック
        if 'role' in self.request.data:
            can_create, error_msg = self.can_create_user_with_role(self.request.user, self.request.data['role'])
            if not can_create:
                raise ValidationError({'error': error_msg})
        
        # テナントを自動設定してユーザー作成
        serializer.save(tenant=self.request.user.tenant)