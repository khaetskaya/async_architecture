from django.contrib.auth.models import AbstractUser
from django.db import models
from users.defs import ROLE_CHOICES, Role
import uuid


class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES, max_length=128, default=Role.DEV.value)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4())
    email = models.EmailField()
