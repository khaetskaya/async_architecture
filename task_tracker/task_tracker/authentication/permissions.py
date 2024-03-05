from rest_framework import request
from django.views.generic import View
from rest_framework.permissions import BasePermission
from tasks.defs import Role


class ReassignTasksPermission(BasePermission):
    def has_permission(self, request: request.Request, view: View) -> bool:
        user = request.user
        if user.role in [Role.ADMIN.value, Role.MANAGER.value]:
            return True
        return False
