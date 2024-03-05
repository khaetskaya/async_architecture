from rest_framework import request
from django.views.generic import View
from rest_framework.permissions import BasePermission
from analytics.defs import Role


class AdminPermission(BasePermission):
    def has_permission(self, request: request.Request, view: View) -> bool:
        user = request.user
        if user.role == Role.ADMIN.value:
            return True
        return False
