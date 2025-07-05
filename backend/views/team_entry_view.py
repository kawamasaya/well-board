from collections import defaultdict
from datetime import datetime, timedelta

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from backend.models import Entry
from backend.models.user import UserRole
from backend.permissions import IsTeamManagerOrSelf


@extend_schema(
    tags=["team-entry"])

class TeamEntryViewSet(ViewSet):
    """
    チーム別エントリー集約表示API ViewSet
    
    チーム・ユーザー別に時系列のモチベーション・ストレスデータを
    効率的に集約して返すカスタムAPI。ダッシュボード表示用。
    
    Permissions:
        - SUPERUSER/ADMIN: 全チームデータアクセス
        - MANAGER: 管理チームのデータのみ
        - USER: 自分のデータのみ
        
    Features:
        - 複数チームの同時データ取得
        - ユーザー別時系列データの構造化
        - メモリ効率的なデータ集約処理
    """
    permission_classes = [IsAuthenticated, IsTeamManagerOrSelf]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='team_ids',
                type={'type': 'array', 'items': {'type': 'number'}},
                location=OpenApiParameter.QUERY,
                description='カンマ区切りのチームIDリスト',
                required=True
            ),
        ]
    )
    def list(self, request, tenants_pk):
        """
        チーム別のエントリーデータを集約して返すAPI
        
        権限に基づいてエントリーをフィルタリングし、チーム・ユーザー別に
        時系列のストレス度・モチベーション度データを構造化して返す。
        
        Args:
            request: HTTPリクエストオブジェクト
            tenants_pk (int): テナント（組織）ID
            
        Returns:
            Response: 以下の形式のJSONレスポンス
                [
                    {
                        "id": int,  # チームID
                        "name": str,  # チーム名
                        "users": [
                            {
                                "id": int,  # ユーザーID
                                "name": str,  # ユーザー名
                                "entries": {
                                    "labels": ["MM/DD", ...],  # 日付ラベル
                                    "stress_values": [int, ...],  # ストレス度値
                                    "motivation_values": [int, ...]  # モチベーション度値
                                }
                            }
                        ]
                    }
                ]
                
        Permission Logic:
            - SUPERUSER/ADMIN: 全エントリーアクセス可能
            - MANAGER: 管理するチームのエントリーのみ
            - USER: 自分のエントリーのみ
        """
        user = request.user
        
        # 3ヶ月前の日付を計算
        three_months_ago = datetime.now().date() - timedelta(days=90)
        
        # 権限に基づいてエントリーをフィルタリング
        if user.role in [UserRole.SUPERUSER.value, UserRole.ADMIN.value]:
            # スーパーユーザーと管理者は全てのエントリーにアクセス可能
            entries = Entry.objects.filter(
                tenant_id=tenants_pk,
                reported_at__gte=three_months_ago
            )
        elif user.role == UserRole.MANAGER.value:
            # マネージャーは管理するチームのエントリーにアクセス可能
            managed_team_ids = user.managed_teams.values_list('id', flat=True)
            entries = Entry.objects.filter(
                tenant_id=tenants_pk,
                team_id__in=managed_team_ids,
                reported_at__gte=three_months_ago
            )
        else:
            # 一般ユーザーは自分のエントリーのみアクセス可能
            entries = Entry.objects.filter(
                tenant_id=tenants_pk,
                user=user,
                reported_at__gte=three_months_ago
            )
        
        entries = entries.select_related(
            'team',  # 同じクエリでチームデータを取得
            'user'   # 同じクエリでユーザーデータを取得
        ).order_by('team_id', 'user_id', 'reported_at')
        
        # ネストされた構造を構築
        teams_data = {}
        users_data = defaultdict(lambda: {
            "labels": [],
            "stress_values": [],
            "motivation_values": []
        })
        
        for entry in entries:
            team = entry.team
            user = entry.user
            
            if team.id not in teams_data:
                teams_data[team.id] = {
                    "id": team.id,
                    "name": team.name,
                    "users": []
                }
            
            # ユーザーデータに日付と両方のスコアを追加
            users_data[(team.id, user.id)]["labels"].append(
                entry.reported_at.strftime("%m/%d")
            )
            users_data[(team.id, user.id)]["stress_values"].append(
                entry.stress_score or 0
            )
            users_data[(team.id, user.id)]["motivation_values"].append(
                entry.motivation_score or 0
            )
        
        # チームとユーザーデータを結合
        for (team_id, user_id), data in users_data.items():
            user = next(e.user for e in entries 
                      if e.team.id == team_id and e.user.id == user_id)
            
            teams_data[team_id]["users"].append({
                "id": user.id,
                "name": user.name,
                "entries": {
                    "labels": data["labels"],
                    "stress_values": data["stress_values"],
                    "motivation_values": data["motivation_values"]
                }
            })
        
        # チームIDで順序付けしたリストに変換
        response_data = sorted(teams_data.values(), key=lambda x: x['id'])
            
        return Response(response_data)