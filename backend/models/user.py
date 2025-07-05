from enum import Enum

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from .team import Team
from .tenant import Tenant


class UserRole(Enum):
    SUPERUSER=1
    ADMIN=2
    MANAGER=3
    USER=4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
    
class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def create_user(self,email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPERUSER.value)

        if not extra_fields.get('tenant_id'):
            from backend.models import Tenant
            tenant = Tenant.objects.first() or Tenant.objects.create(name='Default Tenant')
            extra_fields['tenant_id'] = tenant.id

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
        
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.IntegerField(choices=UserRole.choices(), default=UserRole.USER.value)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team, related_name='members')

    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "user"
        indexes = [
            models.Index(fields=['tenant'], name='user_tenant_idx'),
        ]

    def __str__(self):        
        return f"({self.id}){self.name}"