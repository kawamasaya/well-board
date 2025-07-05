from django.db import models
from django.utils import timezone


class TenantRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class TenantRequest(models.Model):
    tenant_name = models.CharField(max_length=100)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=TenantRequestStatus.choices,
        default=TenantRequestStatus.PENDING,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'tenant_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"({self.id}){self.tenant_name}"