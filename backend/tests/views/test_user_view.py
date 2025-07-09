from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APITestCase

from backend.models import Team, Tenant
from backend.models.user import UserRole
from backend.permissions import IsAdminOrManager, IsOwnerOrAdmin, IsTenantUser
from backend.serializers.user_serializer import UserSerializer
from backend.views.user_view import UserViewSet


class TestUserView(APITestCase):

    @staticmethod
    def create_tenant(name):
        """テナントを作成するヘルパーメソッド"""
        return Tenant.objects.create(name=name)
    
    @staticmethod
    def create_user(email, name, tenant, role=UserRole.USER.value):
        """ユーザーを作成するヘルパーメソッド"""
        User = get_user_model()
        return User.objects.create_user(email=email, password="12345", name=name, tenant=tenant, role=role)
    
    @staticmethod
    def create_team(name, tenant):
        """チームを作成するヘルパーメソッド"""
        return Team.objects.create(name=name, tenant=tenant)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # テスト用のテナントを作成
        cls.tenant1 = cls.create_tenant("tenant1")
        cls.tenant2 = cls.create_tenant("tenant2")
        
        # テスト用のユーザーを作成（さまざまなロール）
        cls.tenant1_user1 = cls.create_user("user1@example.com", "user1", cls.tenant1, UserRole.USER.value)
        cls.tenant1_admin = cls.create_user("admin1@example.com", "admin1", cls.tenant1, UserRole.ADMIN.value)
        cls.tenant1_manager = cls.create_user("manager1@example.com", "manager1", cls.tenant1, UserRole.MANAGER.value)
        cls.tenant2_user2 = cls.create_user("user2@example.com", "user2", cls.tenant2, UserRole.USER.value)
        
        # テスト用のチームを作成
        cls.team1 = cls.create_team("team1", cls.tenant1)
        cls.team2 = cls.create_team("team2", cls.tenant2)
    
    def test_get_permission_for_undefined_action(self):
        """
        定義されていないアクションでデフォルトの権限が設定されることをテストする。
        """
        view = UserViewSet()
        view.action = 'custom_action'
        permissions = view.get_permissions()

        self.assertEqual(len(permissions), 2)
        self.assertIsInstance(permissions[0], IsAuthenticated)
        self.assertIsInstance(permissions[1], IsTenantUser)



    def test_get_permission_for_admin_or_manager_actions(self):
        """
        管理者またはマネージャー権限のパーミッションが設定されることをテストする。
        """
        view = UserViewSet()
        actions = ['create', 'destroy']
        
        for action in actions:
            view.action = action
            permissions = view.get_permissions()
            
            self.assertEqual(len(permissions), 2)
            self.assertIsInstance(permissions[0], IsAuthenticated)
            self.assertIsInstance(permissions[1], IsAdminOrManager)




    def test_get_permission_for_update_actions(self):
        """
        定義されていないアクションでデフォルトの権限が設定されることをテストする。
        """
        view = UserViewSet()
        actions = ['update', 'partial_update']
        
        for action in actions:
            view.action = action
            permissions = view.get_permissions()
            
            self.assertEqual(len(permissions), 2)
            self.assertIsInstance(permissions[0], IsAuthenticated)
            self.assertIsInstance(permissions[1], IsOwnerOrAdmin)


    def test_get_queryset_returns_user_for_current_tenant(self):
        """
        get_querysetメソッドが現在のテナントに属するユーザーのみを返すことをテストする。
        """
        request = RequestFactory().get('/')
        request.user = self.tenant1_user1

        view = UserViewSet()
        view.request = request

        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 3)  # user1, admin1, manager1
        user_names = [user.name for user in queryset]
        self.assertIn('user1', user_names)
        self.assertIn('admin1', user_names)
        self.assertIn('manager1', user_names)


    def test_perform_create_sets_tenant(self):
        """
        perform_createメソッドでユーザーのテナントが自動的に設定されることをテストする。
        """
        # モックリクエストを作成（管理者ユーザーを使用）
        factory = RequestFactory()
        request = factory.post('/users/')
        request.user = self.tenant1_admin

        # ロール指定なしのデータ（can_create_user_with_roleはスキップされる）
        data = {}
        request.data = data

        # UserViewSetインスタンスを作成
        view = UserViewSet()
        view.request = request

        # 必須フィールドを含む有効なデータでシリアライザーを作成
        serializer = UserSerializer(data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'testpassword123',
            'teams': [self.team1.id]  # 既存チームのIDを指定
        })
        
        # バリデーションを実行
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")

        # perform_createを呼び出し
        view.perform_create(serializer)

        # 正しいテナントでユーザーが作成されたことを確認
        created_user = serializer.instance
        self.assertEqual(created_user.tenant, self.tenant1)





    def test_can_change_role_user_to_manager_fails(self):
        """
        一般ユーザーがマネージャーロールに変更できないことをテストする。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_user1, UserRole.MANAGER.value)
        
        self.assertFalse(can_change)
        self.assertEqual(error_msg, "自分より上位のロールに設定することはできません。")

    def test_can_change_role_user_to_admin_fails(self):
        """
        一般ユーザーが管理者ロールに変更できないことをテストする。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_user1, UserRole.ADMIN.value)
        
        self.assertFalse(can_change)
        self.assertEqual(error_msg, "自分より上位のロールに設定することはできません。")

    def test_can_change_role_manager_to_admin_fails(self):
        """
        マネージャーが管理者ロールに変更できないことをテストする。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_manager, UserRole.ADMIN.value)
        
        self.assertFalse(can_change)
        self.assertEqual(error_msg, "自分より上位のロールに設定することはできません。")

    def test_can_change_role_admin_to_manager(self):
        """
        管理者がマネージャーロールに変更できることをテストする。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_admin, UserRole.MANAGER.value)
        
        self.assertTrue(can_change)
        self.assertIsNone(error_msg)

    def test_can_change_role_admin_to_user(self):
        """
        管理者が一般ユーザーロールに変更できることをテストする。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_admin, UserRole.USER.value)
        
        self.assertTrue(can_change)
        self.assertIsNone(error_msg)

    def test_can_change_role_to_superuser_fails(self):
        """
        どのロールからもSUPERUSERロールに変更できないことをテストする。
        """
        view = UserViewSet()
        
        # 一般ユーザーから（上位ロールのメッセージが先に返される）
        can_change, error_msg = view.can_change_role(self.tenant1_user1, UserRole.SUPERUSER.value)
        self.assertFalse(can_change)
        self.assertEqual(error_msg, "自分より上位のロールに設定することはできません。")
        
        # 管理者から（上位ロールのメッセージが先に返される）
        can_change, error_msg = view.can_change_role(self.tenant1_admin, UserRole.SUPERUSER.value)
        self.assertFalse(can_change)
        self.assertEqual(error_msg, "自分より上位のロールに設定することはできません。")

    def test_can_change_role_same_level(self):
        """
        同じレベルのロールに変更できることをテストする。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_user1, UserRole.USER.value)
        
        self.assertTrue(can_change)
        self.assertIsNone(error_msg)

    def test_can_change_role_manager_to_user(self):
        """
        マネージャーが一般ユーザーロールに変更できることをテストする（下位ロールのため）。
        """
        view = UserViewSet()
        can_change, error_msg = view.can_change_role(self.tenant1_manager, UserRole.USER.value)
        
        self.assertTrue(can_change)
        self.assertIsNone(error_msg)

    def test_can_change_role_superuser_specific_check(self):
        """
        SUPERUSERロール専用のチェックをテストする。
        """
        # SUPERUSERユーザーを作成
        superuser = self.create_user("super@example.com", "superuser", self.tenant1, UserRole.SUPERUSER.value)
        
        view = UserViewSet()
        
        # SUPERUSERが他のロールを設定しようとする場合（有効なケース）
        can_change, error_msg = view.can_change_role(superuser, UserRole.ADMIN.value)
        self.assertTrue(can_change)
        self.assertIsNone(error_msg)
        
        # SUPERUSERがSUPERUSERロールを設定しようとする場合（無効）
        can_change, error_msg = view.can_change_role(superuser, UserRole.SUPERUSER.value)
        self.assertFalse(can_change)
        self.assertEqual(error_msg, "スーパーユーザーロールは設定できません。")

    def test_can_create_user_with_role_user_creates_user_fails(self):
        """
        一般ユーザーが一般ユーザーを作成できないことをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_user1, UserRole.USER.value)
        
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "一般ユーザーはユーザーを作成する権限がありません。")

    def test_can_create_user_with_role_user_creates_manager_fails(self):
        """
        一般ユーザーがマネージャーを作成できないことをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_user1, UserRole.MANAGER.value)
        
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "一般ユーザーはユーザーを作成する権限がありません。")

    def test_can_create_user_with_role_manager_creates_user(self):
        """
        マネージャーが一般ユーザーを作成できることをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_manager, UserRole.USER.value)
        
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)

    def test_can_create_user_with_role_manager_creates_manager(self):
        """
        マネージャーがマネージャーを作成できることをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_manager, UserRole.MANAGER.value)
        
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)

    def test_can_create_user_with_role_admin_creates_user(self):
        """
        管理者が一般ユーザーを作成できることをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_admin, UserRole.USER.value)
        
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)

    def test_can_create_user_with_role_admin_creates_manager(self):
        """
        管理者がマネージャーを作成できることをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_admin, UserRole.MANAGER.value)
        
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)

    def test_can_create_user_with_role_admin_creates_admin(self):
        """
        管理者が管理者を作成できることをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_admin, UserRole.ADMIN.value)
        
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)

    def test_can_create_user_with_role_superuser_fails(self):
        """
        SUPERUSERロール作成がすべてのロールから拒否されることをテストする。
        """
        view = UserViewSet()
        superuser = self.create_user("super@example.com", "superuser", self.tenant1, UserRole.SUPERUSER.value)
        
        # 一般ユーザーから（先に一般ユーザー権限チェックで弾かれる）
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_user1, UserRole.SUPERUSER.value)
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "一般ユーザーはユーザーを作成する権限がありません。")
        
        # マネージャーから
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_manager, UserRole.SUPERUSER.value)
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "スーパーユーザーで作成する権限がありません。")
        
        # 管理者から
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_admin, UserRole.SUPERUSER.value)
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "スーパーユーザーで作成する権限がありません。")
        
        # SUPERUSERから
        can_create, error_msg = view.can_create_user_with_role(superuser, UserRole.SUPERUSER.value)
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "スーパーユーザーで作成する権限がありません。")


    def test_can_create_user_with_role_user_creates_admin_fails(self):
        """
        一般ユーザーが管理者を作成できないことをテストする（一般ユーザー権限で先に弾かれる）。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_user1, UserRole.ADMIN.value)
        
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "一般ユーザーはユーザーを作成する権限がありません。")

    def test_can_create_user_with_role_manager_creates_admin_fails(self):
        """
        マネージャーが管理者を作成できないことをテストする。
        """
        view = UserViewSet()
        can_create, error_msg = view.can_create_user_with_role(self.tenant1_manager, UserRole.ADMIN.value)
        
        self.assertFalse(can_create)
        self.assertEqual(error_msg, "管理者権限が必要です。")

    def test_can_create_user_with_role_superuser_creates_others(self):
        """
        SUPERUSERが他のロールを作成できることをテストする。
        """
        view = UserViewSet()
        superuser = self.create_user("super@example.com", "superuser", self.tenant1, UserRole.SUPERUSER.value)
        
        # SUPERUSER -> 一般ユーザー
        can_create, error_msg = view.can_create_user_with_role(superuser, UserRole.USER.value)
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)
        
        # SUPERUSER -> マネージャー
        can_create, error_msg = view.can_create_user_with_role(superuser, UserRole.MANAGER.value)
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)

        # SUPERUSER -> ADMIN
        can_create, error_msg = view.can_create_user_with_role(superuser, UserRole.ADMIN.value)
        self.assertTrue(can_create)
        self.assertIsNone(error_msg)