from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from backend.models import Team, Tenant
from backend.models.user import UserRole


class TestTeamAPI(TestCase):
    """
    Team API の権限チェックをテストするクラス
    実際のHTTPリクエストを通じて権限の動作を検証する
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        
        # テスト用のテナントを作成
        cls.tenant1 = Tenant.objects.create(name="Test Tenant 1")
        cls.tenant2 = Tenant.objects.create(name="Test Tenant 2")
        
        # 各ロールのユーザーを作成（テナント1）
        cls.superuser = User.objects.create_user(
            email="superuser@test.com",
            password="testpass123",
            name="Super User",
            role=UserRole.SUPERUSER.value,
            tenant=cls.tenant1
        )
        
        cls.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            name="Admin User",
            role=UserRole.ADMIN.value,
            tenant=cls.tenant1
        )
        
        cls.manager = User.objects.create_user(
            email="manager@test.com",
            password="testpass123",
            name="Manager User",
            role=UserRole.MANAGER.value,
            tenant=cls.tenant1
        )
        
        cls.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            name="Regular User",
            role=UserRole.USER.value,
            tenant=cls.tenant1
        )
        
        # テナント2のユーザー
        cls.tenant2_user = User.objects.create_user(
            email="tenant2@test.com",
            password="testpass123",
            name="Tenant2 User",
            role=UserRole.ADMIN.value,
            tenant=cls.tenant2
        )
        
        # テナントなしユーザーは作成できない（NOT NULL制約のため）
        # 代わりに削除予定のテナントに所属するユーザーを想定
        cls.temp_tenant = Tenant.objects.create(name="Temp Tenant")
        cls.orphaned_user = User.objects.create_user(
            email="orphaned@test.com",
            password="testpass123",
            name="Orphaned User",
            role=UserRole.USER.value,
            tenant=cls.temp_tenant
        )
        
        # テスト用のチームを作成
        cls.team1 = Team.objects.create(
            name="Team 1",
            tenant=cls.tenant1
        )
        cls.team2 = Team.objects.create(
            name="Team 2",  
            tenant=cls.tenant2
        )
    
    def setUp(self):
        self.client = APIClient()
        # ネストしたURLパターンを使用
        self.teams_url = reverse('teams-list', kwargs={'tenants_pk': self.tenant1.pk})
        self.tenant2_teams_url = reverse('teams-list', kwargs={'tenants_pk': self.tenant2.pk})
        
    def _authenticate_user(self, user):
        """ユーザーでログイン"""
        self.client.force_authenticate(user=user)
        
    def test_list_teams_with_superuser(self):
        """SUPERUSERでのチーム一覧取得テスト"""
        self._authenticate_user(self.superuser)
        response = self.client.get(self.teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # tenant1のチームのみ
        self.assertEqual(response.data[0]['name'], 'Team 1')
        
    def test_list_teams_with_admin(self):
        """ADMINでのチーム一覧取得テスト"""
        self._authenticate_user(self.admin)
        response = self.client.get(self.teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_list_teams_with_manager(self):
        """MANAGERでのチーム一覧取得テスト"""
        self._authenticate_user(self.manager)
        response = self.client.get(self.teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_list_teams_with_regular_user(self):
        """一般USERでのチーム一覧取得テスト"""
        self._authenticate_user(self.user)
        response = self.client.get(self.teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_list_teams_with_different_tenant_user(self):
        """異なるテナントのユーザーでのチーム一覧取得テスト"""
        self._authenticate_user(self.tenant2_user)
        # tenant2のユーザーは自分のテナントのURLでアクセス
        response = self.client.get(self.tenant2_teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # tenant2のチームのみ
        self.assertEqual(response.data[0]['name'], 'Team 2')
        
    def test_list_teams_with_orphaned_user(self):
        """孤立したテナントのユーザーでのチーム一覧取得テスト"""
        self._authenticate_user(self.orphaned_user)
        # 孤立したユーザーは自分のテナントのURLでアクセス
        orphaned_teams_url = reverse('teams-list', kwargs={'tenants_pk': self.temp_tenant.pk})
        response = self.client.get(orphaned_teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # そのテナントにはチームがないので空
        
    def test_create_team_with_superuser(self):
        """SUPERUSERでのチーム作成テスト"""
        self._authenticate_user(self.superuser)
        data = {'name': 'New Team'}
        response = self.client.post(self.teams_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Team')
        
    def test_create_team_with_admin(self):
        """ADMINでのチーム作成テスト"""
        self._authenticate_user(self.admin)
        data = {'name': 'Admin Team'}
        response = self.client.post(self.teams_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Admin Team')
        
    def test_create_team_with_manager(self):
        """MANAGERでのチーム作成テスト"""
        self._authenticate_user(self.manager)
        data = {'name': 'Manager Team'}
        response = self.client.post(self.teams_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Manager Team')
        
    def test_create_team_with_regular_user_forbidden(self):
        """一般USERでのチーム作成テスト（権限なし）"""
        self._authenticate_user(self.user)
        data = {'name': 'User Team'}
        response = self.client.post(self.teams_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_team_with_orphaned_user(self):
        """孤立したテナントのユーザーでのチーム作成テスト"""
        self._authenticate_user(self.orphaned_user)
        # 孤立したユーザーは自分のテナントのURLでアクセス
        orphaned_teams_url = reverse('teams-list', kwargs={'tenants_pk': self.temp_tenant.pk})
        data = {'name': 'Orphaned Team'}
        response = self.client.post(orphaned_teams_url, data)
        
        # 一般ユーザーなので権限なし
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_retrieve_team_with_authorized_user(self):
        """認証済みユーザーでのチーム詳細取得テスト"""
        self._authenticate_user(self.user)
        team_url = reverse('teams-detail', kwargs={'tenants_pk': self.tenant1.pk, 'pk': self.team1.pk})
        response = self.client.get(team_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Team 1')
        
    def test_retrieve_team_with_different_tenant_user(self):
        """異なるテナントユーザーでのチーム詳細取得テスト"""
        self._authenticate_user(self.tenant2_user)
        # tenant2のユーザーがtenant1のチームにアクセス（権限なし）
        team_url = reverse('teams-detail', kwargs={'tenants_pk': self.tenant1.pk, 'pk': self.team1.pk})
        response = self.client.get(team_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_cross_tenant_access_forbidden(self):
        """異なるテナントのユーザーが別のテナントのURL経由でアクセスするテスト"""
        self._authenticate_user(self.tenant2_user)
        # tenant2のユーザーがtenant1のURLでチーム一覧にアクセス（権限なし）
        response = self.client.get(self.teams_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_team_with_admin(self):
        """ADMINでのチーム更新テスト"""
        self._authenticate_user(self.admin)
        team_url = reverse('teams-detail', kwargs={'tenants_pk': self.tenant1.pk, 'pk': self.team1.pk})
        data = {'name': 'Updated Team'}
        response = self.client.patch(team_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Team')
        
    def test_update_team_with_regular_user_forbidden(self):
        """一般USERでのチーム更新テスト（権限なし）"""
        self._authenticate_user(self.user)
        team_url = reverse('teams-detail', kwargs={'tenants_pk': self.tenant1.pk, 'pk': self.team1.pk})
        data = {'name': 'User Updated Team'}
        response = self.client.patch(team_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_team_with_admin(self):
        """ADMINでのチーム削除テスト"""
        # 削除用のチームを作成
        test_team = Team.objects.create(name="Delete Me", tenant=self.tenant1)
        
        self._authenticate_user(self.admin)
        team_url = reverse('teams-detail', kwargs={'tenants_pk': self.tenant1.pk, 'pk': test_team.pk})
        response = self.client.delete(team_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(pk=test_team.pk).exists())
        
    def test_delete_team_with_regular_user_forbidden(self):
        """一般USERでのチーム削除テスト（権限なし）"""
        # 削除用のチームを作成
        test_team = Team.objects.create(name="Cannot Delete", tenant=self.tenant1)
        
        self._authenticate_user(self.user)
        team_url = reverse('teams-detail', kwargs={'tenants_pk': self.tenant1.pk, 'pk': test_team.pk})
        response = self.client.delete(team_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Team.objects.filter(pk=test_team.pk).exists())
        
    def test_unauthenticated_access_forbidden(self):
        """未認証でのアクセステスト"""
        response = self.client.get(self.teams_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_unauthenticated_create_forbidden(self):
        """未認証でのチーム作成テスト"""
        data = {'name': 'Unauthorized Team'}
        response = self.client.post(self.teams_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)