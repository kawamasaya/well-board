from rest_framework import serializers

from backend.models import User, Tenant, TenantRequest


class TenantRequestSerializer(serializers.Serializer):
    tenantName = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)
    domain = serializers.CharField(max_length=100)

    def validate_email(self, value):
        """メールアドレスの重複チェック"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスは既に使用されています。")
        if TenantRequest.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスで既にリクエスト済みです。")
        return value

    def validate_tenantName(self, value):
        """テナント名の重複チェック"""
        if Tenant.objects.filter(name=value).exists():
            raise serializers.ValidationError("この組織名は既に使用されています。")
        if TenantRequest.objects.filter(tenant_name=value).exists():
            raise serializers.ValidationError("この組織名で既にリクエスト済みです。")
        return value

    def create(self, validated_data):
        """テナントリクエストを作成"""
        request = TenantRequest.objects.create(
            tenant_name=validated_data['tenantName'],
            email=validated_data['email'],
            name=validated_data['name'],
            domain=validated_data['domain']
        )
        return request