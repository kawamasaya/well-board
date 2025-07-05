from django.db import models

from .tenant import Tenant


class Team(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    questions = models.JSONField(blank=True, null=True)
    managers = models.ManyToManyField(
        'User', 
        blank=True, 
        related_name='managed_teams',
        limit_choices_to={'role__in': [2, 3]}  # ADMIN=2, MANAGER=3のみ選択可能
    )

    def __str__(self):
        return f"({self.id}){self.name}"
    
    class Meta:
        db_table = 'team'
        indexes = [
            models.Index(fields=['tenant'], name='team_tenant_idx'),
        ]