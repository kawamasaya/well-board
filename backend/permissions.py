from rest_framework.permissions import BasePermission

from backend.models.user import UserRole


class TenantBasePermission(BasePermission):
    """
    テナント確認の共通処理を提供するベースクラス
    """
    def _is_authenticated_user(self, request):
        """認証済みユーザーかどうかを確認"""
        return request.user and request.user.is_authenticated
    
    def _check_url_tenant(self, request, view):
        """URLのテナントIDとユーザーのテナントIDを確認"""
        url_tenant_id = view.kwargs.get('tenants_pk')
        if url_tenant_id and str(url_tenant_id) != str(request.user.tenant.id):
            return False
        return True
    
    def _check_object_tenant(self, request, obj):
        """オブジェクトのテナントとユーザーのテナントを確認"""
        if hasattr(obj, 'tenant') and obj.tenant != request.user.tenant:
            return False
        return True
    

class IsAdminOrManager(TenantBasePermission):
    """
    管理者（ADMIN）またはマネージャー（MANAGER）のみアクセス可能
    """
    def has_permission(self, request, view):
        if not self._is_authenticated_user(request):
            return False
        
        if not self._check_url_tenant(request, view):
            return False
        
        # 役割確認
        return request.user.role in [UserRole.SUPERUSER.value, UserRole.ADMIN.value, UserRole.MANAGER.value]


class IsOwnerOrAdmin(TenantBasePermission):
    """
    データの所有者または管理者のみアクセス可能（オブジェクトレベル権限）
    """
    def has_permission(self, request, view):
        if not self._is_authenticated_user(request):
            return False
        
        return self._check_url_tenant(request, view)
    
    def has_object_permission(self, request, view, obj):
        if not self._check_object_tenant(request, obj):
            return False
        
        # 管理者は全てのデータにアクセス可能
        if request.user.role in [UserRole.SUPERUSER.value, UserRole.ADMIN.value]:
            return True
        
        # データの所有者確認
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # User オブジェクト自体の場合
        if hasattr(obj, 'email') and hasattr(obj, 'name'):
            return obj == request.user
        
        return False


class IsTeamManagerOrSelf(TenantBasePermission):
    """
    チームマネージャー、管理者、または自分自身のデータのみアクセス可能
    """
    def has_permission(self, request, view):
        if not self._is_authenticated_user(request):
            return False
        
        return self._check_url_tenant(request, view)


class IsTenantUser(TenantBasePermission):
    """
    テナントユーザーのみアクセス可能
    """
    def has_permission(self, request, view):
        if not self._is_authenticated_user(request):
            return False
            
        url_tenant_id = view.kwargs.get('tenants_pk')
        if not url_tenant_id:
            return True  # tenants_pk がない場合は基本チェックのみ
        
        return self._check_url_tenant(request, view)
    
    def has_object_permission(self, request, view, obj):
        """オブジェクトレベルでのテナント確認"""
        return self._check_object_tenant(request, obj)