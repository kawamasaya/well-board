from rest_framework import serializers

from backend.models import Team

from .user_serializer import UserSerializer


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'questions', 'managers', 'tenant')
        read_only_fields = ('tenant',)

class TeamDetailSerializer(serializers.ModelSerializer):
    managers = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ('id', 'name', 'questions', 'managers', 'tenant')
        read_only_fields = ('tenant',)