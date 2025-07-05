from rest_framework import serializers

from backend.models import User


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'role',
            'teams',
            'tenant'
        )
        read_only_fields = ('tenant',)  # テナントを読み取り専用に設定


class UserDetailSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()

    def get_teams(self, obj):
        return [{
            'id': team.id,
            'name': team.name
            } for team in obj.teams.all()]
       
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'role',
            'teams',
            'tenant'
        )
        read_only_fields = ('tenant',)


