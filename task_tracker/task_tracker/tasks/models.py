from django.contrib.auth.models import AbstractUser
from django.db import models
from tasks.defs import ROLE_CHOICES, Role, STATUS_CHOICES, TaskStatus
import uuid


class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES, max_length=128, default=Role.DEV.value)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4)


class Task(models.Model):
    assignee = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(choices=STATUS_CHOICES, max_length=64, default=TaskStatus.OPENED.value)
    description = models.CharField(max_length=1028)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4)
    jira_id = models.CharField(max_length=128, null=True, blank=True)
