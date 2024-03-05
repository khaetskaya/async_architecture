import ujson
from django.http import HttpResponse
from oauth2_provider.views.generic import ProtectedResourceView
from rest_framework import viewsets

from users.kafka_producer import producer

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        result = super().create(request, *args, **kwargs)
        data = result.data
        event = {
            "event_name": "AccountCreated",
            "data": {
                "public_id": data.get("public_id"),
                "email": data.get("email"),
                "role": data.get("role"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "username": data.get("username"),
            },
        }
        producer.send("accounts-stream", event)

        return result

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        new_role = request.data.get("role")
        old_role = user.role
        result = super().update(request, *args, **kwargs)
        data = result.data
        if new_role != old_role:
            event = {
                "event_name": "AccountRoleChanged",
                "data": {
                    "public_id": str(user.public_id),
                    "role": new_role,
                },
            }
            producer.send("accounts", event)

        event = {
            "event_name": "AccountChanged",
            "data": {
                "public_id": data.get("public_id") or str(user.public_id),
                "first_name": data.get("first_name") or user.first_name,
                "last_name": data.get("last_name") or user.last_name,
            },
        }
        producer.send("accounts-stream", event)
        return result

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        result = super().destroy(request, *args, **kwargs)
        data = result.data
        event = {
            "event_name": "AccountDeactivated",
            "data": {
                "public_id": user.public_id,
            },
        }
        producer.send("accounts-stream", event)
        return result


class CurrentUserInfo(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_info = {
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "public_id": str(user.public_id),
            "is_active": user.is_active,
        }
        return HttpResponse(ujson.dumps(user_info))
