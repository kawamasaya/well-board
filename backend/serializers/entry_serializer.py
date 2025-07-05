from rest_framework import serializers

from backend.models import Entry


class EntrySerializer(serializers.ModelSerializer):
    reported_at = serializers.DateField(input_formats=['%Y-%m-%d'], write_only=True)
    
    class Meta:
        model = Entry
        fields = '__all__'
        read_only_fields = ('tenant', 'user', 'stress_score', 'motivation_score')
    
class EntryDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.name
        }
    
    def get_team(self, obj):
        return {
            'id': obj.team.id,
            'name': obj.team.name
        }
    
    class Meta:
        model = Entry
        fields = '__all__'
        read_only_fields = ('tenant', 'user', 'stress_score', 'motivation_score')