from django.contrib.auth.models import AbstractUser
from django.db import models
from analytics.defs import ROLE_CHOICES, STATUS_CHOICES, USER_TRANSACTION_CHOICES, BILLING_CYCLE_CHOICES
import uuid


class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES, max_length=128)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4)
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    assignee = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4)
    status = models.CharField(choices=STATUS_CHOICES, max_length=64)
    description = models.CharField(max_length=1028)
    assign_price = models.IntegerField()
    closure_price = models.IntegerField()
    jira_id = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class BillingCycle(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=64, choices=BILLING_CYCLE_CHOICES)
    public_id = models.UUIDField(unique=True, null=True, blank=True)


class UserTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    debit = models.IntegerField()
    credit = models.IntegerField()
    task = models.ForeignKey(Task, on_delete=models.PROTECT, null=True, blank=True)
    reason = models.CharField(max_length=64, choices=USER_TRANSACTION_CHOICES)
    description = models.CharField(max_length=1028)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4)
    billing_cycle = models.ForeignKey(BillingCycle, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
