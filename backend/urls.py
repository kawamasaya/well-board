# from django.urls import path

# from backend.views import HelloWorldView, hello_world

from django.urls import re_path
from rest_framework_nested import routers

from backend.views import (
    entry_view,
    team_entry_view,
    team_view,
    tenant_view,
    user_view,
    views,
)

router = routers.DefaultRouter()
router.register('tenants', tenant_view.TenantViewSet, basename='tenants')

# テナント配下のリソース
tenant_router = routers.NestedSimpleRouter(router, 'tenants', lookup='tenants')
tenant_router.register('teams', team_view.TeamViewSet, basename='teams') #/tenants/1/teams チーム設定
tenant_router.register('users', user_view.UserViewSet, basename='users') #/tenants/1/users ユーザー設定
tenant_router.register('entries', entry_view.EntryViewSet, basename='entries') #/tenants/1/entries 個人のウェルネス記録登録
tenant_router.register('team-entries', team_entry_view.TeamEntryViewSet, basename='team-entries') #/tenants/1/team-entries チームのウェルネス記録確認

# チーム配下のリソース
team_router = routers.NestedSimpleRouter(tenant_router, 'teams', lookup='team')

urlpatterns = [
    re_path('^.*$', views.HomePageView.as_view(), name='home'),
]
