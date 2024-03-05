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
