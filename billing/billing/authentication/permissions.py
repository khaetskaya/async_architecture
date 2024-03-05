from rest_framework import request
from django.views.generic import View
from rest_framework.permissions import BasePermission
from billing.defs import Role


class StatsPermission(BasePermission):
    def has_permission(self, request: request.Request, view: View) -> bool:
        user = request.user
        if user.role in [Role.ADMIN.value, Role.ACCOUNTANT.value]:
            return True
        return False
