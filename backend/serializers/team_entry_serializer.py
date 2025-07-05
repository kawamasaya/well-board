from rest_framework import serializers

from backend.serializers.entry_serializer import EntrySerializer


class UserEntryDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.IntegerField())

class UserEntrySerializer(serializers.Serializer):
    user = serializers.IntegerField()
    name = serializers.CharField()
    graph_data = UserEntryDataSerializer()

class TeamWithEntriesSerializer(serializers.Serializer):
    team = serializers.IntegerField(source='id')
    name = serializers.CharField()
    entries = EntrySerializer(many=True)


