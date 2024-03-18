from enum import Enum


class Role(str, Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    ACCOUNTANT = 'accountant'
    DEV = 'dev'
    LEAD = 'lead'
    QA = 'qa'


ROLE_CHOICES = (
    (Role.ADMIN.value, Role.ADMIN.value),
    (Role.MANAGER.value, Role.MANAGER.value),
    (Role.ACCOUNTANT.value, Role.ACCOUNTANT.value),
    (Role.DEV.value, Role.DEV.value),
    (Role.LEAD.value, Role.LEAD.value),
    (Role.QA.value, Role.QA.value),
)


class TaskStatus(str, Enum):
    OPENED = 'opened'
    CLOSED = 'closed'


STATUS_CHOICES = (
    (TaskStatus.CLOSED.value, TaskStatus.CLOSED.value),
    (TaskStatus.OPENED.value, TaskStatus.OPENED.value),
)


class UserTransactionReason(str, Enum):
    ASSIGN = 'assign'
    CLOSURE = 'closure'
    DAILY_PAYOUT = 'daily_payout'


USER_TRANSACTION_CHOICES = (
    (UserTransactionReason.ASSIGN.value, UserTransactionReason.ASSIGN.value),
    (UserTransactionReason.CLOSURE.value, UserTransactionReason.CLOSURE.value),
    (UserTransactionReason.DAILY_PAYOUT.value, UserTransactionReason.DAILY_PAYOUT.value)
)


class BillingCycleStatus(str, Enum):
    OPENED = 'opened'
    CLOSED = 'closed'


BILLING_CYCLE_CHOICES = (
    (BillingCycleStatus.CLOSED.value, BillingCycleStatus.CLOSED.value),
    (BillingCycleStatus.OPENED.value, BillingCycleStatus.OPENED.value)
)