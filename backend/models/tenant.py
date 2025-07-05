from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    domain_settings = models.JSONField(default=dict)


    def __str__(self):
        return f"({self.id}){self.name}"
    
    class Meta:
        db_table = 'tenant'