from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APITestCase

from backend.models import Team, Tenant
from backend.permissions import IsAdminOrManager, IsTenantUser
from backend.serializers.team_serializer import TeamSerializer
from backend.views.team_view import TeamViewSet


class TestTeamView(APITestCase):
        
    @staticmethod
    def create_tenant(name):
        """テナントを作成するヘルパーメソッド"""
        return Tenant.objects.create(name=name)
    
    @staticmethod
    def create_user(email, name, tenant):
        """ユーザーを作成するヘルパーメソッド"""
        User = get_user_model()
        return User.objects.create_user(email=email, password="12345", name=name, tenant=tenant)
    
    
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
        
        # テスト用のユーザーを作成
        cls.tenant1_user1 = cls.create_user("user1@example.com", "user1", cls.tenant1)
        cls.tenant2_user2 = cls.create_user("user2@example.com", "user2", cls.tenant2)
        
        # テスト用のチームを作成
        cls.team1 = cls.create_team("team1", cls.tenant1)
        cls.team2 = cls.create_team("team2", cls.tenant2)

    
    def test_get_permissions_for_admin_actions(self):
        """
        管理者権限のパーミッションが設定されることをテストする。
        """
        view = TeamViewSet()
        admin_actions = ['create', 'update', 'partial_update', 'destroy']
        
        for action in admin_actions:
            view.action = action
            permissions = view.get_permissions()
            
            # 認証権限＋管理者権限の確認
            self.assertEqual(len(permissions), 2)
            self.assertIsInstance(permissions[0], IsAuthenticated)
            self.assertIsInstance(permissions[1], IsAdminOrManager)

    def test_get_permissions_for_user_actions(self):
        """
        一般ユーザー権限のパーミッションが設定されることをテストする。
        """
        view = TeamViewSet()
        user_actions = ['list', 'retrieve']
        
        for action in user_actions:
            view.action = action
            permissions = view.get_permissions()
            
            # 認証権限＋一般ユーザー権限の確認
            self.assertEqual(len(permissions), 2)
            self.assertIsInstance(permissions[0], IsAuthenticated)
            self.assertIsInstance(permissions[1], IsTenantUser)

    def test_get_permissions_for_undefined_action(self):
        """
        定義されていないアクションでデフォルトの権限が設定されることをテストする。
        """
        view = TeamViewSet()
        view.action = 'custom_action'
        permissions = view.get_permissions()
        
        # デフォルト権限の確認
        self.assertEqual(len(permissions), 2)
        self.assertIsInstance(permissions[0], IsAuthenticated)
        self.assertIsInstance(permissions[1], IsTenantUser)
        
    def test_get_queryset_returns_teams_for_current_tenant(self):
        """
        get_querysetメソッドが現在のテナントに属するチームのみを返すことをテストする。
        """
        # リクエストを設定
        request = RequestFactory().get('/')
        request.user = self.tenant1_user1

        # ビューを作成してリクエストを設定
        view = TeamViewSet()
        view.request = request

        # テスト対象のメソッドを呼び出し
        queryset = view.get_queryset()

        # 現在のテナントのチームのみが返されることを確認
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().name, 'team1')

    def test_perform_create_sets_tenant(self):
        """
        perform_createメソッドでユーザーのテナントが自動的に設定されることをテストする。
        """
        # モックリクエストを作成
        factory = RequestFactory()
        request = factory.post('/teams/')
        request.user = self.tenant1_user1

        # TeamViewSetインスタンスを作成
        view = TeamViewSet()
        view.request = request

        # モックシリアライザーを作成
        serializer = TeamSerializer(data={'name': 'team'})
        serializer.is_valid()

        # perform_createを呼び出し
        view.perform_create(serializer)

        # 正しいテナントでチームが作成されたことを確認
        created_team = serializer.instance
        assert created_team.tenant == self.tenant1
